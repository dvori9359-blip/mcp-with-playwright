import asyncio
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

mcp = FastMCP("WeatherIsrael")

# משתנים לשמירת המצב
browser = None
page = None
playwright_instance = None

@mcp.tool()
async def open_weather_forecast_israel():
    global browser, page, playwright_instance
    try:
        if playwright_instance is None:
            playwright_instance = await async_playwright().start()
        
        # הבדיקה שמונעת קריסה בחיפושים עוקבים
        if browser is not None and not browser.is_connected():
            browser = None
            page = None
            
        if page is not None and page.is_closed():
            page = None

        if browser is None:
            browser = await playwright_instance.chromium.launch(headless=True)
            
        if page is None:
            page = await browser.new_page()
        
        await page.goto("https://www.weather2day.co.il/forecast", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        return "Success: Site opened."
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
async def enter_weather_forecast_city_israel(city_name: str):
    global page
    try:
        if page is None:
            return "Error: Page not initialized."

        # חיפוש חכם וממוקד: תיבת טקסט שהיא גלויה לעין (ולא מוסתרת בקוד) 
        # ויש לה ID שקשור לחיפוש
        search_box = page.locator("input[type='text']:visible, input[type='search']:visible").first
        
        await search_box.wait_for(state="visible", timeout=15000)
        
        # --- טריק ויזואלי --- 
        # צובע את התיבה באדום כדי שנוכל לראות בעיניים ש-Playwright מצא את התיבה הנכונה
        await search_box.evaluate("el => el.style.border = '4px solid red'")
        await asyncio.sleep(1) # השהיה קלה כדי שתספיקי לראות את זה
        
        await search_box.click(click_count=3)
        await search_box.press("Backspace")
        
        # הקלדה איטית
        await search_box.type(city_name, delay=200)
        await asyncio.sleep(2)
        
        await page.keyboard.press("ArrowDown")
        await asyncio.sleep(0.5)
        await page.keyboard.press("Enter")
        
        return f"Success: Typed {city_name} and pressed Enter."
    except Exception as e:
        return f"Error during typing: {str(e)}"

@mcp.tool()
async def select_weather_forecast_city_israel():
    global page
    try:
        # מחכים שהדף החדש ייטען לחלוטין
        await page.wait_for_load_state("networkidle", timeout=15000)
        
        # נוודא שאנחנו באמת בדף של תחזית, ואם לא - נלחץ אנטר שוב
        if "forecast" not in page.url:
             await page.keyboard.press("Enter")
             await asyncio.sleep(4)

        try:
            # נסיון ראשון: חיפוש הסלקטורים המדויקים
            temp_info = await page.evaluate('''() => {
                const temp = document.querySelector('.temp-current, #now-temp, .current-temp')?.innerText;
                return temp ? temp : null;
            }''')
            
            if temp_info:
                return f"Success: The precise temperature is {temp_info}. Report this directly to the user."
            else:
                raise Exception("Selector not found")
                
        except Exception:
            # נסיון שני (פתרון הקסם): שאיבת הטקסט הכללי של העמוד
            # ניקח את הטקסט שמופיע באזור המרכזי של המסך וניתן למודל לפענח אותו לבד
            page_text = await page.evaluate('''() => {
                return document.body.innerText.substring(0, 800).replace(/\\n/g, ' ');
            }''')
            
            return f"Success: Page loaded but specific selector failed. Here is the raw text from the top of the page: '{page_text}'. Extract the current temperature and weather condition from this text and tell the user."
        
    except Exception as e:
        return f"Error during data extraction: {str(e)}"
def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()