import json
from datetime import date, timedelta, datetime
from pathlib import Path
from typing import Any
import pandas as pd
import requests

class NAVFetcher:
    """Fetch and cache mutual fund NAV data."""

    def __init__(
        self,
        latest_url: str,
        historical_url: str,
        cache_directory: str | Path,
        timeout: int = 30,
    ) -> None:
        self.latest_url = latest_url
        self.historical_url = historical_url
        self.cache_directory = Path(cache_directory)
        self.timeout = timeout

        self.cache_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _get_cache_path(
        self,
        nav_date: date,
    ) -> Path:
        """Return cache file path for a NAV date."""

        return (
            self.cache_directory
            / f"nav_{nav_date.isoformat()}.json"
        )

    def _build_historical_url(
        self,
        nav_date: date,
    ) -> str:
        """Build the historical NAV URL for a given date."""

        return self.historical_url.format(
            date=nav_date.isoformat()
        )

    def _fetch_url(
        self,
        url: str,
    ) -> Any:
        """Fetch JSON data from a URL."""

        response = requests.get(
            url,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()

    def _save_data(
        self,
        data: Any,
        file_path: Path,
    ) -> None:
        """Save data as JSON."""

        with file_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

    def _load_data(
        self,
        file_path: Path,
    ) -> Any:
        """Load data from a JSON file."""

        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def get_latest_nav_date(
        self,
        data: dict[str, Any],
    ) -> date:
        """Extract the latest NAV date from the response."""

        nav_dates = []

        for data_group in data.get("data", []):
            for category in data_group.get("categories", []):
                for group in category.get("groups", []):
                    for scheme in group.get("schemes", []):
                        scheme_date = scheme.get("date")

                        if scheme_date:
                            nav_dates.append(
                                datetime.strptime(
                                    scheme_date,
                                    "%d-%b-%Y",
                                ).date()
                            )

        if not nav_dates:
            raise ValueError("No NAV dates found.")

        return max(nav_dates)

    def get_latest_nav(self) -> Any:
        """Get latest NAV using today's cache file."""

        today = date.today()

        cache_path = self.cache_directory / (
            f"nav_{today.isoformat()}.json"
        )

        if cache_path.exists():
            print(f"Using cached latest NAV: {today}")
            return self._load_data(cache_path)

        print("Fetching latest NAV...")

        data = self._fetch_url(self.latest_url)

        self._save_data(data, cache_path)

        return data

    def get_historical_nav(
        self,
        nav_date: date,
    ) -> Any:
        """Get NAV data for a specific date using the cache."""

        cache_path = self._get_cache_path(nav_date)

        if cache_path.exists():
            print(f"Using cached NAV: {nav_date}")

            return self._load_data(cache_path)

        url = self._build_historical_url(nav_date)

        print(f"Fetching NAV for {nav_date}...")

        data = self._fetch_url(url)

        self._save_data(data, cache_path)

        return data

    def get_comparison_dates(
        self
    ) -> dict[str, date]:
        """Calculate dates required for NAV comparisons."""

        today= date.today()

        return {
            "previous": today - timedelta(days= 1),
            "weekly": today - timedelta(days=7),
            "monthly": today - timedelta(days=30),
            "quarterly": today - timedelta(days=90),
            "yearly": today - timedelta(days=365),
        }

    def _get_previous_cache_date(
        self,
        latest_nav_date: date,
    ) -> date:
        """Find the most recent cached NAV before latest NAV date."""

        cache_files = list(
            self.cache_directory.glob("nav_*.json")
        )

        available_dates = []

        for file_path in cache_files:
            date_string = file_path.stem.replace(
                "nav_",
                "",
            )

            file_date = date.fromisoformat(date_string)

            if file_date < latest_nav_date:
                available_dates.append(file_date)

        if not available_dates:
            raise ValueError(
                "No previous NAV data available in cache."
            )

        return max(available_dates)

    def get_comparison_data(
        self
    ) -> dict[str, Any]:
        """Get NAV data for all comparison periods."""

        dates = self.get_comparison_dates()

        return {
            "previous": self.get_historical_nav(
                dates["previous"]
            ),
            "weekly": self.get_historical_nav(
                dates["weekly"]
            ),
            "monthly": self.get_historical_nav(
                dates["monthly"]
            ),
            "quarterly": self.get_historical_nav(
                dates["quarterly"]
            ),
            "yearly": self.get_historical_nav(
                dates["yearly"]
            ),
        }

    def get_processed_data(self, data) -> pd.DataFrame:
        """Extract all scheme records into a DataFrame."""
        schemes = []

        for data_group in data.get("data", []):
            for category in data_group.get("categories", []):
                for group in category.get("groups", []):
                    schemes.extend(group.get("schemes", []))

        return pd.DataFrame(schemes)