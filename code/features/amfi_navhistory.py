from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from pathlib import Path
from typing import Any
import requests, json, pandas as pd, holidays

class NAVFetcher:
    def __init__(
            self,
            url:str,
            cache_directory: str | Path,
            timeout: int = 30
            ):
        self.url = url
        self.timeout = timeout
        self.cache_directory = Path(cache_directory)
        current_year = date.today().year
        self.in_holidays= holidays.India(years=[current_year - 1, current_year])

    def _get_cache_path(self, nav_date: date) -> Path:
        return (
            self.cache_directory / f"nav_{nav_date.isoformat()}.json"
        )

    def _build_url(self, nav_date: date) -> str:
        return self.url.format(date= nav_date.isoformat())

    def _fetch_from_url(self, url: str) -> Any:
        response = requests.get(url, timeout= self.timeout)
        response.raise_for_status()

        return response.json()

    def _save_data(self, data: Any, file_path: Path) -> None:
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii= False)

    def _load_data(self, file_path: Path) -> Any:
        with file_path.open("r", encoding= "utf-8") as file:
            return json.load(file)

    def get_latest_nav(self, nav_date: date) -> Any:

        cache_path = self._get_cache_path(nav_date)

        if cache_path.exists():
            print("Using cached data")
            return self._load_data(cache_path)

        url= self._build_url(nav_date)

        data = self._fetch_from_url(url)
        self._save_data(data, cache_path)

        return data

    def get_processed_data(self, data) -> pd.DataFrame:
        """Extract all scheme records into a DataFrame."""
        schemes = []

        for data_group in data.get("data", []):
            for scheme in data_group.get("schemes", []):
                    schemes.extend(scheme.get("navs", []))

        return pd.DataFrame(schemes)

    def _nearest_business_day(self, target_date:date) -> date:

        while(
            target_date.weekday() >= 5
            or target_date in self.in_holidays
            ):
            target_date -= timedelta(days= 1)

        return target_date

    def past_business_dates(self,target_date, timeframe: str) -> date:
        latest_day = self._nearest_business_day(target_date)

        if timeframe == "latest":
            past_date = latest_day

        elif timeframe == "day":
            past_date = latest_day - timedelta(days=1)

        elif timeframe == "week":
            past_date = latest_day - timedelta(weeks=1)

        elif timeframe == "month":
            past_date = latest_day - relativedelta(months= 1)

        elif timeframe == "quarter":
            past_date = latest_day - relativedelta(months=3)

        elif timeframe == "year":
            past_date = latest_day - relativedelta(years= 1)

        else:
            raise ValueError(
                "Invalid timeframe. Use 'latest', 'day', 'week', 'month', 'quarter' or 'year'"
            )

        past_business_day = self._nearest_business_day(past_date)

        return past_business_day



