from enum import StrEnum
import os
from dataclasses import dataclass
from typing import Callable, TypeAlias, cast

from prompt_toolkit.document import Document
from questionary import Validator, ValidationError, select, path as Qpath
from easygui import fileopenbox, diropenbox
from pandas import DataFrame, read_csv

from .console_stuff import ConsoleClass

FileFunctionType: TypeAlias = Callable[[str, str | None], str | None]
FolderFunctionType: TypeAlias = Callable[[str], str | None]



@dataclass
class InputData:
    """
    
    """
    dataFile: DataFrame | None
    PathDat: str | None
    cancelInput: bool   = False 
    erroring: Exception | None = None

# ----------------   Enum     ---------------- #

class InputTypeEnum(StrEnum):
    Folder = "folder"
    File = "File"



# ---------------- Validators ---------------- #
class CSVValidator(Validator):
    def validate(self, document):
        path = (document.text or "").strip()
        if not path:
            raise ValidationError(message="Please enter a path")
        if not path.lower().endswith(".csv"):
            raise ValidationError(
                message="Only .csv files are allowed.",
                cursor_position=len(path),
            )
        path = os.path.expanduser(path)
        if not os.path.isfile(path):
            raise ValidationError(
                message="That file doesn't exist.",
                cursor_position=len(path),
            )

class FileValidator(Validator):
    def __init__(self, extensions: list[str] | None = None) -> None:
        super().__init__()
        self.extensions = [ext.lower() for ext in (extensions or [])]

    def validate(self, document: Document) -> None:
        path = (document.text or "").strip()

        if not path:
            raise ValidationError(message="Please enter a path")
        
        path = os.path.expanduser(path)

        if not os.path.isfile(path):
            raise ValidationError(
                message="That file dosnt't exist.",
                cursor_position=len(document.text or "")
            )
        
        if self.extensions:
            _, ext = os.path.splitext(path)
            if ext.lower() not in self.extensions:
                raise ValidationError(
                    message=f"File must be one of: {', '.join(self.extensions)}",
                    cursor_position=len(document.text or "")
                )

class FolderValidator(Validator):
    def validate(self, document):
        path = (document.text or "").strip()
        if not path:
            raise ValidationError(message="Please enter a path")
        path = os.path.expanduser(path)
        if not os.path.isdir(path):
            raise ValidationError(
                message="That folder doesn't exist.",
                cursor_position=len(path),
            )


# ---------------- File Inputs ---------------- #

def _select_file_path_easygui(message: str, file_type: str | None) -> str | None:
    vaildate_file_types: list[str] | None = [file_type] if file_type is not None else None

    picked_file_path = fileopenbox(
        msg=message,
        title=message,
        filetypes= vaildate_file_types,
        multiple=False
    )

    if picked_file_path is None:
        return None
    
    file_path = os.path.expanduser(str(picked_file_path)).strip()

    if file_path.lower().endswith(file_path) and os.path.isfile(file_path):
        return os.path.normpath(os.path.abspath(file_path))
    
    return None

def _select_file_path_questionary(massage: str, file_type: str | None )-> str | None:
    validate_file_type: list[str] | None  = [file_type] if file_type is not None else None

    picked_file_path: str | None = Qpath(
        massage,
        validate=FileValidator(validate_file_type),
        only_directories=False
    ).ask()

    if picked_file_path is None:
        return None

    return os.path.normpath(os.path.abspath(os.path.expanduser(picked_file_path.strip())))


# ---------------- Folder Inputs ---------------- #

def _select_folder_path_easygui(message: str) -> str | None:
    picked_folder_path: str | None = diropenbox(
        msg=message,
        title=message,
        default=os.path.expanduser("~")
    )

    if picked_folder_path is None:
        return None

    folder_path = os.path.expanduser(str(picked_folder_path)).strip()

    if not os.path.isdir(folder_path):
        return None

    return os.path.normpath(os.path.abspath(folder_path))


def _select_folder_path_questionary(message: str) -> str | None:
    picked_folder_path: str | None = Qpath(
        message,
        validate=FolderValidator(),
        only_directories=True
    ).ask()

    if picked_folder_path is None:
        return None

    return os.path.normpath(os.path.abspath(os.path.expanduser(picked_folder_path))) 


# ----------------    Inputs     ---------------- #

def _selected_type(
        message: str, 
        type_of_input_choices: list[str], 
        type_of_input: InputTypeEnum, 
        type_input_dict: 
            dict[
                InputTypeEnum, 
                tuple[FileFunctionType, FileFunctionType] | 
                tuple[FolderFunctionType, FolderFunctionType]
                ]
        ) -> FileFunctionType | FolderFunctionType | None:
    while True:
        choice: str = select(
            message,
            choices= type_of_input_choices
        ).ask()

        match (choice):

            case "Browse...(EasyGUI)":
                return type_input_dict[type_of_input][0]
            
            case "Type or paste a path (Questionary)":
                return type_input_dict[type_of_input][1]

            case "Cancel":
                return None

            case __:
                return None


def path_input(message: str, type_of_input: InputTypeEnum, type_of_file: str | None) -> InputData:
    
    type_of_function: FileFunctionType | FolderFunctionType | None = _selected_type(
        message,["Browse...(EasyGUI)", "Type or paste a path (Questionary)", "Cancel"],
        type_of_input, 
        { 
            InputTypeEnum.File: (_select_file_path_easygui, _select_file_path_questionary),
            InputTypeEnum.Folder: (_select_folder_path_easygui, _select_folder_path_questionary)
            
        }
    )

    # Takes out so if the the user choice the cancel button it say the input was cancel
    if type_of_function is None:
        text = "No File Selected" if type_of_file is InputTypeEnum.File else "No Folder Selected" 
        return InputData(None,None , cancelInput=True, erroring=FileExistsError(text))

    # IF the function was a FileType
    if type(type_of_function) is FileFunctionType:
        
        path: str | None = cast(FileFunctionType, type_of_function)(message, type_of_file)

        if path is None: 
            return InputData(None, path, cancelInput=True, erroring=FileExistsError("No File Selected")) 
        
        try:    

            dataFrame: DataFrame = read_csv(path)
        except Exception as Error:
            return InputData(None,path, erroring= Error) 

        return InputData(dataFrame, path) 
    
    
    
    elif type(type_of_function) is FolderFunctionType:
        
        path: str | None = cast(FolderFunctionType, type_of_function)(message)

        if path is None:
            return InputData(None,path, cancelInput=True, erroring=FileExistsError("No Folder Selected")) 
        
        return InputData(None, path)

    
    raise SystemError("something went wrong")

    






def _ask_for_output_folder_path() -> None | str:
    while True:
        choice: str = select(
            "Pick an output folder:",
            choices=["Browse...(EasyGUI)", "Type or paste a path (Questionary)", "Cancel"],
        ).ask()

        if choice in (None, "Cancel"):
            return None

        if choice.startswith("Browse"):
            picked = diropenbox(
                msg="Select an output folder:",
                title="Select Output Folder",
                default=os.path.expanduser("~"),
            )
            if picked is None:
                continue
            path = os.path.expanduser(str(picked)).strip()
            if os.path.isdir(path):
                return os.path.normpath(os.path.abspath(path))
            ConsoleClass.printing("[yellow] That isn't a folder. Try again. [/]")
            continue

        typed: str | None = Qpath(
            "Path to folder:",
            validate=FolderValidator(),
            only_directories=True,
        ).ask()
        if typed:
            return os.path.normpath(os.path.abspath(os.path.expanduser(typed.strip())))




if __name__ == "__main__":
    # quick standalone test for folder selection
    folder = _ask_for_output_folder_path()
    if folder is None:
        print("❌ User canceled.")
    else:
        print(f"✅ Selected folder: {folder}")
    



