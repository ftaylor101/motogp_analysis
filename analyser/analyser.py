import pandas as pd
import numpy as np
from typing import List


class Analyser:
    """
    This class performs the analysis of the lap time data extracted from a data source, such as PDFs. It manipulates
    dataframes to find best lap times, best average lap time etc.
    """
    def __init__(self):
        self.__data = None
        self.status = None

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value: pd.DataFrame):
        """
        Set the data to be analysed.

        :param value: The data to be analysed as a DataFrame.
        """
        if not value.empty:
            assert type(value) == pd.DataFrame, f"Expected type DataFrame, was given {type(value)}"
            assert "Riders" in value.columns, "Expected a column named 'Rider'"
            assert "LapTimes" in value.columns, "Expected a column named 'LapTimes'"
            self.__data = value
            print("All is good")
            self.status = "Good"
        else:
            self.status = "Bad. DF was empty or had incorrect column names."

    def unique_riders(self):
        """
        Get a Pandas Series containing the unique rider names for the session under analysis.

        :return:
        """
        return self.__data["Riders"].unique()

    def select_riders(self, selected_riders: List[str]) -> pd.DataFrame:
        """
        Select the given riders from the entire dataframe and format the output for easy plotting.

        :param selected_riders: A list of riders
        :return: A dataframe only containing data for the given riders
        """
        rider_laps = self.__data[self.__data["Riders"].isin(selected_riders)]
        rider_laps["LapNumber"] = 0
        grouped_df = rider_laps.groupby("Riders")

        rider_laps["LapNumber"] = range(1, len(rider_laps) + 1)
        lap_numbers = np.arange(1, len(rider_laps) + 1)

        return rider_laps
