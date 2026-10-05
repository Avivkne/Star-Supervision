# -*- coding: utf-8 -*-
"""
בוט טלגרם להפקת דוחות פיקוח עליון.
זרימה: הודעות קוליות / טקסט / תמונות -> חילוץ שדות והערות (gpt-4o-mini)
       -> השלמת פרטים חסרים בדיאלוג -> אישור -> קובץ Word מתבנית docxtpl.

משתני סביבה (ב-Render):
  TELEGRAM_BOT_TOKEN   (חובה)
  OPENAI_API_KEY       (חובה)
  ALLOWED_USER_IDS     (מומלץ) מזהי טלגרם מופרדים בפסיק; ריק = כולם מורשים
  DEFAULT_CC           (אופציונלי) נמענים קבועים להעתק, מופרדים ב-|
  OPENAI_MODEL=gpt-4o-mini | TRANSCRIBE_MODEL=whisper-1 | TEMPLATE_PATH=template.docx
"""
import json
import logging
import os
import shutil
import tempfile
import threading
from collections import defaultdict
from datetime import date
from functools import wraps
from http.server import BaseHTTPRequestHandler, HTTPServer

import telebot
from openai import OpenAI
from telebot import types

from report_builder import FIELDS, build_report, with_derived

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("inspection-bot")

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TRANSCRIBE_MODEL = os.getenv("TRANSCRIBE_MODEL", "whisper-1")
ALLOWED = {int(x) for x in os.getenv("ALLOWED_USER_IDS", "").split(",") if x.strip()}
DEFAULT_CC = [x.strip() for x in os.getenv("DEFAULT_CC", "").split("|") if x.strip()]

bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=8)
# ברירת מחדל: OpenAI. לשימוש בספק תואם (למשל Groq בחינם) מגדירים LLM_BASE_URL ו-LLM_API_KEY
client = OpenAI(
    api_key=os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL") or None,
)

BTN_DONE = "✅ סיום והפקת דוח"
BTN_STATUS = "📋 מצב נוכחי"
BTN_NEW = "🗑 התחל מחדש"

WHISPER_HINT = ("דוח פיקוח עליון על ביצוע מבנה. בטון, זיון, ברזל, תבניות, יציקה, כלונסאות, "
                "קורות, עמודים, תקרה, יסודות, קירות, מרתף, קונסטרוקציה, ציר, קומה.")

# ------------------------------------------------------------------ מצב שיחה
# stage: collecting -> asking (שאלות על שדות חסרים) -> confirm -> (הפקה) -> איפוס
STATES = {}
LOCKS = defaultdict(threading.RLock)  # נעילה לכל צ'אט: שומר על סדר הודעות/תמונות


def new_state():
    return {
        "stage": "collecting",
        "fields": {},
        "specific": [],      # [{"text": str, "images": [paths]}]
        "general": [],       # [str]
        "cc": [],            # [str]
        "pending": [],       # תמונות שחיכו לתיאור
        "asking": None,
        "img_n": 0,
        "last_ack_group": None,
        "dir": tempfile.mkdtemp(prefix="report_"),
    }


def get_state(chat_id):
    if chat_id not in STATES:
        STATES[chat_id] = new_state()
    return STATES[chat_id]


def reset_state(chat_id):
    st = STATES.pop(chat_id, None)
    if st:
        shutil.rmtree(st["dir"], ignore_errors=True)
    return get_state(chat_id)


def main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(BTN_DONE)
    kb.row(BTN_STATUS, BTN_NEW)
    return kb


def guarded(fn):
    """הרשאות + נעילה לכל צ'אט + תפיסת שגיאות."""
    @wraps(fn)
    def wrapper(obj):
        chat_id = obj.chat.id if hasattr(obj, "chat") else obj.message.chat.id
        if ALLOWED and obj.from_user.id not in ALLOWED:
            return
        with LOCKS[chat_id]:
            try:
                fn(obj, chat_id)
            except Exception:
                log.exception("handler failed")
                bot.send_message(chat_id, "⚠️ אירעה שגיאה בעיבוד. נסה שוב, ואם זה חוזר שלח /new והתחל מחדש.")
    return wrapper


# ------------------------------------------------------------------ OpenAI
SYSTEM_PROMPT = """אתה עוזר למהנדס קונסטרוקטור בהפקת דוח פיקוח עליון על ביצוע.
תקבל JSON עם known_fields (פרטים שכבר ידועים) ו-input (טקסט חופשי או תמלול הקלטה מהשטח).
החזר JSON בלבד, במבנה הבא:
{"fields": {...}, "specific_remarks": ["..."], "general_remarks": ["..."], "cc": ["..."]}

מפתחות מותרים ב-fields: __KEYS__

כללים:
0. אופן הצגת השדות בתבנית המכתב (חשוב לנסח בהתאם):
   - structure_name: רק שם/סימון המבנה, בלי המילה "מבנה" (התבנית כבר כוללת אותה). למשל: ב', A, מגדל 3.
   - inspection_subject: ביטוי שם בלי אות ל' בהתחלה (התבנית כותבת "בוצע פיקוח ל" לפניו). למשל: יציקת תקרת קומה 2, זיון עמודים.
   - work_status: פסקה קצרה (1-3 משפטים) בלשון רשמית שמתארת את מצב העבודה בעת הסיור, רק לפי מה שנאמר.
   - inspector_name: שם המפקח בלבד. execution_team: שמות/תפקידי נציגי הביצוע שנכחו.
   - star_present: שמות נציגי "סטאר מהנדסים" שנכחו.
   - author_initials: ראשי התיבות של inspector_name באנגלית, אות גדולה ונקודה בין האותיות, למשל A.K.
     תעתק את השם לאנגלית (אביב קנבל -> Aviv Knebl -> A.K). חשב אותם בכל פעם שמופיע או משתנה inspector_name.
     אם נאמרו ראשי תיבות במפורש, השתמש בהם כפי שנאמרו.
1. fields: כלול רק שדה שנאמר במפורש ב-input. אל תנחש ואל תמציא. אם ה-input מתקן שדה ידוע, החזר את הערך החדש.
   תאריכים בפורמט DD/MM/YYYY. תאריך היום: __TODAY__ (פענח "היום", "אתמול" וכד' ביחס אליו).
2. specific_remarks: כל ממצא/הערה הקשורים לאלמנט או מיקום מסוים (קורה, עמוד, ציר, קומה, יציקה...).
   נסח מחדש בעברית הנדסית מקצועית, תמציתית, בלשון רשמית ("נמצא כי...", "יש לבצע..."),
   ושמור במדויק על כל המספרים, המידות, הצירים, הקומות ושמות האלמנטים. אל תוסיף עובדות.
   ממצאים שונים = הערות נפרדות.
3. general_remarks: הערות כלליות שאינן קשורות לאלמנט ספציפי (התקדמות, בטיחות, לוחות זמנים, הנחיות כלליות).
4. cc: שמות/אימיילים שהתבקש להעתיק אליהם.
5. דיבור אל הבוט ("שלום", "תכין דוח", "סיימתי") אינו תוכן. החזר רשימות ריקות.
6. אם ה-input מתחיל ב-"[תשובה לשאלה: X]" זו תשובה לשדה X; הצב אותה בשדה המתאים.
7. כל מחרוזת בשורה אחת, בלי ירידות שורה."""


def _clean_list(value):
    out = []
    for item in value if isinstance(value, list) else []:
        if isinstance(item, dict):
            item = item.get("text", "")
        item = " ".join(str(item).split())
        if item:
            out.append(item)
    return out


def extract(text, st):
    prompt = (SYSTEM_PROMPT
              .replace("__KEYS__", ", ".join(FIELDS))
              .replace("__TODAY__", date.today().strftime("%d/%m/%Y")))
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps({"known_fields": st["fields"], "input": text},
                                                   ensure_ascii=False)},
        ],
    )
    try:
        data = json.loads(resp.choices[0].message.content)
    except (ValueError, TypeError):
        data = {}
    fields = {}
    for k, v in (data.get("fields") or {}).items():
        if k in FIELDS and v not in (None, "", "null"):
            fields[k] = " ".join(str(v).split())
    return {
        "fields": fields,
        "specific": _clean_list(data.get("specific_remarks")),
        "general": _clean_list(data.get("general_remarks")),
        "cc": _clean_list(data.get("cc")),
    }


def transcribe(audio_bytes, filename):
    r = client.audio.transcriptions.create(
        model=TRANSCRIBE_MODEL, file=(filename, audio_bytes), language="he", prompt=WHISPER_HINT)
    return (r.text or "").strip()


def tg_download(file_id):
    info = bot.get_file(file_id)
    return bot.download_file(info.file_path), info.file_path


# ------------------------------------------------------------------ לוגיקת שיחה
def missing_required(st):
    return [k for k, (_, req) in FIELDS.items() if req and not st["fields"].get(k)]


def build_summary(st):
    lines = ["📋 סיכום הדוח", f"תאריך הדוח: {date.today().strftime('%d/%m/%Y')} (אוטומטי)"]
    shown = with_derived(st["fields"])
    for k, (label, req) in FIELDS.items():
        lines.append(f"{label}: {shown.get(k) or '—'}")
    with_img = sum(1 for r in st["specific"] if r["images"])
    lines.append(f"הערות ספציפיות: {len(st['specific'])} (מתוכן {with_img} עם תמונות)")
    lines.append(f"הערות כלליות: {len(st['general'])}")
    if st["pending"]:
        lines.append(f"תמונות שממתינות לתיאור: {len(st['pending'])}")
    return "\n".join(lines)


def start_finish(chat_id, st):
    # תמונות שנשארו בלי תיאור: משייכים להערה האחרונה, או יוצרים הערה
    if st["pending"]:
        if st["specific"]:
            st["specific"][-1]["images"] += st["pending"]
        else:
            st["specific"].append({"text": "(ללא תיאור)", "images": list(st["pending"])})
        st["pending"] = []
    if not st["specific"] and not st["general"]:
        bot.send_message(chat_id, "עדיין לא התקבלו הערות. שלח הקלטה, טקסט או תמונות ואז לחץ סיום.")
        return
    ask_next(chat_id, st)


def ask_next(chat_id, st):
    missing = missing_required(st)
    if missing:
        st["stage"], st["asking"] = "asking", missing[0]
        label = FIELDS[missing[0]][0]
        bot.send_message(chat_id, f"חסר פרט: {label}.\nאפשר לענות בהקלטה או בטקסט.")
        return
    st["stage"], st["asking"] = "confirm", None
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton("📄 הפק דוח", callback_data="gen"),
           types.InlineKeyboardButton("➕ המשך להוסיף", callback_data="back"))
    bot.send_message(chat_id, build_summary(st) +
                     "\n\nלתיקון פרט אפשר פשוט לכתוב/להקליט, למשל: \"שם הלקוח הוא ...\"", reply_markup=kb)


def handle_content(chat_id, text, images=None):
    """נקודת כניסה אחת לכל טקסט/תמלול, עם או בלי תמונות."""
    st = get_state(chat_id)
    images = images or []

    # --- שלב שאלות על שדות חסרים
    if st["stage"] == "asking":
        st["pending"] += images
        key = st["asking"]
        label = FIELDS[key][0]
        data = extract(f"[תשובה לשאלה: {label}] {text}", st)
        value = data["fields"].get(key) or " ".join(text.split())
        st["fields"][key] = value
        for k, v in data["fields"].items():  # אם נאמרו גם פרטים אחרים
            if k != key and not st["fields"].get(k):
                st["fields"][k] = v
        bot.send_message(chat_id, f"✔️ {label}: {value}")
        ask_next(chat_id, st)
        return

    # --- איסוף רגיל (גם חזרה ממסך האישור לצורך תיקון)
    came_from_confirm = st["stage"] == "confirm"
    st["stage"] = "collecting"
    bot.send_chat_action(chat_id, "typing")
    data = extract(text, st)
    st["fields"].update(data["fields"])
    st["general"] += data["general"]
    st["cc"] += [c for c in data["cc"] if c not in st["cc"]]

    new_remarks = [{"text": t, "images": []} for t in data["specific"]]
    if new_remarks:
        # כל התמונות הממתינות + אלה שהגיעו עם ההודעה -> להערה הראשונה
        new_remarks[0]["images"] = st["pending"] + images
        st["pending"] = []
    elif images:
        # הגיעה תמונה עם כיתוב שהמודל לא סיווג כהערה ספציפית: ההערה היא הכיתוב עצמו
        new_remarks = [{"text": " ".join(text.split()), "images": st["pending"] + images}]
        st["pending"] = []
    st["specific"] += new_remarks

    parts = []
    for r in new_remarks:
        suffix = f" 📷×{len(r['images'])}" if r["images"] else ""
        parts.append(f"• הערה: {r['text'][:140]}{suffix}")
    parts += [f"• הערה כללית: {t[:140]}" for t in data["general"]]
    if data["fields"]:
        parts.append("• פרטים: " + ", ".join(f"{FIELDS[k][0]}={v}" for k, v in data["fields"].items()))
    if not parts:
        parts.append("לא זיהיתי תוכן חדש בהודעה.")
    msg = "✅ נקלט:\n" + "\n".join(parts)
    if came_from_confirm:
        msg += "\n\nעודכן. לחץ \"סיום והפקת דוח\" כדי לחזור לסיכום."
    bot.send_message(chat_id, msg, reply_markup=main_keyboard())


def generate_and_send(chat_id, st):
    bot.send_message(chat_id, "⏳ מפיק את הדוח...")
    bot.send_chat_action(chat_id, "upload_document")
    cc = DEFAULT_CC + [c for c in st["cc"] if c not in DEFAULT_CC]
    path = build_report(st["fields"], st["specific"], st["general"], cc, st["dir"])
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in
                   f"{st['fields'].get('project_num', 'ללא')}_{st['fields'].get('visit_date', '')}")
    with open(path, "rb") as f:
        bot.send_document(chat_id, f, visible_file_name=f"דוח_פיקוח_{safe}.docx",
                          caption="הדוח מוכן ✅ לדוח חדש פשוט התחל לשלוח הודעות.")
    reset_state(chat_id)


# ------------------------------------------------------------------ handlers
@bot.message_handler(commands=["start", "help"])
@guarded
def cmd_start(m, chat_id):
    get_state(chat_id)
    bot.send_message(
        chat_id,
        "שלום! אני מפיק דוחות פיקוח עליון.\n\n"
        "שלח לי מהשטח הקלטות, טקסט ותמונות, בכל סדר:\n"
        "• תמונה עם כיתוב = הערה עם תמונה\n"
        "• תמונה בלי כיתוב = תשויך להקלטה/טקסט הבא\n"
        "• אפשר לומר פרטי פרויקט (לקוח, מבנה, תאריך ביקור...) באותה הקלטה\n\n"
        "בסוף לחץ \"סיום והפקת דוח\". אשאל על מה שחסר ואפיק קובץ Word.",
        reply_markup=main_keyboard())


@bot.message_handler(commands=["new", "cancel"])
@guarded
def cmd_new(m, chat_id):
    reset_state(chat_id)
    bot.send_message(chat_id, "🗑 התחלנו דוח חדש.", reply_markup=main_keyboard())


@bot.message_handler(commands=["status"])
@guarded
def cmd_status(m, chat_id):
    bot.send_message(chat_id, build_summary(get_state(chat_id)))


@bot.message_handler(content_types=["text"])
@guarded
def on_text(m, chat_id):
    text = (m.text or "").strip()
    if text == BTN_DONE:
        start_finish(chat_id, get_state(chat_id))
    elif text == BTN_STATUS:
        bot.send_message(chat_id, build_summary(get_state(chat_id)))
    elif text == BTN_NEW:
        reset_state(chat_id)
        bot.send_message(chat_id, "🗑 התחלנו דוח חדש.", reply_markup=main_keyboard())
    elif text:
        handle_content(chat_id, text)


@bot.message_handler(content_types=["voice", "audio"])
@guarded
def on_voice(m, chat_id):
    media = m.voice or m.audio
    bot.send_chat_action(chat_id, "typing")
    data, tg_path = tg_download(media.file_id)
    if m.voice:
        ext = "ogg"
    else:
        ext = os.path.splitext(tg_path)[1].lstrip(".").lower() or "mp3"
        ext = "ogg" if ext == "oga" else ext
    text = transcribe(data, f"audio.{ext}")
    if not text:
        bot.send_message(chat_id, "לא הצלחתי לשמוע תוכן בהקלטה. נסה שוב.")
        return
    bot.send_message(chat_id, f"🎤 תומלל:\n{text}")
    handle_content(chat_id, text)


@bot.message_handler(content_types=["photo", "document"])
@guarded
def on_photo(m, chat_id):
    if m.content_type == "document":
        if not (m.document.mime_type or "").startswith("image/"):
            bot.send_message(chat_id, "קבצים שאינם תמונה לא נתמכים. שלח תמונה (JPG/PNG).")
            return
        file_id = m.document.file_id
    else:
        file_id = m.photo[-1].file_id  # הגודל הגדול ביותר

    st = get_state(chat_id)
    data, _ = tg_download(file_id)
    st["img_n"] += 1
    path = os.path.join(st["dir"], f"img_{st['img_n']}.jpg")
    with open(path, "wb") as f:
        f.write(data)

    caption = (m.caption or "").strip()
    if caption:
        handle_content(chat_id, caption, images=[path])
        return

    st["pending"].append(path)
    group = m.media_group_id
    if group is None or group != st["last_ack_group"]:  # לא להציף תגובות באלבום
        st["last_ack_group"] = group
        bot.send_message(chat_id, "📷 התמונה נשמרה. שלח תיאור (הקלטה/טקסט) והיא תשויך אליו.")


@bot.callback_query_handler(func=lambda c: c.data in ("gen", "back"))
@guarded
def on_callback(c, chat_id):
    bot.answer_callback_query(c.id)
    st = get_state(chat_id)
    if c.data == "gen":
        if st["stage"] != "confirm":
            return
        generate_and_send(chat_id, st)
    else:
        st["stage"] = "collecting"
        bot.send_message(chat_id, "ממשיכים. שלח עוד הערות או תמונות.", reply_markup=main_keyboard())


# ------------------------------------------------------------------ Render
def start_health_server():
    """Render Web Service דורש פורט פתוח. לא נחוץ אם משתמשים ב-Background Worker."""
    port = os.getenv("PORT")
    if not port:
        return

    class Health(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *args):
            pass

    server = HTTPServer(("0.0.0.0", int(port)), Health)
    threading.Thread(target=server.serve_forever, daemon=True).start()


if __name__ == "__main__":
    start_health_server()
    log.info("bot started")
    # בלי skip_pending: הוא קורס על 409 בהתנגשות זמנית; infinity_polling מנסה שוב לבד
    bot.infinity_polling(timeout=30, long_polling_timeout=30)
