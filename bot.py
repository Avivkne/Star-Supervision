import logging
import json
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from supabase import create_client, Client
import google.generativeai as genai

# --- מפתחות קבועים (כבר מעודכנים עבורך) ---
TELEGRAM_TOKEN = "8810122605:AAFkA97_VY3KV172CFf-7BleyDhMQgj4yYM"
MY_CHAT_ID = 8251059616 

# --- מפתחות דינמיים (יימשכו מהגדרות השרת של Render) ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# חיבור לשירותים
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

PROMPT_INSTRUCTIONS = """
אתה עוזר משרדי עבור חברת קונסטרוקציות בשם "סטאר מהנדסים". תפקידך הוא לקחת טקסט חופשי שנכתב או תומלל על ידי מהנדס בשטח, ולשלוף ממנו את המידע עבור טופס פיקוח עליון.
עליך להחזיר פלט בפורמט JSON בלבד, ללא שום טקסט נוסף לפני או אחרי, לפי המבנה הבא משמאל לימין:
{
  "project_num": "מספר פרויקט אם הוזכר, אחרת תשאיר ריק",
  "letter_num": "מספר מכתב/דוח אם הוזכר, אחרת תשאיר ריק",
  "client_name": "שם הלקוח לכבודו נכתב הדוח",
  "contact_person": "לידי מי המכתב מיועד",
  "client_email": "כתובת מייל אם הוזכרה",
  "structure_name": "שם המבנה או הפרויקט",
  "inspection_subject": "מה בוצע במהלך הסיור (למשל: בדיקת זיון תקרת קומה א)",
  "star_present": "מי נוכח מטעם סטאר מהנדסים (למשל: הח\"ม)",
  "inspector_name": "שם המפקח באתר",
  "execution_team": "נציגי הביצוע/קבלן",
  "author_initials": "ראשי תיבות של המהנדס",
  "work_status": "תיאור קצר ומקצועי של מצב העבודה הנוכחי באתר לפי דברי המהנדס"
}
השתמש בשפה מקצועית של מהנדסי בניין. אם פרט מסוים לא הוזכר בטקסט, השאר אותו כריק ("").
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != MY_CHAT_ID:
        return
    await update.message.reply_text("🏗️ בוט פיקוח עליון של סטאר מהנדסים פעיל!\nשלח לי הודעה חופשית (טקסט או קול) עם פרטי הסיור, ואני אכין לך את הדוח.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != MY_CHAT_ID:
        await update.message.reply_text("אין לך הרשאה להשתמש בבוט זה.")
        return

    user_text = update.message.text
    await update.message.reply_text("🔄 מעבד את הנתונים באמצעות AI, אנא המתן...")

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"{PROMPT_INSTRUCTIONS}\n\nהטקסט מהשטח:\n{user_text}")
        
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        
        data["telegram_user"] = update.effective_user.username or "Aviv"
        data["report_date"] = datetime.now().strftime("%d/%m/%Y")
        data["visit_date"] = datetime.now().strftime("%d/%m/%Y")
        data["remarks_json"] = []

        # שמירה ב-Supabase
        supabase.table("reports").insert(data).execute()
        
        await update.message.reply_text(f"✅ הנתונים נקלטו בהצלחה בבסיס הנתונים עבור פרויקט {data.get('project_num', '')}!\nכעת תוכל לפתוח את אפליקציית ה-Streamlit ולמשוך את הנתונים.")
        
    except Exception as e:
        await update.message.reply_text(f"❌ התרחשה שגיאה בעיבוד הנתונים: {e}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()