import os, requests, pandas as pd
NOAA_TOKEN = os.environ.get("NOAA_TOKEN")

def fetch_noaa_station_data(station_id, start_date, end_date, dataset="daily-summaries"):
    if not NOAA_TOKEN:
        raise RuntimeError("Set NOAA_TOKEN env var to use NOAA API.")
    url = "https://www.ncei.noaa.gov/access/services/data/v1"
    params = {
        "dataset": dataset,
        "stations": station_id,
        "startDate": start_date,
        "endDate": end_date,
        "format": "json",
        "includeAttributes": "false",
        "includeStationName": "false"
    }
    headers = {"token": NOAA_TOKEN}
    r = requests.get(url, params=params, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame.from_records(data)
    # Basic cleaning: keep numeric-like columns only and rename to expected if present
    return df
