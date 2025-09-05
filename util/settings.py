from dataclasses import dataclass, field
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..main import MainProject

from .console_stuff import ConsoleClass
from .input_script import InputData, InputModeEnum, FileFolderInput


@dataclass
class Settings:
    MainRefrence: "MainProject"
    OutputPath: str = field(default="Output")


    def _set_output_path(self)-> None:
        
        inputer: FileFolderInput = FileFolderInput("Select Output Folder", InputModeEnum.Folder, None)
        
        data: InputData = inputer.get_path()

        if data.cancelInput:
            return
        
        if data.erroring:
            ConsoleClass.printing(f"[yellow] Faild to load Folder {data.erroring} [/]")
            return 
        
        if data.dataPath is None:
            ConsoleClass.printing("[yellow] No folder path return [/]")
            return
        
        self.MainRefrence.CSV_Data._file_output_path = data.dataPath

        ConsoleClass.printing("[green]✓ Folder change successfully. Returning to Main Menu…[/]")
        
        self.MainRefrence.MenuSystem.menus[:] = self.MainRefrence.MenuSystem.menus[:1]
        return


        