from dataclasses import dataclass, field
from typing import Any, cast

from pandas import DataFrame

@dataclass
class CSV_DataHolder:

    data: dict[str, list[Any]] = field(init=False, default_factory=dict)
    headers: list[str]         = field(init=False, default_factory=list)
    data_frame: DataFrame      = field(init=False)

    _file_loaded: bool         = field(init=False, default_factory=bool) 

    _file_input_path: str      = field(init=False, default_factory=str)
    _file_output_path: str      = field(init=False, default_factory=str)


    @classmethod
    def generate_from_data(cls, data_frame:DataFrame)-> "CSV_DataHolder":
        """
        
        Builder för the CSV_DataHolder based on DataFrame

        Args:
            data_frame (DataFrame): The data from the CSV

        Returns:
            CSV_DataHolder: The DataHolder for the information of the csv
       
        """

        if type(data_frame) is not DataFrame:
            raise TypeError("Not the correct type")
        
        self = cls.__new__(cls)
        self.data_frame = data_frame.rename(columns=str)
        self.data = cast(dict[str, list[Any]], data_frame.to_dict(orient="list"))
        self.headers = data_frame.columns.astype(str).tolist()
        return self

