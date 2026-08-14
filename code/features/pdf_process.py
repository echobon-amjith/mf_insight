import pandas as pd
import pdfplumber
import streamlit as st

@st.cache_data
def pdf_table_df(pdf_path, passw) -> pd.DataFrame:
    with pdfplumber.open(pdf_path,password= passw) as pdf:
        page = pdf.pages[0]

        # Cropping the page to the required table 
        bounding_box = (0,round(page.height/4)+39,page.width,page.height)
        cropped_page = page.crop(bounding_box)

        # Extracting the required table
        table_settings = {
            "vertical_strategy": "text",
            "horizontal_strategy": "lines"
        }
        table = cropped_page.extract_table(table_settings)

        # Deleting the last row of Total and transforming into a DataFrame
    df= pd.DataFrame(table[:-1])
    # Selecting the ISIN, Cost Value and Unit Balance Columns
    clean_df= df[[1,6,7]]
    clean_df.columns= ['ISIN', 'Cost Value', 'Unit Balance']

    for col in clean_df.columns[1:]:
        clean_df[col] = clean_df[col].str.replace(',','',regex=False)
        clean_df[col] = pd.to_numeric(clean_df[col])

    return clean_df

