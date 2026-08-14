import streamlit as st
from features.pdf_process import pdf_table_df

st.title("Extract your portfolio from CAS")

pdf_file= st.file_uploader(label="Upload the CAS from myCAMS", type=["pdf"], max_upload_size= 10)
pdf_pass = st.text_input(label= "Enter Password (If encrypted)", type= "password")

if st.button(label = "Extract"):
    if pdf_file is not None:
        df = pdf_table_df(pdf_file,pdf_pass)
        st.write("### Your Mutual Fund Portfolio")
        st.dataframe(df)
    else:
        st.warning("Please attach a PDF file first before clicking the button.")