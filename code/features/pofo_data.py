import pandas as pd
from features.pdf_process import MFtable
import pdfplumber
from features.amfi_navhistory import NAVFetcher
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

    def _mf_nav_fetch(self, timeframe:str):
        target_date= date.today()-timedelta(days= 1)
        nav_data = self.fetch.get_latest_nav(self.fetch.past_business_dates(target_date, timeframe))
        nav_df= self.fetch.get_processed_data(nav_data)
        nav_df["ISIN"]=nav_df["ISIN_RI"] + nav_df["ISIN_PO"]

        return nav_df

    def get_pofo_value(self,timeframe, lookup_columns:list = ["NAV_Name", "ISIN", "hNAV_Date", "hNAV_Amt"]):
        pdf= MFtable(self.pdf_path, self.password)
        df= pdf.mfc_table_df()
        lookup_latest_nav_df = self._mf_nav_fetch("latest")
        lookup_prev_nav_df = self._mf_nav_fetch(timeframe)
        nav_pf_data= df.merge(
            lookup_latest_nav_df[lookup_columns],
            on= "ISIN",
            how= "left"
        )
        nav_pf_data= nav_pf_data.merge(
            lookup_prev_nav_df[["ISIN","hNAV_Amt"]],
            on= "ISIN",
            how= "left"
        )

        num_columns= ["hNAV_Amt_x","hNAV_Amt_y"]

        # Strip out commas across all numeric columns
        nav_pf_data[num_columns] = nav_pf_data[num_columns].replace("," , "",regex=True)

        # Convert all 3 columns to float
        nav_pf_data[num_columns] = nav_pf_data[num_columns].apply(pd.to_numeric)

        return nav_pf_data

    def col_rename(self, data):
        data.rename(columns={"schemeId": "Scheme ID", "NAV_Name": "Fund Name", "category": "Category", "hNAV_Date": "Date", "hNAV_Amt_x": "Current NAV", "hNAV_Amt_y": "Previous NAV"},inplace= True)

        return data

    def get_processed_pofo_data(self,timeframe,df_columns:list =["Date", "Fund Name", "Cost Value", "Current Value", "All-Portfolio %", "Total Gain", "Gain %", "Gain"]):
        data= self.col_rename(self.get_pofo_value(timeframe))
        data["Date"] = pd.to_datetime(data["Date"])
        data["Date"]= data["Date"].dt.strftime('%Y-%m-%d')
        data["Current Value"]= (data["Unit Balance"]*data["Current NAV"]).round(2)
        data["Gain"]= (data["Current Value"]-(data["Unit Balance"]*data["Previous NAV"])).round(2)
        data["Total Gain"]= (data["Current Value"]-data["Cost Value"]).round(2)
        data["Gain %"]= ((data["Gain"]/data["Cost Value"])*100).round(2)
        data["All-Portfolio %"]= ((data["Current Value"]/sum(data["Current Value"]))*100).round(2)

        return data[df_columns]



    




