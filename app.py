import streamlit as st
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
import io
from datetime import datetime

# הגדרת כיוון כתיבה מימין לשמאל
st.set_page_config(layout="centered", page_title="מחולל דוחות פיקוח עליון")

st.markdown("""
    <style>
    body { direction: RTL; text-align: right; }
    div[data-testid="stMarkdownContainer"] { text-align: right; }
    input, textarea { direction: RTL; text-align: right; }
    .footer-credit {
        position: fixed; left: 20px; bottom: 20px; text-align: left; 
        direction: ltr; color: #888888; font-size: 16px; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# לוגו
try:
    _, col_logo, _ = st.columns([1.2, 2.6, 1.2])
    with col_logo: st.image("logo.png", width=245)
except: pass

st.markdown("<h1 style='text-align: center;'>🏗️ מחולל דוחות פיקוח עליון</h1>", unsafe_allow_html=True)

# פרטים
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
author_initials = st.text_input("ראשי תיבות של כותב הדוח", value="A.K")

st.header("🚧 מצב העבודה באתר")
work_status = st.text_area("תיאור מצב העבודה הנוכחי באתר:", value="רוב הברזל מורכב במלואו")

st.header("✒️ חתימת המהנדס")
signature_file = st.file_uploader("העלה תמונת חתימה:", type=["png", "jpg", "jpeg"])

st.header("📸 הערות ספציפיות וליקויי סיור")
if 'dynamic_remarks' not in st.session_state:
    st.session_state.dynamic_remarks = [{'text': '', 'image': None}]

for idx, item in enumerate(st.session_state.dynamic_remarks):
    st.write(f"**הערה 4.{idx + 1}**")
    st.session_state.dynamic_remarks[idx]['text'] = st.text_area(f"פירוט ליקוי:", value=item['text'], key=f"text_{idx}", label_visibility="collapsed")
    st.session_state.dynamic_remarks[idx]['image'] = st.file_uploader(f"תמונה ל-4.{idx + 1}:", type=["png", "jpg", "jpeg"], key=f"image_{idx}")
    st.write("---")

if st.button("➕ הוסף הערה ותמונה נוספת"):
    st.session_state.dynamic_remarks.append({'text': '', 'image': None})
    st.rerun()

st.header("📝 הערות וממצאים כלליים")
txts = ["יש להסיר שאריות בטון ישן מתחתית ברזלי הזיון.", "יש לדאוג טרם היציקה שמשטח היציקה נקי.", "יש לשמור על עובי כיסוי עפ\"י התכניות.", "ניתן להמשיך בעבודות לאחר אישור המפקח.", "לשאלות נוספות ניתן לפנות אלינו."]
notes = [st.checkbox(t) for t in txts]

st.header("📨 העתקים")
cc_list = st.text_area("רשימת תפוצה:", value="1. בוריס בקלמן/ישראל קנר – סטאר מהנדסים\n2. ראש צוות - סטאר מהנדסים\n3. מנהל פרויקט\n4. תיק פרויקט\n5. תיק כללי", height=140)

if st.button("🚀 הפק קובץ Word"):
    try:
        doc = DocxTemplate("template.docx")
        rlm = "\u200f"
        
        gen_remarks = [f"{rlm}5.{i+1}.{rlm} {txts[i]}{rlm}" for i, n in enumerate(notes) if n]
        cc_final = [f"{rlm}{line.strip()}{rlm}" for line in cc_list.split('\n') if line.strip()]
        
        spec_remarks = []
        for idx, item in enumerate(st.session_state.dynamic_remarks):
            if item['text'].strip():
                spec_remarks.append({'text': f"{rlm}4.{idx+1}.{rlm} {item['text'].strip()}{rlm}", 
                                     'image': InlineImage(doc, item['image'], width=Inches(2)) if item['image'] else None})

        context = {
            'report_date': report_date, 'project_num': project_num, 'letter_num': letter_num,
            'client_name': client_name, 'contact_person': contact_person, 'client_email': client_email,
            'structure_name': structure_name, 'visit_date': visit_date, 'inspection_subject': inspection_subject,
            'star_present': f"{rlm}{star_present}{rlm}", 'inspector_name': inspector_name,
            'execution_team': execution_team, 'author_initials': author_initials,
            'work_status': "\n".join([f"{rlm}{line}{rlm}" for line in work_status.split("\n")]),
            'signature_image': InlineImage(doc, signature_file, width=Inches(1.875)) if signature_file else None,
            'specific_remarks_list': spec_remarks, 'general_remarks_list': gen_remarks, 'cc_final_list': cc_final_list
        }
        
        doc.render(context)
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        st.success("🎉 הדוח הופק בהצלחה!")
        st.download_button("💾 הורד דוח", bio, f"{project_num}-{letter_num}.docx")
    except Exception as e:
        st.error(f"שגיאה: {e}")

st.markdown("<div class='footer-credit'>נבנה ע\"י אביב קנבל, סטאר מהנדסים</div>", unsafe_allow_html=True)