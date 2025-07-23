import streamlit as st
from streamlit_main import main
import pdfplumber
from convert_to_pdf import convert_all_docs_in_folder
import os
from data_processing import add_vectors

st.title("Query Chatbot")
# st.subheader("Job Description Based Search")
# jd_input = st.text_area("Paste Job Description here:", height=300, key='jd_text_input')

st_query = st.text_input("Enter your Query",key = 'key1')
k = st.slider('How many results you want :',1,20,5)
user_query = st_query.lower()


# For JD search
# if st.button("Search by Job Description"):
#     if jd_input:
#         zip_buffer = main(k=k, user_query=jd_input, is_jd_search=True) 
#     else:
#         st.warning("Please paste a Job Description to search.")
# elif (user_query != "") and (user_query != " "):
#     zip_buffer = main(k, user_query)
# else:
#     zip_buffer = None 

uploading_files = st.file_uploader("Attach",accept_multiple_files=True,type=['pdf','doc','docx'])
if uploading_files:
    print(uploading_files)
    if st.button("Upload File"):
        resume_data =''
        for uploading_file in uploading_files:
            with open('resumes/'+uploading_file.name, "wb") as f:
                f.write(uploading_file.getbuffer())
            add_vectors()
            st.success(f"Uploaded: {uploading_file.name}")
    else:
        st.info("Click the button above to upload the file.")

if user_query!= "" and user_query != " ":
    zip_buffer = main(k,user_query)
    if zip_buffer is not None:
        st.download_button(
            label="Download Selected Resumes",
            data=zip_buffer,
            file_name="resumes.zip",
            mime="application/zip"
        )
