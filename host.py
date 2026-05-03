
import asyncio
from contextlib import AsyncExitStack
from typing import Any
import httpx
import os
from anthropic import Anthropic
from client import MCPClient
from dotenv import load_dotenv
load_dotenv()
class ChatHost:
    def __init__(self):
        # 1. הגדרת המפתח והלקוח (מותאם לנטפרי)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic = Anthropic(
            api_key=api_key,
            http_client=httpx.Client(verify=False) 
        )
        # 2. חיבור השרתים (ארה"ב וישראל)
        self.mcp_clients: list[MCPClient] = [
            MCPClient("./weather_USA.py"),
            MCPClient("./weather_Israel.py")
        ]    
        self.tool_clients: dict[str, tuple[MCPClient, str]] = {}
        self.clients_connected = False
        self.exit_stack = AsyncExitStack()
    async def connect_mcp_clients(self):
        """פונקציה לחיבור הלקוחות - חובה שתהיה קיימת"""
        if self.clients_connected:
            return
        for client in self.mcp_clients:
            if client.session is None:
                await client.connect_to_server()
        self.clients_connected = True
    async def get_available_tools(self) -> list[dict[str, Any]]:
        """איסוף הכלים מכל השרתים המחוברים"""
        await self.connect_mcp_clients()
        self.tool_clients = {}
        available_tools: list[dict[str, Any]] = []
        for client in self.mcp_clients:
            try:
                response = await client.session.list_tools()
                for tool in response.tools:
                    exposed_name = f"{client.client_name}__{tool.name}"
                    self.tool_clients[exposed_name] = (client, tool.name)
                    available_tools.append({
                        "name": exposed_name,
                        "description": f"[{client.client_name}] {tool.description}",
                        "input_schema": tool.inputSchema,
                    })
            except Exception as e:
                print(f"Warning: Failed to get tools from {client.client_name}: {str(e)}")
        return available_tools
    async def process_query(self, query: str) -> str:
        messages = [{"role": "user", "content": query}]
        available_tools = await self.get_available_tools()
        final_text = []
        # הנחיית מערכת - נווט את ה-LLM להפעיל את הכלים בסדר הנכון
        system_instruction = (
    "You are a weather assistant. To get weather in Israel, you MUST call these tools in order without stopping: "
    "1. weather_Israel__open_weather_forecast_israel "
    "2. weather_Israel__enter_weather_forecast_city_israel (with city name) "
    "3. weather_Israel__select_weather_forecast_city_israel. "
    "Proceed through all steps until the forecast page is displayed in the browser."
)
        while True:
            try:
                response = self.anthropic.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1000,
                system=system_instruction,
                messages=messages,
                tools=available_tools
            )
                assistant_message_content = []
                tool_results = []
                saw_tool_use = False
                for content in response.content:
                    assistant_message_content.append(content)
                    if content.type == 'text':
                        final_text.append(content.text)
                    elif content.type == 'tool_use':
                        saw_tool_use = True
                        tool_name = content.name
                        client, original_tool_name = self.tool_clients[tool_name]
                        # הפעלת הכלי בדפדפן
                        result = await client.session.call_tool(original_tool_name, content.input)
                        final_text.append(f"\n[מפעיל כלי: {tool_name}]")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content,
                        })

                if not saw_tool_use:
                    break
                messages.append({"role": "assistant", "content": assistant_message_content})
                messages.append({"role": "user", "content": tool_results})
            except Exception as e:
                return f"שגיאה בתקשורת: {str(e)}"
        return "\n".join(final_text)         
    async def chat_loop(self):
        print("\nMCP Host Started!")
        print("את יכולה לשאול על מזג האוויר בישראל או בארה\"ב.")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() in ['quit', 'exit', 'יציאה']:
                    break
                if not query:
                    continue
                response = await self.process_query(query)
                print("\n" + response)
            except Exception as e:
                print(f"\nError: {str(e)}")
    async def cleanup(self):
        for client in reversed(self.mcp_clients):
            await client.cleanup()
        await self.exit_stack.aclose()
async def main():
    host = ChatHost()
    try:
        await host.chat_loop()
    finally:
        await host.cleanup()
if __name__ == "__main__":
    asyncio.run(main())