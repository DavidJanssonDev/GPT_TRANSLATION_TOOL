from util.input_script import InputData, InputTypeEnum, _ask_for_output_folder_path, path_input
from util.csv_stuff import CSV_DataHolder        # noqa: E402
from util.settings import Settings               # noqa: E402
from util.menu_stuff import MenuSystem           # noqa: E402
from util.libary_installment import Intallments  # noqa: E402
from util.console_stuff import ConsoleClass
from util.translate_class import TransalteSystem # noqa: E402
from rich.traceback import install               # noqa: E402

install()

class MainProject:
    def __init__(self, File_path) -> None:
        
        # SET UP ALL REQUIRED LIBRARIES
        self.Intallments_Class: Intallments = Intallments(File_path)
        self.Intallments_Class.install_required_libraries()

        self.settings: Settings = Settings("uploads/Output", "uploads/Input")

        self.CSV_Data: CSV_DataHolder = CSV_DataHolder()
        self.TransalteSystem: TransalteSystem = TransalteSystem() 
        self.MenuSystem: MenuSystem = MenuSystem(self)




    def _load_csv(self):
        data: InputData = path_input("Select CSV TYPE", InputTypeEnum.File, "*.csv")
        
        # Handle cancel / error gracefully (don’t crash the menu)
        if data.cancelInput:
            return
        if data.erroring:
            ConsoleClass.printing(f"[yellow]Failed to load CSV: {data.erroring}[/]")
            return
        
        if data.dataFile is None:
            ConsoleClass.printing("[yellow]No data returned.[/]")
            return

        # Build and store the CSV holder (classmethod returns a new instance)
        self.CSV_Data = CSV_DataHolder.generate_from_data(data.dataFile)  # <-- assign the result
        self.CSV_Data._file_loaded = True

        ConsoleClass.printing("[green]✓ CSV loaded successfully. Returning to Main Menu…[/]")

        # Jump back to the root menu
        self.MenuSystem.menus[:] = self.MenuSystem.menus[:1]
    def run(self)-> None:
        self.MenuSystem.run()

   

if __name__ == "__main__":
    # quick standalone test for folder selection
    folder = _ask_for_output_folder_path()
    if folder is None:
        print("❌ User canceled.")
    else:
        print(f"✅ Selected folder: {folder}")

