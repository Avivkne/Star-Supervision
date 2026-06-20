# כפתור הפקה
if st.button("🚀 הפק קובץ Word"):
    try:
        doc = DocxTemplate("template.docx")
        
        # תו סמוי לכפיית כיווניות ימין לשמאל (RLM)
        rlm = "\u200f"
        
        # בניית רשימת הערות כלליות (חלק 5) כטקסט נקי עם RLM
        general_remarks_list = []
        general_counter = 1
        if note1: 
            general_remarks_list.append(f"{rlm}5.{general_counter}. {txt1}")
            general_counter += 1
        if note2: 
            general_remarks_list.append(f"{rlm}5.{general_counter}. {txt2}")
            general_counter += 1
        if note3: 
            general_remarks_list.append(f"{rlm}5.{general_counter}. {txt3}")
            general_counter += 1
        if note4: 
            general_remarks_list.append(f"{rlm}5.{general_counter}. {txt4}")
            general_counter += 1
        if note5: 
            general_remarks_list.append(f"{rlm}5.{general_counter}. {txt5}")
            general_counter += 1

        # בניית רשימת העתקים כטקסט נקי עם RLM בתחילת כל שורה
        cc_final_list = []
        for line in cc_list.split('\n'):
            if line.strip():
                cc_final_list.append(f"{rlm}{line.strip()}")

        # עיבוד חלק 4
        specific_remarks_list = []
        for idx, item in enumerate(st.session_state.dynamic_remarks):
            current_num = f"4.{idx + 1}"
            if item['text'].strip():
                remark_data = {
                    'text': f"{rlm}{current_num}. {item['text'].strip()}",
                    'image': None
                }
                if item['image'] is not None:
                    remark_data['image'] = InlineImage(doc, item['image'], width=Inches(2))
                specific_remarks_list.append(remark_data)

        # יצירת ה-context המאוחד
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
            'star_present': star_present,
            'inspector_name': inspector_name,
            'execution_team': execution_team,
            'author_initials': author_initials,
            'specific_remarks_list': specific_remarks_list,
            'general_remarks_list': general_remarks_list,
            'cc_final_list': cc_final_list
        }

        doc.render(context)
        
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        
        # קיצור סוג ה-MIME למניעת חיתוך שורות ארוכות
        ms_word_mime = "application/octet-stream"
        
        st.success("🎉 הדוח הופק בהצלחה!")
        st.download_button(
            label="💾 הורד קובץ Word מוכן",
            data=bio,
            file_name=f"{project_num}-{letter_num}.docx",
            mime=ms_word_mime
        )
    except FileNotFoundError:
        st.error("שגיאה: קובץ התבנית 'template.docx' לא נמצא באותה תיקייה.")
    except Exception as e:
        st.error(f"התרחשה שגיאה: {str(e)}")

# חתימת קרדיט
st.markdown("<div class='footer-credit'>נבנה ע\"י אביב קנבל, סטאר מהנדסים</div>", unsafe_allow_html=True)
