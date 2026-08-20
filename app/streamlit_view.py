import streamlit as st
from features.pdf_process import MFtable

st.title("Extract your portfolio from CAS")

pdf_file= st.file_uploader(label="Upload the CAS from myCAMS", type=["pdf"], max_upload_size= 10)
pdf_pass = st.text_input(label= "Enter Password (If encrypted)", type= "password")

if st.button(label = "Extract"):
    if pdf_file is not None:
        proc= MFtable(pdf_file, pdf_pass)
        df=proc.mfc_table_df()
        df["Market Value"]= df["Unit Balance"]*df["NAV"]
        df["Average NAV"] = df["Cost Value"]/df["Unit Balance"]
        st.write("### Your Mutual Fund Portfolio")
        st.write(df)

    else:
        st.warning("Please attach a PDF file first before clicking the button.")