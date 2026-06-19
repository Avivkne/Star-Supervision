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
    .stCheckbox { text-align: right; direction: RTL; }
    </style>
""", unsafe_allow_html=True)

# כותרת ראשית משולבת עם לוגו (אופציה א')
col_logo1, col_logo2 = st.columns([1, 4])
with col_logo1:
    try:
        st.image("logo.png", width=120)
    except:
        pass  # אם הלוגו עדיין לא הועלה, האפליקציה לא תתרסק ותציג רק כותרת

with col_logo2:
    st.title("🏗️ מחולל דוחות פיקוח עליון")

st.write("מלא את הפרטים להלן ולחץ על כפתור ההפקה בתחתית העמוד")

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
structure_name = st.text_input("שם המבנה / הפרויקט", value="מבנה XXXX")
visit_date = st.text_input("תאריך הסיור", value=datetime.now().strftime("%d/%m/%Y"))
inspection_subject = st.text_input("במהלך הסיור בוצע פיקוח ל...", value="האלמנט/אלמנטים נבדקים")

st.header("👥 נוכחים בסיור")
inspector_name = st.text_input("שם המפקח באתר", value="מפקח נחמד")
execution_team = st.text_input("נציגי הביצוע", value="אחמד ויוסי")
author_initials = st.text_input("ראשי תיבות של כותב הדוח (עבור ה-Footer)", value="A.K")

# אזור הערות עם צ'קבוקסים ובנק משפטים
st.header("📝 ממצאים והערות")
st.write("בחר את המשפטים הרלוונטיים לסיור זה:")

# הגדרת בנק המשפטים (הצ'קבוקסים)
note1 = st.checkbox("1. יש להסיר שאריות בטון ישן מתחתית ברזלי הזיון.")
note2 = st.checkbox("2. יש לדאוג טרם היציקה שמשטח היציקה נקי משאריות לכלוך ופסולת.")
note3 = st.checkbox("3. יש לשמור על עובי כיסוי עפ\"י המצוין בתכניות.")
note4 = st.checkbox("4. ניתן להמשיך בעבודות לאחר אישור סופי של המפקח. על המפקח לבדוק את הזיון ואת הרכיבים השונים באופן סופי לפני היציקה.")
note5 = st.checkbox("5. במידה וישנן שאלות נוספות, ניתן לפנות אלינו בכל עת.")

# תיבת טקסט חופשי להערות נוספות וספציפיות
st.write("---")
extra_remarks = st.text_area("הערות וליקויים נוספים (כל הערה בשורה חדשה):", value="")

# כפתור הפקה
if st.button("🚀 הפק דוח Word"):
    try:
        # טעינת התבנית
        doc = DocxTemplate("template.docx")
        
        # איסוף ההערות שנבחרו בצ'קבוקסים
        final_remarks_list = []
        if note1: final_remarks_list.append("יש להסיר שאריות בטון ישן מתחתית ברזלי הזיון.")
        if note2: final_remarks_list.append("יש לדאוג טרם היציקה שמשטח היציקה נקי משאריות לכלוך ופסולת.")
        if note3: final_remarks_list.append("יש לשמור על עובי כיסוי עפ\"י המצוין בתכניות.")
        if note4: final_remarks_list.append("ניתן להמשיך בעבודות לאחר אישור סופי של המפקח. על המפקח לבדוק את הזיון ואת הרכיבים השונים באופן סופי לפני היציקה.")
        if note5: final_remarks_list.append("במידה וישנן שאלות נוספות, ניתן לפנות אלינו בכל עת.")
        
        # הוספת ההערות החופשיות שנכתבו בתיבה (אם נכתבו)
        if extra_remarks.strip():
            for line in extra_remarks.split("\n"):
                if line.strip():
                    final_remarks_list.append(line.strip())
        
        # חיבור כל ההערות יחד עם ירידת שורה של וורד
        remarks_formatted = "\n".join(final_remarks_list)
        
        # סנכרון המשתנים עם קובץ הוורד
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