from pathlib import Path

import pandas as pd
import pdfplumber

class table_extract:
    """Extract tables from encrypted or unencrypted PDFs."""

    def __init__(self, pdf_path: str, password: str | None = None):
        self.pdf_path = Path(pdf_path)
        self.password = password

    def table_df(self) -> pd.DataFrame:
        with pdfplumber.open(self.pdf_path,password= self.password) as pdf:
            page = pdf.pages[0]
            bounding_box = (0,round(page.height/4)+39,page.width,page.height)
            cropped_page = page.crop(bounding_box)

            table_settings = {
                "vertical_strategy": "text",
                "horizontal_strategy": "lines"
            }

            table = cropped_page.extract_table(table_settings)
            df= pd.DataFrame(table, columns=['Folio Id', 'ISIN', 'Scheme Name', '','','','Cost Value', 'Unit Balance', 'NAV Date', 'NAV', 'Market Value'])
            clean_df= df.drop(index=df.index[-1], columns=['Folio Id','Scheme Name','','',''])

            return clean_df

    def wh(self):
        with pdfplumber.open(self.pdf_path,password= self.password) as pdf:
            page = pdf.pages[0]

            self.w = page.width
            self.h = page.height

