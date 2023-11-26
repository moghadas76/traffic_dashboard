
import json
import os
import pandas as pd


class JsonToPandas:

    def __init__(self, json_file_path: str):
        """
        Initialize the object with the given JSON file path.

        Parameters:
            json_file_path (str): The path to the JSON file.

        Returns:
            None
        """
        self._check_if_file_exists(json_file_path)
        self.json_file_path = json_file_path

    def _check_if_file_exists(self, json_file_path: str):
        if not os.path.isfile(json_file_path):
            raise FileNotFoundError("BasicTS can not find data file {0}".format(json_file_path))

    def load(self):
        df = pd.read_json(self.json_file_path)
        return df
    
    def load_json(self):
        with open(self.json_file_path) as f:
            data = json.load(f)
        return data
    
    def to_dataframe(self):
        df = self.load()
        return df
    
    @staticmethod
    def bulk_load(json_file_path: list):
        dfs = []
        for path in json_file_path:
            df = JsonToPandas(path).to_dataframe()
            dfs.append(df)
        dfs = JsonToPandas.merge_dataframes(*dfs)
        return dfs
    
    def append_to_dataframe(self, df1, file_path):
        df = pd.read_json(file_path)
        df = self.merge_dataframes(df, df1)
        return df

    @classmethod
    def merge_dataframes(self, *df1):
        df = pd.concat(df1)
        return df
    
    def merge_dataframes(self, *df1):
        df = pd.concat(df1)
        return df
    
    def save_as_paraquet(self, df, parquet_file_path: str):
        df.to_parquet(parquet_file_path)
