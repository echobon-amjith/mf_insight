import pandas as pd
from tests.pdf_cred import PDF_PATH, PDF_PASS
from features.pdf_process import table_extract

class TestPDF_process:
    """Tests for PDF table extraction."""

    def test_extract_tables_returns_dataframe(self):
        """Verify that extraction returns a DataFrame."""
        extractor = table_extract(pdf_path= PDF_PATH, password= PDF_PASS)

        dataframe = extractor.table_df()

        assert isinstance(dataframe, pd.DataFrame)
        assert not dataframe.empty

    def test_extract_tables_has_expected_columns(self):
        """Verify that the expected columns are extracted."""
        extractor = table_extract(pdf_path= PDF_PATH, password= PDF_PASS)

        dataframe = extractor.table_df()

        expected_columns = [
            "ISIN",
            "Scheme Name",
            "Unit Balance",
            "Cost Value",
            "NAV Date",
            "NAV",
            "Market Value"
        ]

        assert set(expected_columns).issubset(dataframe.columns)
        missing_columns = set(expected_columns) - set(dataframe.columns)
        assert not missing_columns, f"Missing columns: {missing_columns}"

    

