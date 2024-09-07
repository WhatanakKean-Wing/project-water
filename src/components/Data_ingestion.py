import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

class DataIngestion:
    # Class variable: Station codes
    LOWER_MEKONG_STATION_CODES = {
        "STR": "Stung Treng", 
        "KRA": "Kratie",
        "KOM": "Kompong Cham",
        "PPB": "Phnom Penh (Bassac)",
        "PPP": "Phnom Penh Port",
        "KOH": "Koh Khel (Bassac)",
        "NEA": "Neak Luong",
        "PRE": "Prek Kdam (Tonle Sap)",
        "TCH": "Tan Chau",
        "CDO": "Chau Doc (Bassac)"
    }

    def __init__(self, station_code):
        if station_code not in self.LOWER_MEKONG_STATION_CODES:
            raise ValueError(f"Invalid station code. Choose from: {list(self.LOWER_MEKONG_STATION_CODES.keys())}")
        self.station_code = station_code
        self.station_name = self.LOWER_MEKONG_STATION_CODES[station_code]
        self.df = None  # DataFrame to store fetched data

    def get_data(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        BASE_URL = "http://ffw.mrcmekong.org/fetchwet_st.php?StCode="
        r = requests.get(BASE_URL + self.station_code, headers=headers)
        soup = BeautifulSoup(r.content, 'lxml')
        body = soup.find('body')
        data_string = body.text

        # Replace non-JSON parts
        data_string = data_string.replace('date_gmt:', '"date_gmt":')
        data_string = data_string.replace('Max:', '"Max":')
        data_string = data_string.replace('Min:', '"Min":')
        data_string = data_string.replace('AVG:', '"AVG":')
        data_string = data_string.replace('floodLevel:', '"floodLevel":')
        data_string = data_string.replace('alarmLevel:', '"alarmLevel":')


        for year in range(1992, 2025):
            data_string = data_string.replace(f'{year}:', f'"{year}":')
        data_string = data_string.replace(',]', ']')
        data = json.loads(data_string)
        self.df = pd.DataFrame(data)
        self.df['date_gmt'] = self.df['date_gmt'].apply(lambda x: x.split("-")[1] + "-" + x.split("-")[2])
        self.df.to_csv('../data/data.csv')
        self.df['station'] = self.station_name

        return self.df