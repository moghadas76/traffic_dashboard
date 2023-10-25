import os
import torch
import pickle
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from dashboard.utils import load_pkl

if os.path.isfile("src/dashboard/assets/metr_la/cached_metr_la_dataframe.pkl"):
    df: pd.DataFrame = pd.read_pickle("src/dashboard/assets/metr_la/cached_metr_la_dataframe.pkl")
else:
    class ForecastingDataset(Dataset):
        """Time series forecasting dataset."""

        def __init__(self, data_file_path: str, index_file_path: str, mode: str, seq_len:int) -> None:
            """Init the dataset in the forecasting stage.

            Args:
                data_file_path (str): data file path.
                index_file_path (str): index file path.
                mode (str): train, valid, or test.
                seq_len (int): the length of long term historical data.
            """

            super().__init__()
            assert mode in ["train", "valid", "test"], "error mode"
            self._check_if_file_exists(data_file_path, index_file_path)
            # read raw data (normalized)
            data = load_pkl(data_file_path)
            processed_data = data["processed_data"]
            self.data = torch.from_numpy(processed_data).float()
            # read index
            self.index = load_pkl(index_file_path)[mode]
            # length of long term historical data
            self.seq_len = seq_len
            # mask
            self.mask = torch.zeros(self.seq_len, self.data.shape[1], self.data.shape[2])

        def _check_if_file_exists(self, data_file_path: str, index_file_path: str):
            """Check if data file and index file exist.

            Args:
                data_file_path (str): data file path
                index_file_path (str): index file path

            Raises:
                FileNotFoundError: no data file
                FileNotFoundError: no index file
            """

            if not os.path.isfile(data_file_path):
                raise FileNotFoundError("BasicTS can not find data file {0}".format(data_file_path))
            if not os.path.isfile(index_file_path):
                raise FileNotFoundError("BasicTS can not find index file {0}".format(index_file_path))

        def __getitem__(self, index: int) -> tuple:
            """Get a sample.

            Args:
                index (int): the iteration index (not the self.index)

            Returns:
                tuple: (future_data, history_data), where the shape of each is L x N x C.
            """

            idx = list(self.index[index])

            history_data = self.data[idx[0]:idx[1]]     # 12
            future_data = self.data[idx[1]:idx[2]]      # 12
            if idx[1] - self.seq_len < 0:
                long_history_data = self.mask
            else:
                long_history_data = self.data[idx[1] - self.seq_len:idx[1]]     # 11

            return future_data, history_data, long_history_data, idx

        def __len__(self):
            """Dataset length

            Returns:
                int: dataset length
            """

            return len(self.index)
        
    validation_dataset = ForecastingDataset(
        data_file_path="src/dashboard/assets/metr_la/data_in12_out12.pkl",
        index_file_path="src/dashboard/assets/metr_la/index_in12_out12.pkl",
        mode="valid",
        seq_len=12
    )
    df = pd.DataFrame()

    validation_data_loader = DataLoader(
        dataset=validation_dataset,
        batch_size=1,
        shuffle=False,
        num_workers=2,
        pin_memory=True,
    )
    for i, (future_data, history_data, long_history_data, idx) in enumerate(validation_data_loader):
        if i<14*24*12:
            df = pd.concat([df, pd.DataFrame(future_data.squeeze(0)[..., [0]].squeeze(-1).numpy())], axis=0)
    date_index = pd.date_range(start ='1-1-2018', periods=len(df) ,freq ='5T')
    df["date"] =  date_index
    df.set_index("date", inplace=True)
    df.to_pickle('src/dashboard/assets/metr_la/cached_metr_la_dataframe.pkl')

print(df.shape, df.index)
assert df is not None