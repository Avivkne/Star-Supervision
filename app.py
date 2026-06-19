import streamlit as st
from docxtpl import DocxTemplate
import io
from datetime import datetime

# הגדרת כיוון כתיבה מימין לשמאל עבור הממשק
st.set_page_config(layout="centered", page_title="מחולל דוחות פיקוח עליון")

# עיצוב בסיסי בעברית ותיקון כיווניות (RTL)
st.markdown("""
    <style>
    body { direction: RTL; text-align: right; }
    div[data-testid="stMarkdownContainer"] { text-align: right; }
    .stTextInput th { text-align: right; }
    input { direction: RTL; text-align: right; }
    textarea { direction: RTL; text-align: right; }
    </style>
""", unsafe_allow_html=True)

st.title("🏗️ מחולל דוחות פיקוח עליון - סטאר מהנדסים")
st.write("מלא את הפרטים להלן ולחץ על כפתור ההפקה בתחתית העמוד.")

# חלוקה לכרטיסיות / אזורים בטופס
st.header("📋 פרטי המכתב והפרויקט")
col1, col2 = st.columns(2)

with col1:
    project_num = st.text_input("מספר פרויקט", value="1001")
    letter_num = st.text_input("מספר מכתב", value="01")
    report_date = st.text_input("תאריך המכתב", value=datetime.now().strftime("%d.%m.%Y"))

with col2:
    client_name = st.text_input("לכבוד (שם הלקוח)", value="חברת אזורים")
    contact_person = st.text_input("לידי", value="ישראל ישראלי")
    client_email = st.text_input("במייל", value="office@client.com")

st.header("🏢 פרטי הסיור")
structure_name = st.text_input("שם המבנה / הפרויקט (להנדון)", value="מבנה מגורים א'")
visit_date = st.text_input("תאריך הסיור", value=datetime.now().strftime("%d.%m.%Y"))
inspection_subject = st.text_input("במהלך הסיור בוצע פיקוח ל...", value="זיון תקרת קומה 1")

st.header("👥 נוכחים בסיור")
inspector_name = st.text_input("שם המפקח באתר", value="משה כהן")
execution_team = st.text_input("נציגי הביצוע", value="אחמד ויוסי")
author_initials = st.text_input("ראשי תיבות של כותב הדוח (עבור ה-Footer)", value="י.ק.")

st.header("📝 ממצאים והערות")
remarks_text = st.text_area(
    "הערות הפיקוח (רשום כל הערה בשורה חדשה):", 
    value="יש להסיר שאריות בטון ישן מתחתית ברזלי הזיון.\nיש לדאוג טרם היציקה שמשטח היציקה נקי משאריות לכלוך ופסולת.\nיש לשמור על עובי כיסוי עפ\"י המצוין בתכניות."
)

# כפתור הפקה
if st.button("🚀 הפק דוח Word"):
    try:
        # טעינת התבנית
        doc = DocxTemplate("template.docx")
        
        # הכנת רשימת ההערות בפורמט נקי
        remarks_list = [line.strip() for line in remarks_text.split("\n") if line.strip()]
        # חיבור ההערות עם ירידת שורה של וורד
        remarks_formatted = "\n".join(remarks_list)
        
        # סנכרון המשתנים
        context = {
            'report_date': report_date,
            'project_num': project_num,
            'letter_num': letter_num,
            'client_name': client_name,
            'contact_person': contact_person,
            'client_email': client_email,
            'structure_name': structure_name,
            'visit_date': visit_date,
            'inspection_subject': inspection_subject,
            'inspector_name': inspector_name,
            'execution_team': execution_team,
            'author_initials': author_initials,
            'remarks': remarks_formatted
        }
        
        # רינדור הנתונים לתוך הוורד
        doc.render(context)
        
        # שמירה לזיכרון כדי לאפשר הורדה בדפדפן
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        
        st.success("🎉 הדוח הופק בהצלחה! לחץ על הכפתור למטה כדי להוריד אותו:")
        
        st.download_button(
            label="💾 הורד קובץ Word מוכן",
            data=bio,
            file_name=f"דו_ח_פיקוח_{project_num}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except FileNotFoundError:
        st.error("שגיאה: קובץ התבנית 'template.docx' לא נמצא באותה תיקייה של הקוד.")
    except Exception as e:
        st.error(f"התרחשה שגיאה: {str(e)}")