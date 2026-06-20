import streamlit as st
from docxtpl import DocxTemplate, RichText
from docx.shared import Pt
import io
from datetime import datetime

# הגדרת כיוון כתיבה מימין לשמאל עבור הממשק
st.set_page_config(layout="centered", page_title="מחולל דוחות פיקוח עליון")

# עיצוב בסיסי בעברית ותיקון כיווניות (RTL) + מרכזי לוגו
st.markdown("""
    <style>
    body { direction: RTL; text-align: right; }
    div[data-testid="stMarkdownContainer"] { text-align: right; }
    .stTextInput th { text-align: right; }
    input { direction: RTL; text-align: right; }
    textarea { direction: RTL; text-align: right; }
    .stCheckbox { text-align: right; direction: RTL; }
    
    /* מירכוז מוחלט של אלמנטים בקונטיינר של הלוגו */
    .centered-logo {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-left: auto;
        margin-right: auto;
        width: 100%;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 1. הצגת הלוגו מוגדל (רוחב 350) וממורכז לחלוטין באמצע הדף
try:
    # יצירת מירכוז בעזרת עמודות - עמודה אמצעית רחבה
    col_space1, col_logo, col_space2 = st.columns([1, 3, 1])
    with col_logo:
        st.image("logo.png", use_container_width=True)
except:
    pass  # אם הלוגו לא נמצא, האפליקציה תמשיך לרוץ כרגיל

st.markdown("<h1 style='text-align: center;'>🏗️ מחולל דוחות פיקוח עליון</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>מלא את הפרטים להלן ולחץ על כפתור ההפקה בתחתית העמוד</p>", unsafe_allow_html=True)

# חלוקה לכרטיסיות / אזורים בטופס
st.header("📋 פרטי המכתב והפרויקט")
col1, col2 = st.columns(2)

with col1:
    project_num = st.text_input("מספר פרויקט", value="23R001")
    letter_num = st.text_input("מספר מכתב", value="L01")
    report_date = st.text_input("תאריך המכתב", value=datetime.now().strftime("%d/%m/%Y"))

with col2:
    client_name = st.text_input("לכבוד (שם הלקוח)", value="לקוח")
    contact_person = st.text_input("לידי", value="המפקח/מנהל הפרוייקט")
    client_email = st.text_input("במייל", value="office@client.com")

st.header("🏢 פרטי הסיור")
structure_name = st.text_input("שם המבנה / הפרויקט", value="1538")
visit_date = st.text_input("תאריך הסיור", value=datetime.now().strftime("%d/%m/%Y"))
inspection_subject = st.text_input("במהלך הסיור בוצע פיקוח ל...", value="האלמנט/אלמנטים נבדקים")

st.header("👥 נוכחים בסיור")
inspector_name = st.text_input("שם המפקח באתר", value="מפקח נחמד")
execution_team = st.text_input("נציגי הביצוע", value="אחמד ויוסי")
author_initials = st.text_input("ראשי תיבות של כותב הדוח (עבור ה-Footer)", value="A.K")

# אזור הערות עם צ'קבוקסים ובנק משפטים
st.header("📝 ממצאים והערות")
st.write("בחר את המשפטים הרלוונטיים לסיור זה (הסעיפים ימוספרו אוטומטית):")

# הגדרת בנק המשפטים (הצ'קבוקסים)
note1 = st.checkbox("יש להסיר שאריות בטון ישן מתחתית ברזלי הזיון.")
note2 = st.checkbox("יש לדאוג טרם היציקה שמשטח היציקה נקי משאריות לכלוך ופסולת.")
note3 = st.checkbox("יש לשמור על עובי כיסוי עפ\"י המצוין בתכניות.")
note4 = st.checkbox("ניתן להמשיך בעבודות לאחר אישור סופי של המפקח. על המפקח לבדוק את הזיון ואת הרכיבים השונים באופן סופי לפני היציקה.")
note5 = st.checkbox("במידה וישנן שאלות נוספות, ניתן לפנות אלינו בכל עת.")

# תיבת טקסט חופשי להערות נוספות וספציפיות
st.write("---")
extra_remarks = st.text_area("הערות וליקויים נוספים (כל הערה בשורה חדשה, ימוספרו בהמשך):", value="")

# כפתור הפקה
if st.button("🚀 הפק דוח Word"):
    try:
        # טעינת התבנית
        doc = DocxTemplate("template.docx")
        
        # 2. מנגנון יצירת סעיפים ממוספרים רצים (רק עבור מה שסומן ב-V)
        final_remarks_list = []
        item_counter = 1
        
        if note1: 
            final_remarks_list.append(f"{item_counter}. יש להסיר שאריות בטון ישן מתחתית ברזלי הזיון.")
            item_counter += 1
        if note2: 
            final_remarks_list.append(f"{item_counter}. יש לדאוג טרם היציקה שמשטח היציקה נקי משאריות לכלוך ופסולת.")
            item_counter += 1
        if note3: 
            final_remarks_list.append(f"{item_counter}. יש לשמור על עובי כיסוי עפ\"י המצוין בתכניות.")
            item_counter += 1
        if note4: 
            final_remarks_list.append(f"{item_counter}. ניתן להמשיך בעבודות לאחר אישור סופי של המפקח. על המפקח לבדוק את הזיון ואת הרכיבים השונים באופן סופי לפני היציקה.")
            item_counter += 1
        if note5: 
            final_remarks_list.append(f"{item_counter}. במידה וישנן שאלות נוספות, ניתן לפנות אלינו בכל עת.")
            item_counter += 1
        
        # הוספת ההערות החופשיות והמשך המספור הרץ שלהן
        if extra_remarks.strip():
            for line in extra_remarks.split("\n"):
                if line.strip():
                    final_remarks_list.append(f"{item_counter}. {line.strip()}")
                    item_counter += 1
        
        # חיבור כל ההערות יחד עם ירידת שורה של וורד
        remarks_formatted = "\n".join(final_remarks_list)
        
        # פונקציית עזר להמרת טקסט רגיל לטקסט מעוצב בגופן David ובגודל 13.5
        def format_david(text_val):
            rt = RichText()
            rt.add(text_val, font='David', size=Pt(13.5))
            return rt

        # סנכרון המשתנים עם קובץ הוורד והחלת העיצוב המבוקש
        context = {
            'report_date': format_david(report_date),
            'project_num': format_david(project_num),
            'letter_num': format_david(letter_num),
            'client_name': format_david(client_name),
            'contact_person': format_david(contact_person),
            'client_email': format_david(client_email),
            'structure_name': format_david(structure_name),
            'visit_date': format_david(visit_date),
            'inspection_subject': format_david(inspection_subject),
            'inspector_name': format_david(inspector_name),
            'execution_team': format_david(execution_team),
            'author_initials': format_david(author_initials),
            'remarks': format_david(remarks_formatted)
        }
        
        # רינדור הנתונים לתוך הוורד
        doc.render(context)
        
        # שמירה לזיכרון כדי לאפשר הורדה בדפדפן
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        
        st.success("🎉 הדוח הופק בהצלחה! לחץ על הכפתור למטה כדי להוריד אותו:")
        
        # שם הקובץ שונה לפורמט הדינמי המבוקש: {project_num}-{letter_num}.docx
        st.download_button(
            label="💾 הורד קובץ Word מוכן",
            data=bio,
            file_name=f"{project_num}-{letter_num}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except FileNotFoundError:
        st.error("שגיאה: קובץ התבנית 'template.docx' לא נמצא באותה תיקייה של הקוד.")
    except Exception as e:
        st.error(f"התרחשה שגיאה: {str(e)}")