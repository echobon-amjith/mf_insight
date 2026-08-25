import streamlit as st
from features.amfi_navhistory import NAVFetcher
from features.pofo_data import MFdata

st.set_page_config(layout="wide")
st.title("Extract your portfolio from CAS")

col1, col2 = st.columns(2)
with col1:
    pdf_file= st.file_uploader(label="Upload the CAS from myCAMS", type=["pdf"], max_upload_size= 10)
    option = st.selectbox("Interval",("Daily","Weekly","Monthly","Quarterly", "Yearly"), index=0)
with col2:
    pdf_pass = st.text_input(label= "Enter Password (If encrypted)", type= "password")
   
if st.button(label = "Extract"):
    if pdf_file is not None:
        fetch= NAVFetcher(url="https://www.amfiindia.com/api/nav-history?query_type=all_for_date&from_date={date}", cache_directory= r"data\daily_cache")
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
                    "Invalid timeframe. Use 'latest', 'day', 'week', 'month', 'quarter' or 'year'"
                )

            col5, col6 = st.columns(2)
            col5.metric(label= "Current Total Value", value= df["Current Value"].sum().astype(int), delta= f"{((df['Total Gain'].sum())/df['Cost Value'].sum()):.2%}")
            col6.metric(label= "Total Gain",value= df["Total Gain"].sum().astype(int) , delta= df["Gain"].sum().round(2))
            st.write(df.sort_values(by="Gain %", ascending= False).set_index("Fund Name"))
            st.metric(label= "Cost Value", value= df["Cost Value"].sum().astype(int))

    else:
        st.warning("Please attach a PDF file first before clicking the button.")