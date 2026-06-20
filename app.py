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
    .stDownloadButton { text-align: right; }
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
star_present = st.text_input("נוכח מטעם סטאר מהנדסים", value='הח"מ')
inspector_name = st.text_input("שם המפקח באתר", value="מפקח נחמד")
execution_team = st.text_input("נציגי הביצוע", value="אחמד ויוסי")
author_initials = st.text_input("ראשי תיבות של כותב הדוח (עבור ה-Footer)", value="A.K")

# חלק 3: מצב העבודה באתר
st.header("🚧 מצב העבודה באתר")
work_status = st.text_area("תיאור מצב העבודה הנוכחי באתר:", value="רוב הברזל מורכב במלואו")

# חלק 4: חתימת המהנדס
st.header("✒️ חתימת המהנדס")
signature_file = st.file_uploader("העלה תמונת חתימה:", type=["png", "jpg", "jpeg"])

# חלק 5: הערות דינמיות וליקויים מהאתר
st.header("📸 הערות ספציפיות וליקויי סיור")
st.write("כאן ניתן להוסיף הערות חופשיות ממוספרות (מ-4.1 ואילך) ותמונה:")

if 'dynamic_remarks' not in st.session_state:
    st.session_state.dynamic_remarks = [{'text': '', 'image': None}]

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