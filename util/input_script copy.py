import os
from enum import StrEnum
from dataclasses import dataclass
from typing import Callable, TypeAlias, cast

from prompt_toolkit.document import Document
from questionary import Validator, ValidationError, select, path as Qpath
from easygui import fileopenbox, diropenbox
from pandas import DataFrame, read_csv

from .console_stuff import ConsoleClass

# Type aliases
FileFunctionType: TypeAlias = Callable[[], str | None]
FolderFunctionType: TypeAlias = Callable[[], str | None]


@dataclass
class InputData:
    """Container for storing input data and related metadata"""
    dataFile: DataFrame | None
    dataPath: str | None
    cancelInput: bool = False
    erroring: Exception | None = None


class InputModeEnum(StrEnum):
    """Enum for defining the type of input"""
    Folder = "folder"
    File = "file"


class FileFolderInput:
    """
    Unified interface for file/folder input with GUI or CLI options.
    """

    # ---------------- Validators ---------------- #

    class FileValidator(Validator):
        def __init__(self, extensions: list[str] | None = None) -> None:
            super().__init__()
            self.extensions = [ext.lower().replace("*","") for ext in (extensions or [])]


        def validate(self, document: Document) -> None:
            path = (document.text or "").strip()
            if not path:
                raise ValidationError(message="Please enter a path")

            path = os.path.expanduser(path)
            if not os.path.isfile(path):
                raise ValidationError(
                    message="That file doesn't exist.",
                    cursor_position=len(document.text or "")
                )

            if self.extensions and not any(path.lower().endswith(ext) for ext in self.extensions):
                raise ValidationError(
                    message=f"File must be one of: {self.extensions}",
                    cursor_position=len(document.text or "")
                )

    class FolderValidator(Validator):
        def validate(self, document: Document) -> None:
            path = (document.text or "").strip()
            if not path:
                raise ValidationError(message="Please enter a path")

            path = os.path.expanduser(path)
            if not os.path.isdir(path):
                raise ValidationError(
                    message="That folder doesn't exist.",
                    cursor_position=len(path),
                )

    # ---------------- Constructors ---------------- #

    def __init__(self, message: str, input_type: InputModeEnum, file_type: str | None = None):
        self.message:   str           = message
        self.mode:      InputModeEnum = input_type
        self.file_type: str | None    = file_type

    # ---------------- File Inputs ---------------- #

    def _select_file_path_easygui(self) -> str | None:
        picked_file =  fileopenbox(
            msg=self.message,
            title=self.message,
            filetypes=[self.file_type] if self.file_type else None,
            multiple=False
        )
        if not picked_file:
            return None
        
        path: str = str(picked_file)

        path = os.path.expanduser(path)
        
        if not os.path.isfile(path):
            return None
        
        return os.path.normpath(os.path.abspath(path)) 

    def _select_file_path_questionary(self) -> str | None:
        picked_file = Qpath(
            self.message,
            validate=self.FileValidator([self.file_type] if self.file_type else None),
            only_directories=False
        ).ask()
        if not picked_file:
            return None
        return os.path.normpath(os.path.abspath(os.path.expanduser(picked_file.strip())))

    # ---------------- Folder Inputs ---------------- #

    def _select_folder_path_easygui(self) -> str | None:
        picked_folder = diropenbox(
            msg=self.message,
            title=self.message,
            default=os.path.expanduser("~")
        )
        if not picked_folder:
            return None
        path = os.path.expanduser(str(picked_folder)).strip()
        return os.path.normpath(os.path.abspath(path)) if os.path.isdir(path) else None

    def _select_folder_path_questionary(self) -> str | None:
        picked_folder = Qpath(
            self.message,
            validate=self.FolderValidator(),
            only_directories=True
        ).ask()
        if not picked_folder:
            return None
        return os.path.normpath(os.path.abspath(os.path.expanduser(picked_folder.strip())))

    # ---------------- Dispatcher ---------------- #

    def _selected_type(self):
        choice = select(
            self.message,
            choices=["Browse...(EasyGUI)", "Type or paste a path (Questionary)", "Cancel"]
        ).ask()

        match choice:
            case "Browse...(EasyGUI)":
                return (
                    self._select_file_path_easygui if self.mode is InputModeEnum.File
                    else self._select_folder_path_easygui
                )
            case "Type or paste a path (Questionary)":
                return (
                    self._select_file_path_questionary if self.mode is InputModeEnum.File
                    else self._select_folder_path_questionary
                )
            case "Cancel" | _:
                return None

    # ---------------- Public API ---------------- #

    def get_path(self) -> InputData:
        func = self._selected_type()

        if func is None:
            text = "No File Selected" if self.mode is InputModeEnum.File else "No Folder Selected"
            return InputData(None, None, cancelInput=True, erroring=FileExistsError(text))

        ConsoleClass.printing(self.mode)

        if self.mode is InputModeEnum.File:
            path = cast(FileFunctionType, func)()
            if not path:
                return InputData(None, None, cancelInput=True, erroring=FileExistsError("No File Selected"))
            try:
                df = read_csv(path)
            except Exception as e:
                return InputData(None, path, erroring=e)
            return InputData(df, path)

        elif self.mode is InputModeEnum.Folder:
            path = cast(FolderFunctionType, func)()
            if not path:
                return InputData(None, None, cancelInput=True, erroring=FileExistsError("No Folder Selected"))
            return InputData(None, path)

        raise SystemError("Unexpected input type")

    def change_input_mode(self)-> None:
        choices: list[str] = [m.value for m in InputModeEnum]

        selected_mode = select(
            "Select Mode:",
            choices=choices
        ).ask()

        self.mode = InputModeEnum(selected_mode)




if __name__ == "__main__":
    picker = FileFolderInput("Select CSV File", InputModeEnum.File, "*.csv")
    result = picker.get_path()

    if result.cancelInput:
        ConsoleClass.printing("❌ User canceled.")
    elif result.erroring:
        ConsoleClass.printing(f"⚠️ Error: {result.erroring}")
    else:
        ConsoleClass.printing(f"✅ Selected: {result.dataPath}")
