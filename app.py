import streamlit as st
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
import io
from datetime import datetime

# הגדרת כיוון כתיבה מימין לשמאל עבור הממשק
st.set_page_config(layout="centered", page_title="מחולל דוחות פיקוח עליון")

# עיצוב בסיסי בעברית ותיקון כיווניות (RTL) + עיצוב הקרדיט בתחתית
st.markdown("""
    <style>
    body { direction: RTL; text-align: right; }
    div[data-testid="stMarkdownContainer"] { text-align: right; }
    .stTextInput th { text-align: right; }
    input { direction: RTL; text-align: right; }
    textarea { direction: RTL; text-align: right; }
    .stCheckbox { text-align: right; direction: RTL; }
    
    /* עיצוב כפתור ההורדה שיישאר מיושר לימין */
    .stDownloadButton { text-align: right; }
    
    /* עיצוב הקרדיט בתחתית שמאל - גודל 16 */
    .footer-credit {
        position: fixed;
        left: 20px;
        bottom: 20px;
        text-align: left;
        direction: ltr;
        color: #888888;
        font-size: 16px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# הצגת הלוגו מוקטן וממורכז באמצע הדף
try:
    col_space1, col_logo, col_space2 = st.columns([1.2, 2.6, 1.2])
    with col_logo:
        st.image("logo.png", width=245)
except:
    pass

st.markdown("<h1 style='text-align: center;'>🏗️ מחולל דוחות פיקוח עליון</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>מלא את הפרטים להלן ולחץ על כפתור ההפקה בתחתית העמוד</p>", unsafe_allow_html=True)

# חלוקה לאזורים בטופס
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
star_present = st.text_input("נוכח מטעם סטאר מהנדסים (הח\"מ)", value="הח\"מ")
inspector_name = st.text_input("שם המפקח באתר", value="מפקח נחמד")
execution_team = st.text_input("נציגי הביצוע", value="אחמד ויוסי")
author_initials = st.text_input("ראשי תיבות של כותב הדוח (עבור ה-Footer)", value="A.K")

# חלק חדש: רשימת תפוצה / העתקים קבועה עם אפשרות עריכה
st.header("📨 העתקים (רשימת תפוצה)")
col_cc1, col_cc2 = st.columns(2)
with col_cc1:
    cc_1 = st.text_input("העתק 1", value="בוריס בקלמן – סטאר מהנדסים")
    cc_2 = st.text_input("העתק 2", value="מנהל פרויקט")
with col_cc2:
    # סעיף 3 משלב אוטומטית את מספר הפרויקט שהוקלד למעלה
    cc_3 = st.text_input("העתק 3", value=f"תיק פרויקט-{project_num}")
    cc_4 = st.text_input("העתק 4", value="תיק כללי")

# חלק 4: הערות דינמיות וליקויים מהאתר (מתחיל מ-4.1)
st.header("📸 הערות ספציפיות וליקויי סיור")
st.write("כאן ניתן להוסיף הערות חופשיות ממוספרות (מ-4.1 ואילך) ולהעלות תמונה מתחת לכל אחת מהן:")

# אתחול ה-session_state עבור רשימת ההערות הדינמיות אם לא קיים
if 'dynamic_remarks' not in st.session_state:
    st.session_state.dynamic_remarks = [{'text': '', 'image': None}]

# לולאה שמציגה את כל תיבות הטקסט והתמונות הקיימות בזיכרון
for idx, item in enumerate(st.session_state.dynamic_remarks):
    current_num = f"4.{idx + 1}"
    st.write(f"**הערה {current_num}**")
    
    st.session_state.dynamic_remarks[idx]['text'] = st.text_area(
        f"פירוט הליקוי עבור סעיף {current_num}:", 
        value=item['text'], 
        key=f"text_{idx}",
        label_visibility="collapsed"
    )
    
    st.session_state.dynamic_remarks[idx]['image'] = st.file_uploader(
        f"העלה תמונה עבור סעיף {current_num}:", 
        type=["png", "jpg", "jpeg"], 
        key=f"image_{idx}"
    )
    st.write("---")

# כפתור להוספת סעיף הערה ותמונה נוסף (אינסופי)
if st.button("➕ הוסף הערה ותמונה נוספת"):
    st.session_state.dynamic_remarks.append({'text': '', 'image': None})
    st.rerun()

# חלק 5: אזור הערות כלליות עם צ'קבוקסים (מתחיל מ-5.1)
st.header("📝 הערות וממצאים כלליים")
st.write("בחר את המשפטים הרלוונטיים (הסעיפים ימוספרו אוטומטית החל מ-5.1):")

note1 = st.checkbox("יש להסיר שאריות בטון ישן מתחתית ברזלי הזיון.")
note2 = st.checkbox("יש לדאוג טרם היציקה שמשטח היציקה נקי משאריות לכלוך ופסולת.")
note3 = st.checkbox("יש לשמור על עובי כיסוי עפ\"י המצוין בתכניות.")
note4 = st.checkbox("ניתן להמשיך בעבודות לאחר אישור סופי של המפקח. על המפקח לבדוק את הזיון ואת הרכיבים השונים באופן סופי לפני היציקה.")
note5 = st.checkbox("במידה וישנן שאלות נוס