import pandas as pd
from tests.pdf_cred import PDF_PATH, PDF_PASS
from features.pdf_process import pdf_table_df

class TestPDF_process:
    """Tests for PDF table extraction."""

    def test_extract_tables_returns_dataframe(self):
        """Verify that extraction returns a DataFrame."""
        dataframe = pdf_table_df(pdf_path= PDF_PATH, passw= PDF_PASS)

        assert isinstance(dataframe, pd.DataFrame)
        assert not dataframe.empty

    def test_extract_tables_has_expected_columns(self):
        """Verify that the expected columns are extracted."""
        dataframe = pdf_table_df(pdf_path= PDF_PATH,passw= PDF_PASS)

        expected_columns = [
            "ISIN",
            "Unit Balance",
            "Cost Value"
        ]

        assert set(expected_columns).issubset(dataframe.columns)
        missing_columns = set(expected_columns) - set(dataframe.columns)
        assert not missing_columns, f"Missing columns: {missing_columns}"

    

