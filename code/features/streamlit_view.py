import streamlit as st
from features.amfi import NAVFetcher
from features.pofo_data import MFdata

st.title("Extract your portfolio from CAS")

pdf_file= st.file_uploader(label="Upload the CAS from myCAMS", type=["pdf"], max_upload_size= 10)
pdf_pass = st.text_input(label= "Enter Password (If encrypted)", type= "password")

if st.button(label = "Extract"):
    if pdf_file is not None:
        fetch= NAVFetcher(url="https://www.amfiindia.com/api/latest-nav?type=&mfid=all", cache_directory= r"data\daily_cache")
        proc= MFdata(pdf_path= pdf_file, passw= pdf_pass, fetcher= fetch)
        df= proc.get_processed_pofo_data()
        st.write("### Your Mutual Fund Portfolio")
        st.metric(label= "Total Value", value= df["Market Value"].sum().astype(int), delta= df["Gain"].sum().astype(int))
        st.write(df.sort_values(by="Gain %", ascending= False).set_index("Scheme Name"))
        st.metric(label= "Cost Value", value= df["Cost Value"].sum().astype(int))
        st.write(df)

    else:
        st.warning("Please attach a PDF file first before clicking the button.")