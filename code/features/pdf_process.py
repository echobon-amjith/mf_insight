import pandas as pd
import pdfplumber, re

class MFtable:

    def __init__(self, pdf_path: str, passw: str | None = None):
        self.pdf_path = pdf_path
        self.password = passw
        self.pdf = pdfplumber.open(
            self.pdf_path,
            password=self.password
        )

    def _close(self):
        self.pdf.close()

    def _find_keyword_pages(
            self,
            pdf,
            keyword: str
    ) -> list[int]:
        keyword_pages = []
        for page_number, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if keyword in text:
                keyword_pages.append(page_number)

        return keyword_pages

    def extract_value(self, pattern: str):
        page_n= self._find_keyword_pages(self.pdf, "ISIN")
        extracted_value=[]

        for page_i in page_n:
            page = self.pdf.pages[page_i]
            text = page.extract_text() or ""

            isin_values = re.findall(pattern, text)
            for value in isin_values:
                value= re.sub(r"\s+", "", value)
                extracted_value.append(value)

        return extracted_value

    def pofo_overview(self):
        isin_pattern= r"ISIN: \s*((?:[A-Z0-9]\s*){12})"
        unit_pattern= r"Closing Unit Balance:\s*(\d{1,3}(?:,\d{3})*\.\d+|\d*\.\d+)"
        cost_pattern= r"Total Cost Value:\s*(\d{1,3}(?:,\d{3})*\.\d+|\d*\.\d+)"
        isin= self.extract_value(pattern= isin_pattern)
        units= self.extract_value(pattern= unit_pattern)
        cost_value= self.extract_value(pattern= cost_pattern)

        df= pd.DataFrame({
            'ISIN':isin,
            'Unit Balance':units,
            'Cost Value': cost_value
        })
        num_columns= ["Unit Balance", "Cost Value"]

        # Strip out commas across all numeric columns
        df[num_columns] = df[num_columns].replace("," , "",regex=True)

        # Convert all 3 columns to float
        df[num_columns] = df[num_columns].apply(pd.to_numeric)

        self._close()

        return df










