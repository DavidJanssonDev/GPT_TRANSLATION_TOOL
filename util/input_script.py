import os
from dataclasses import dataclass
from prompt_toolkit.document import Document
from questionary import Validator, ValidationError, select, path as Qpath
from easygui import fileopenbox
from pandas import DataFrame, read_csv
from rich import inspect

from .console_stuff import ConsoleClass

@dataclass
class InputData:
    """
    
    """
    dataFile: DataFrame | None
    cancelInput: bool   = False 
    erroring: Exception | None = None



class CSVValidator(Validator):
    def validate(self, document: Document) -> None:
        path = (document.text or "").strip()
        if not path:
            raise ValidationError(message="Please enter a path")
        if not path.lower().endswith(".csv"):
            raise ValidationError(message="Only .csv file doesn't exist.", cursor_position=len(path))
        
        path = os.path.expanduser(path)
        if not os.path.isfile(path):
            raise ValidationError(message="That file doesn't exist.", cursor_position=len(path))


def _ask_for_csv_path() -> None | str:

    while True:
        choice:str = select(
            "Pick a CSV file:",
            choices=["Browse...(EasyGUI)", "Type or paste a path (Questionary)", "Cancel"]
        ).ask()

        if choice in (None, "Cancel"):
            return None

        if choice.startswith("Browse"):

            picked = fileopenbox(
                msg="Select a CSV file",
                title="Select CSV",
                default="*.csv",
                filetypes=["*.csv"],
                multiple=False        
            )

            if picked is None:
                continue

            path = os.path.expanduser(str(picked)).strip()
            if path.lower().endswith(".csv") and os.path.isfile(path):
                return path
            
            ConsoleClass.printing("[yellow] That isn't a .csv file. Try again. [/]")
            continue
        

        typed:str = Qpath(
            "Path to .csv:",
            validate=CSVValidator(),
            only_directories=False
        ).ask()
        if typed:
            return os.path.expanduser(typed.strip())

def input_csv_type() -> InputData:

    file_path = _ask_for_csv_path()

    if file_path is None:
        ConsoleClass.printing("No File Selected")
        return InputData(None, cancelInput=True, erroring=FileExistsError("No File Selected"))
    
    if not file_path.lower().endswith(".csv"):
        ConsoleClass.printing("File is not .csv type")
        return InputData(None, erroring=TypeError("Not The Correct Selected Type"))
    

    try:
        dataFrame: DataFrame = read_csv(file_path)

    except Exception as error:
        ConsoleClass.printing("[yellow] Failed to read the CSV file [/]")
        return InputData(None, erroring=error)
    
    return InputData(dataFrame)


if __name__ == "__main__":
    csv_input: InputData = input_csv_type()
    inspect(csv_input)

    



