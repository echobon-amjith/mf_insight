import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
import pandas as pd
import requests


class NAVFetcher:
    """Fetch and locally cache daily mutual fund data."""

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
        self.cache_directory.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, nav_date: date) -> Path:
        """Return the cache file path for a NAV date."""

        return (
            self.cache_directory
            / f"nav_{nav_date.isoformat()}.json"
        )

    def _fetch_from_url(self, url: str) -> Any:
        """Fetch JSON data from the URL."""
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()

        return response.json()

    def _save_data(self, data: Any, file_path: Path) -> None:
        """Save data as a JSON file."""
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def _load_data(self, file_path: Path) -> Any:
        """Load data from a local JSON file."""
        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    
    def get_latest_nav(self, latest_date: date) -> Any:
        """Get latest NAV, using the daily cache when available."""
        today = date.today()

        cache_path = self._get_cache_path(latest_date)

        if cache_path.exists():
            print("Using cached data")
            return self._load_data(cache_path)

        print("Fetching latest NAV...")

        data = self._fetch_from_url(self.latest_url)
        self._save_data(data, cache_path)

        return data

    def get_historical_nav(self, nav_date: date) -> Any:
        """Get NAV for a specific date, using the local cache when available."""
        cache_path = self._get_cache_path(nav_date)

        if cache_path.exists():
            print(f"Using cached NAV for {nav_date}.")
            return self._load_data(cache_path)

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

from datetime import date, timedelta
from typing import Any


class MutualFundNAVAnalyzer:
    """Analyse NAV movements across different periods."""

    def __init__(self, fetcher: MutualFundNAVFetcher) -> None:
        self.fetcher = fetcher

    def get_comparison_data(
        self,
        latest_data: dict[str, Any],
        latest_date: date,
    ) -> dict[str, Any]:
        """Get NAV data required for performance comparisons."""

        previous_date = self._get_previous_date(latest_date)
        weekly_date = self._get_weekly_date(latest_date)
        monthly_date = self._get_monthly_date(latest_date)

        previous_data = self.fetcher.get_historical_nav(
            previous_date
        )

        weekly_data = self.fetcher.get_historical_nav(
            weekly_date
        )

        monthly_data = self.fetcher.get_historical_nav(
            monthly_date
        )

        return {
            "latest": latest_data,
            "previous": previous_data,
            "weekly": weekly_data,
            "monthly": monthly_data,
        }

    def _get_previous_date(
        self,
        latest_date: date,
    ) -> date:
        """Return the date to use for previous NAV."""
        return latest_date - timedelta(days=1)

    def _get_weekly_date(
        self,
        latest_date: date,
    ) -> date:
        """Return the date one week before latest NAV."""
        return latest_date - timedelta(days=7)

    def _get_monthly_date(
        self,
        latest_date: date,
    ) -> date:
        """Return the date one month before latest NAV."""
        return latest_date - timedelta(days=30)



class MutualFundNAVAnalyzer:
    """Analyse NAV movements across different periods."""

    def __init__(
        self,
        fetcher: MutualFundNAVFetcher,
        maximum_lookback_days: int = 10,
    ) -> None:
        self.fetcher = fetcher
        self.maximum_lookback_days = maximum_lookback_days

    def find_previous_nav(
        self,
        latest_date: date,
    ) -> tuple[date, dict[str, Any]]:
        """Find the most recent available NAV before latest_date."""

        candidate_date = latest_date - timedelta(days=1)

        for _ in range(self.maximum_lookback_days):
            try:
                data = self.fetcher.get_historical_nav(candidate_date)

                actual_date = self.fetcher.get_latest_nav_date(data)

                if actual_date < latest_date:
                    return actual_date, data

            except ValueError:
                pass

            candidate_date -= timedelta(days=1)

        raise ValueError(
            "Could not find a previous NAV within the lookback period."
        )

    def get_nav_comparison(
        self,
    ) -> dict[str, Any]:
        """Get latest, previous, weekly and monthly NAV data."""

        latest_data = self.fetcher.get_latest_nav()

        latest_date = self.fetcher.get_latest_nav_date(
            latest_data
        )

        previous_date, previous_data = self.find_previous_nav(
            latest_date
        )

        return {
            "latest_date": latest_date,
            "latest_data": latest_data,
            "previous_date": previous_date,
            "previous_data": previous_data,
        }



class MutualFundNAVFetcher:
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

    def get_latest_nav(
        self,
        latest_date: date,
    ) -> Any:
        """Get latest NAV using today's cache when available."""

        cache_path = self._get_cache_path(latest_date)

        if cache_path.exists():
            print(f"Using cached latest NAV: {latest_date}")

            return self._load_data(cache_path)

        data = self._fetch_url(self.latest_url)

        self._save_data(
            data,
            cache_path,
        )

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

        date_string = nav_date.strftime("%d-%m-%Y")

        print(f"Fetching NAV for {nav_date}...")

        data = self._fetch_url(url)

        self._save_data(data, cache_path)

        return data

    def get_comparison_dates(
        self,
        latest_nav_date: date,
    ) -> dict[str, date]:
        """Calculate dates required for NAV comparisons."""

        return {
            "previous": self._get_previous_cache_date(latest_nav_date),
            "weekly": latest_nav_date - timedelta(days=7),
            "monthly": latest_nav_date - timedelta(days=30),
            "quarterly": latest_nav_date - timedelta(days=90),
            "yearly": latest_nav_date - timedelta(days=365),
        }
    
    def _get_previous_cache_date(
        self,
        latest_nav_date: date,
    ) -> date:
        """Find the most recent cached NAV before latest NAV date."""

        cache_files = list(
            self.fetcher.cache_directory.glob("nav_*.json")
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
        self,
        latest_nav_date: date,
    ) -> dict[str, Any]:
        """Get NAV data for all comparison periods."""

        dates = self.get_comparison_dates(latest_nav_date)

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
            )
        }
    
    def get_processed_data(self) -> pd.DataFrame:
        """Extract all scheme records into a DataFrame."""
        schemes = []
        data = self.get_data()

        for data_group in data.get("data", []):
            for category in data_group.get("categories", []):
                for group in category.get("groups", []):
                    schemes.extend(group.get("schemes", []))

        return pd.DataFrame(schemes)

    from datetime import date
from typing import Any


def get_latest_nav(self) -> Any:
    """Get latest NAV using today's cache file."""

    today = date.today()

    cache_path = self.cache_directory / (
        f"latest_{today.isoformat()}.json"
    )

    if cache_path.exists():
        print(f"Using cached latest NAV: {today}")
        return self._load_data(cache_path)

    print("Fetching latest NAV...")

    data = self._fetch_url(self.latest_url)

    self._save_data(data, cache_path)

    return data