import streamlit as st, pandas as pd
from features.amfi_navhistory import NAVFetcher
from features.pofo_data import MFdata
from features.config import URL, CACHE_DIR

st.set_page_config(layout="wide")
st.title("Analyse your Portfolio")

col1, col2 = st.columns(2)
with col1:
    pdf_file= st.file_uploader(label="Upload the Detailed CAS from CAMS", type=["pdf"], max_upload_size= 10)
    option = st.selectbox("Interval",("Daily","Weekly","Monthly","Quarterly", "Yearly"), index=0)
with col2:
    pdf_pass = st.text_input(label= "Enter Password (If encrypted)", type= "password")
   
if st.button(label = "Extract"):
    if pdf_file is not None:
        fetch= NAVFetcher(url= URL, cache_directory= CACHE_DIR)
        proc= MFdata(pdf_path= pdf_file, passw= pdf_pass, fetcher= fetch)
        tab1, tab2, tab3= st.tabs(["Table", "Chart", "Performance"])
        with tab1:
            st.write("### Your Mutual Fund Portfolio")
            if option == "Daily":
                df= proc.get_processed_pofo_data(timeframe= "day")
            elif option == "Weekly":
                df= proc.get_processed_pofo_data(timeframe= "week")
            elif option == "Monthly":
                df= proc.get_processed_pofo_data(timeframe= "month")
            elif option == "Quarterly":
                df= proc.get_processed_pofo_data(timeframe= "quarter")
            elif option == "Yearly":
                df= proc.get_processed_pofo_data(timeframe= "year")
            else:
                raise ValueError(
                    "Invalid timeframe. Use 'Daily', 'Weekly', 'Monthly', 'Quarterly' or 'Yearly'"
                )
            col3, col4, col5 = st.columns(3)
            col3.metric(label= "Current Total Value", value= df["Current Value"].sum().astype(int), delta= f"{((df['Total Gain'].sum())/df['Cost Value'].sum()):.2%}")
            col4.metric(label= "Total Gain",value= df["Total Gain"].sum().astype(int) , delta= df["Gain"].sum().round(2))
            date= df["Date"].unique()[0]
            col5.metric(label= "Latest NAV Date",value= pd.to_datetime(date).strftime("%B %d, %Y"))
            st.write(df.drop(columns=['Date']).sort_values(by="Gain %", ascending= False).set_index("Fund Name"))
            st.metric(label= "Cost Value", value= df["Cost Value"].sum().astype(int))

    else:
        st.warning("Please attach a PDF file first before clicking the button.")