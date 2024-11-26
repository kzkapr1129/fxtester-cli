
from pathlib import Path
import pandas as pd

class Analyzer:
    def __init__(self, config):
        self.config = config
        self.csv_data_path =  Path(self.config['analyze']['csv_data_path'])
        self.csv_encoding = self.config['analyze']['csv_encoding']

    def main(self):
        # 入力ファイル(.csv)の読み込み
        file_list = [file for file in self.csv_data_path.glob("*.csv") if file.is_file()]
        for file in file_list:
            df = pd.read_csv(file, parse_dates=["datetime"], dayfirst=False, encoding=self.csv_encoding, names=["datetime", "open", "high", "low", "close", "volume", "tick"])
            for row in df.itertuples():
                print(row.datetime)