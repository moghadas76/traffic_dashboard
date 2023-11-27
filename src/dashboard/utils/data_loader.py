
import json
import os

import pandas as pd
import plotly.express as px
from omegaconf import OmegaConf

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

def load_dataframes():
    """
    Load dataframes from config file and filter out rows where "subtype" is "vehicle".
    This function does not take any parameters.
    Returns the filtered dataframe.
    """
    config = OmegaConf.load("conf/production.yml")
    df = JsonToPandas.bulk_load(config.raw_data_files)
    filter_out = df[df["subtype"] == "counting"]
    locs = pd.DataFrame(filter_out.location.to_list())["coordinates"]
    filter_out["lat"] = locs.str[0]
    filter_out["lang"] = locs.str[1]
    filter_out = filter_out.drop("location", axis=1)
    filter_out = filter_out.drop("source", axis=1)
    return filter_out

def get_plotly_figure(df: pd.DataFrame):
    config = OmegaConf.load("conf/production.yml")
    df['UTC_Time'] = pd.to_datetime(df['_start_timestamp'], utc=True)
    df['local_start_time'] = df['UTC_Time'].dt.tz_convert(config.TZ)
    agg = df[['local_start_time', 'count']].groupby('local_start_time')["count"].agg(["count", "sum"])
    fig = px.line(agg, y=["sum"], title="Aggregated Traffic Count")
    fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label="1d",
                     step="day",
                     stepmode="backward"),
                dict(count=1,
                     label="1m",
                     step="month",
                     stepmode="backward"),
                dict(count=6,
                     label="6m",
                     step="month",
                     stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
    )
    fig.update_layout(
        title_text="Sum of Counts"
    )
    return fig
