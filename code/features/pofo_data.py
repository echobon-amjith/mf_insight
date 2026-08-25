import pandas as pd
from features.pdf_process import MFtable
import pdfplumber
from features.amfi_navhistory import  NAVFetcher
from datetime import date, timedelta

class MFdata:

    def __init__(self,fetcher: NAVFetcher, pdf_path: str, passw: str | None = None):
        self.pdf_path = pdf_path
        self.password = passw
        self.fetch= fetcher
        self.pdf = pdfplumber.open(
            self.pdf_path,
            password=self.password
        )

    def mf_nav_fetch(self, target_date: date= date.today()-timedelta(days=1)):
        nav_data = self.fetch.get_latest_nav(self.fetch._nearest_business_day(target_date))
        nav_df= self.fetch.get_processed_data(nav_data)
        nav_df["ISIN"]=nav_df["ISIN_RI"] + nav_df["ISIN_PO"]

        return nav_df

    def get_pofo_value(self, 
                    #    lookup_columns:list = ["schemeName", "category", "ISIN", "date", "netAssetValue"]
                       lookup_columns:list = ["NAV_Name", "ISIN", "hNAV_Date", "hNAV_Amt"]
                       ):
        pdf= MFtable(self.pdf_path, self.password)
        nav_df= pdf.mfc_table_df()
        lookup_latest_nav_df = self.mf_nav_fetch()
        nav_pf_data= nav_df.merge(
            lookup_latest_nav_df[lookup_columns],
            on= "ISIN",
            how= "left"
        )

        num_columns= ["hNAV_Amt"]

        # Strip out commas across all numeric columns
        nav_pf_data[num_columns] = nav_pf_data[num_columns].replace("," , "",regex=True)

        # Convert all 3 columns to float
        nav_pf_data[num_columns] = nav_pf_data[num_columns].apply(pd.to_numeric)

        return nav_pf_data

    def get_processed_pofo_data(self,df_columns:list =["Scheme Name", "Cost Value", "Date", "NAV", "Market Value", "Gain", "Gain %", "All-Portfolio %"]):
        data= self.get_pofo_value()
        # data.rename(columns={"schemeId": "Scheme ID", "schemeName": "Scheme Name", "category": "Category", "date": "Date", "netAssetValue": "NAV"},inplace= True)
        data.rename(columns={"schemeId": "Scheme ID", "NAV_Name": "Scheme Name", "category": "Category", "hNAV_Date": "Date", "hNAV_Amt": "NAV"},inplace= True)

        data["Date"] = pd.to_datetime(data["Date"])
        data["Date"]= data["Date"].dt.strftime('%Y-%m-%d')
        data["Market Value"]= data["Unit Balance"]*data["NAV"]
        data["Gain"]= data["Market Value"]-data["Cost Value"]
        data["Gain %"]= (data["Gain"]/data["Cost Value"])*100
        data["All-Portfolio %"]= (data["Market Value"]/sum(data["Market Value"]))*100

        return data[df_columns]



    




