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

# חלק 4: הערות דינמיות וליקויים מהאתר
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
        type=["png", "jpg", "jpeg"], 
        key=f"image_{idx}"
    )
    st.write("---")

if st.button("➕ הוסף הערה ותמונה נוספת"):
    st.session_state.dynamic_remarks.append({'text': '', 'image': None})
    st.rerun()

# חלק 5: אזור הערות כלליות עם צ'קבוקסים
st.header("📝 הערות וממצאים כלליים")
st.write("בחר את המשפטים הרלוונטיים (הסעיפים ימוספרו אוטומטית החל מ-5.1):")

txt1 = "יש להסיר שאריות בטון ישן מתחתית ברזלי הזיון."
txt2 = "יש לדאוג טרם היציקה שמשטח היציקה נקי משאריות לכלוך ופסולת."
txt3 = "יש לשמור על עובי כיסוי עפ\"י המצוין בתכניות."
txt4 = "ניתן להמשיך בעבודות לאחר אישור סופי של המפקח. על המפקח לבדוק את הזיון ואת הרכיבים השונים באופן סופי לפני היציקה."
txt5 = "במידה וישנן שאלות נוספות, ניתן לפנות אלינו בכל עת."

note1 = st.checkbox(txt1)
note2 = st.checkbox(txt2)
note3 = st.checkbox(txt3)
note4 = st.checkbox(txt4)
note5 = st.checkbox(txt5)

# חלק 6: חתימת המהנדס
st.header("✒️ חתימת המהנדס")
signature_file = st.file_uploader("העלה תמונת חתימה:", type=["png", "jpg", "jpeg"])

# חלק 7: העתקים
st.header("📨 העתקים")
default_cc_text = f"1. בוריס בקלמן/ישראל קנר – סטאר מהנדסים\n2. ראש צוות - סטאר מהנדסים\n3. מנהל פרויקט\n4. תיק פרויקט\n5. תיק כללי"
cc_list = st.text_area("רשימת תפוצה לעריכה:", value=default_cc_text, height=140)

# כפתור הפקה
if st.button("🚀 הפק קובץ Word"):
    try:
        doc = DocxTemplate("template.docx")
        rlm = "\u200f"
        
        # בניית רשימת הערות כלליות
        general_remarks_list = []
        general_counter = 1
        notes = [note1, note2, note3, note4, note5]
        texts = [txt1, txt2, txt3, txt4, txt5]
        
        for i, note in enumerate(notes):
            if note:
                general_remarks_list.append(f"{rlm}5.{general_counter}.{rlm} {texts[i]}{rlm}")
                general_counter += 1

        cc_final_list = [f"{rlm}{line.strip()}{rlm}" for line in cc_list.split('\n') if line.strip()]

        specific_remarks_list = []
        for idx, item in enumerate(st.session_state.dynamic_remarks):
            current_num = f"4.{idx + 1}"
            if item['text'].strip():
                remark_data = {
                    'text': f"{rlm}{current_num}.{rlm} {item['text'].strip()}{rlm}",
                    'image': InlineImage(doc, item['image'], width=Inches(2)) if item['image'] else None
                }
                specific_remarks_list.append(remark_data)

        formatted_work_status = "\n".join([f"{rlm}{line}{rlm}" for line in work_status.split("\n")])
        final_signature_image = InlineImage(doc, signature_file, width=Inches(1.5)) if signature_file else None

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
            'star_present': f"{rlm}{star_present}{rlm}",
            'inspector_name': inspector_name,
            'execution_team': execution_team,
            'author_initials': author_initials,
            'work_status': formatted_work_status,
            'signature_image': final_signature_image,
            'specific_remarks_list': specific_remarks_list,
            'general_remarks_list': general_remarks_list,
            'cc_final_list': cc_final_list
        }

        doc.render(context)
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        
        st.success("🎉 הדוח הופק בהצלחה!")
        st.download_button("💾 הורד קובץ Word מוכן", bio, f"{project_num}-{letter_num}.docx", "application/octet-stream")
    except Exception as e:
        st.error(f"התרחשה שגיאה: {str(e)}")

st.markdown("<div class='footer-credit'>נבנה ע\"י אביב קנבל, סטאר מהנדסים</div>", unsafe_allow_html=True)