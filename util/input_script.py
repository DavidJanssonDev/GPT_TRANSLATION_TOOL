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



# ---------------- INPUTCLASS ---------------- #

@dataclass
class InputData:
    """
    Container for storing input data and related metadata

    Args: 
        dataFile    (DataFrame | None): Loaded DataFrame when reading a CSV file.
        dataPath    (str       | None): The Path of selected file or folder.
        cancelInput (            bool): Indicates if the input was canceled.
        erroring    (Exception | None): Holds error information if any occurred.

    Return: 
        None 
    """
    dataFile: DataFrame | None
    dataPath: str | None
    cancelInput: bool   = False 
    erroring: Exception | None = None

# ----------------   Enum     ---------------- #

class InputTypeEnum(StrEnum):
    """
    Enum for defining the type of input

    Args:
        Folder: Indicates a folder selection.
        File: Indicates a file selection
    
    Return:
        None
    """
    Folder = "folder"
    File = "File"

# ---------------- Validators ---------------- #

class FileValidator(Validator):
    """
    Validator for ensuring a valid file path with correct extensions.

    Args:
        Validator (list[str] | None): List of allowed extentions

    """
    
    def __init__(self, extensions: list[str] | None = None) -> None:
        super().__init__()
        

        self.extensions = [f".{ext.lower().split(".")[1]}" for ext in extensions or []]

    def validate(self, document: Document) -> None:
        """

        Validator for ensuring a valid file path with correct extensions.

        Args:
            document (Document): The document containing the input path.

        Raises:
            ValidationError: If path is not enterd 
            ValidationError: File dosent Exist 
            ValidationError: File is not in a vailid extention
        """
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
            for extension in self.extensions:
                if not path.endswith(extension):
                    raise ValidationError(
                        message=f"{self.extensions}",
                        cursor_position=len(document.text or "")
                    )

class FolderValidator(Validator):
    """
    Validator for ensuring a valid folder path is provided.
    """
    def validate(self, document):
        """
        
        Validator for ensuring a valid folder path is provided. 

        Args:
            document (Document):  The document containing the input path.

        Raises:
            ValidationError: If the path is None
            ValidationError: Is the folder dosent exists
        """

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
    """

    Select file path with GUI 

    Args:
        message   (str       ): The message in the console is responding when opening the file system  
        file_type (str | None): the file path

    Returns:
        str | None: The file path to file
    """

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
    """

    Gets a path for a file with questionary

    Args:
        message   (str       ): The message in the console is responding when opening the file system  
        file_type (str | None): the file path

    Returns:
        str | None: The file path to file
    """
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
    """
    
    Selects the folder that

    Args:
        message (str): _description_

    Returns:
        str | None: _description_
    """
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
    """
    
    Select what fucntion that is needed

    Args:
        message (str): _description_
        type_of_input_choices (list[str]): _description_
        type_of_input (InputTypeEnum): _description_
        type_input_dict (
            dict[
                InputTypeEnum,
                tuple[FileFunctionType, FileFunctionType]  |  
                tuple[FolderFunctionType, FolderFunctionType] 
                ]
            ): THe dict that holds the correct function

    Returns:
        FileFunctionType | FolderFunctionType | None: Retuns the choisce of function or none for what the user use to do
    """
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
    
    ConsoleClass.printing(type_of_input)
    ConsoleClass.printing(f"IS FILE: {type_of_input is InputTypeEnum.File}")
    ConsoleClass.printing(f"IS FILE: {type_of_input is InputTypeEnum.Folder}")
    # IF the function was a FileType
    if type_of_input is InputTypeEnum.File:
        
        path: str | None = cast(FileFunctionType, type_of_function)(message, type_of_file)

        if path is None: 
            return InputData(None, path, cancelInput=True, erroring=FileExistsError("No File Selected")) 
        
        try:    

            dataFrame: DataFrame = read_csv(path)
        except Exception as Error:
            return InputData(None,path, erroring= Error) 

        return InputData(dataFrame, path) 
    
    
    
    elif type_of_input is InputTypeEnum.Folder:
        
        path: str | None = cast(FolderFunctionType, type_of_function)(message)

        if path is None:
            return InputData(None,path, cancelInput=True, erroring=FileExistsError("No Folder Selected")) 
        
        return InputData(None, path)

    
    raise SystemError("something went wrong")

    





if __name__ == "__main__":
    # quick standalone test for folder selection
    folder = path_input("Select CSV File",InputTypeEnum.File, "*.csv")
    if folder is None:
        print("❌ User canceled.")
    else:
        print(f"✅ Selected folder: {folder}")
    



