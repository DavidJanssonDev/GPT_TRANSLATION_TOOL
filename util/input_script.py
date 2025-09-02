from dataclasses import dataclass
from typing import Optional, cast
from easygui import fileopenbox
from pandas import DataFrame, read_csv
from rich import inspect
from .console_stuff import ConsoleClass

@dataclass
class InputData:
    dataFile: DataFrame | None
    cancelInput: bool   = False 
    erroring: Exception | None = None


def input_csv_type() -> InputData :

    dataFileContent: DataFrame
    
    choice = fileopenbox(
        msg="Select a CSV file",
        multiple=False        
    )

    file_path: Optional[str] = cast(Optional[str], choice)

    if file_path is None:
        ConsoleClass.printing("No File Selected")
        return InputData(None, erroring = FileExistsError("No File Selected"))

    if not file_path.lower().endswith(".csv"):
        ConsoleClass.printing("File is not .csv type")
        return InputData(None, erroring = TypeError("Not The Correct Selected Type"))


    try:
        dataFileContent = read_csv(file_path)
    except Exception as error:
        ConsoleClass.printing("[yellow]No CSV file provided[/]")
        return InputData(None, erroring=error)


    return InputData(dataFileContent) 





if __name__ == "__main__":
    csv_input: InputData = input_csv_type()

    inspect(csv_input)
    # 

    



