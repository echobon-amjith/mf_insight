import pandas as pd
import pdfplumber

class MFtable:

    def __init__(self, pdf_path: str, passw: str | None = None):
        self.pdf_path = pdf_path
        self.password = passw
        self.pdf = pdfplumber.open(
            self.pdf_path,
            password=self.password
        )

    def cams_table_df(self) -> pd.DataFrame:
        with pdfplumber.open(self.pdf_path,password= self.password) as pdf:
            page = self.pdf.pages[0]

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

    def mfc_table_df(self) :
        tab_pages= self._find_keyword_pages(self.pdf,"Market")

        all_tables=[]

        for page_n in tab_pages:
            table_settings= {
            "vertical_strategy": "explicit",
            "horizontal_strategy": "explicit",
            "explicit_vertical_lines": self._column_lines(page_n),
            "explicit_horizontal_lines": self._exp_horiz_lines(page_n)                
            }
            table= self.pdf.pages[page_n].extract_table(table_settings)
            all_tables.extend(table[1:])

        df= pd.DataFrame(all_tables, columns= ["ISIN", "Scheme Name", "Unit Balance", "NAV", "Cost Value"])
        df= df[(df != "").all(axis=1)]

        num_columns= ["Unit Balance", "NAV", "Cost Value"]

        # Strip out commas across all numeric columns
        df[num_columns] = df[num_columns].replace("," , "",regex=True)

        # Convert all 3 columns to float
        df[num_columns] = df[num_columns].apply(pd.to_numeric) 
            

        self._close()

        return df

    def _add_missing_lines(self,horizontal_lines: list[float], min_distance) -> list[float]:
        """Add horizontal lines when adjacent lines are too far apart."""
        if not horizontal_lines:
            return []

        new_lines = [horizontal_lines[0]]

        for current, next_line in zip(
            horizontal_lines,
            horizontal_lines[1:]
        ):
            distance = next_line - current

            if distance > min_distance:
                number_of_lines = int(distance // min_distance)

                for i in range(1, number_of_lines + 1):
                    new_line = current + i * min_distance

                    if new_line < next_line:
                        new_lines.append(new_line)

            new_lines.append(next_line)

        return sorted(set(new_lines))

    def _exp_horiz_lines(
            self, 
            page_number:int, 
            target: list[str]= ["Market", "Page"]
    ):

        page= self.pdf.pages[page_number]
        slack = {
            "Market": 14,
            "Page": 14,
        }

        horizontal_lines = self._find_text_coordinates(
            page= page,
            axis= "top",
            target_headers= target,
            header_slack= slack      
        )
        explicit_horizontal_lines= self._add_missing_lines(horizontal_lines, min_distance= 29)

        return explicit_horizontal_lines

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

    def _find_text_coordinates(
        self,
        page,
        axis: str,
        target_headers: list[str],
        header_slack: dict[str, float] | None = None
    ) -> list[float]:
        """Find the x1 coordinates of specified column headers."""

        header_slack = header_slack or {}
        words = page.extract_words()

        coordinates = []
        for word in words:
            header = word["text"].strip()

            if header in target_headers:
                slack = header_slack.get(header, 0)
                if axis == "x1":
                    coordinates.append(word[axis] + slack)
                else :
                    coordinates.append(word[axis] - slack)

        return sorted(set(coordinates))

    def _column_lines(
        self,
        page_number: int,
        target_headers: list[str]= ["Folio","ISIN", "Name", "Balance", "NAV", "Cost"
                                    #  "Gain", "Market"
                                     ]
    ):
        """Extract a table using header x-coordinates as vertical lines."""

        page = self.pdf.pages[page_number]
        slack = {
            "Folio": 28,
            "ISIN": 28,
            "Name": 35,
            "Balance" :7 ,
            "NAV": 14,
            "Cost": 14
            # "Gain": 7,
            # "Market": 21
        }

        vertical_lines = self._find_text_coordinates(
            page=page,
            axis="x1",
            target_headers=target_headers,
            header_slack= slack
        )

        return vertical_lines






