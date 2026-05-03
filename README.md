# 🌤️ Israel Weather MCP Agent

פרויקט זה מממש שרת MCP (Model Context Protocol) המאפשר למודלי שפה (LLMs) לגלוש באופן אוטונומי לאתר מזג האוויר הישראלי, לחפש עיר ספציפית ולשלוף את התחזית המדויקת שלה בזמן אמת.

## 🎯 מטרת הפרויקט
הפרויקט מדגים שילוב של סוכן AI עם דפדפן (באמצעות Playwright). הסוכן מסוגל:
1. לפתוח דפדפן ולנווט לאתר [Weather2day](https://www.weather2day.co.il/forecast).
2. לאתר את שדה החיפוש ולהקליד את שם העיר המבוקשת.
3. לבחור את העיר מהרשימה הנפתחת.
4. לשאוב את נתוני הטמפרטורה, הלחות, והרוח ישירות מהטקסט שמופיע בעמוד (RAG) ולהציג אותם למשתמש.

## 🛠️ טכנולוגיות
* **Python**
* **FastMCP** - לבניית שרת ה-MCP.
* **Playwright (Async)** - לאוטומציה ושליטה על הדפדפן.
* **Anthropic API (Claude)** - כמודל השפה המפעיל את הכלים.

## 🚀 הוראות הרצה (Installation & Setup)

1. **שכפול הפרויקט:**
   `git clone https://github.com/dvori9359-blip/MCP-with-Playwright.git`
   `cd MCP-with-Playwright`

2. **התקנת תלויות וסביבת עבודה:**
   `uv sync`
   `uv pip install python-dotenv`

3. **התקנת דפדפן Chromium עבור Playwright:**
   `uv run playwright install chromium`

4. **הגדרת מפתח API:**
   צרו קובץ בשם `.env` בתיקיית הפרויקט והוסיפו אליו את מפתח ה-API שלכם מ-Anthropic:
   `ANTHROPIC_API_KEY=sk-ant-api-YOUR_KEY_HERE`

5. **הפעלת הפרויקט:**
   `uv run host.py`

## 💬 דוגמאות לשאילתות
* "מה מזג האוויר בחיפה?"
* "מה התחזית בירושלים להיום?"
* "מה המזג אוויר בבני ברק?"