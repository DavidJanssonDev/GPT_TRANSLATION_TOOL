from util.input_script import InputData, InputTypeEnum, path_input
from util.csv_stuff import CSV_DataHolder        # noqa: E402
from util.settings import Settings               # noqa: E402
from util.menu_stuff import MenuSystem           # noqa: E402
from util.libary_installment import Intallments  # noqa: E402
from util.console_stuff import ConsoleClass
from util.translate_class import TransalteSystem # noqa: E402
from rich.traceback import install               # noqa: E402

install()

class MainProject:
    """
    The Main class that holds everything together
    """
    def __init__(self, File_path: str) -> None:
        """
        Initialize the MainProject and its core components.

        Args:
            File_path (str): Path to the requirements file for required libraries.
        
        """
        
        # SET UP ALL REQUIRED LIBRARIES
        self.Intallments_Class: Intallments = Intallments(File_path)
        self.Intallments_Class.install_required_libraries()

        self.settings: Settings = Settings(self)

        self.CSV_Data: CSV_DataHolder = CSV_DataHolder()
        self.TransalteSystem: TransalteSystem = TransalteSystem() 
        self.MenuSystem: MenuSystem = MenuSystem(self)




    def _load_csv(self):
        """
        Load a CSV file into the Project and makes the user go back to main menu
        """
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
        """
        Run the interactive menu system for the project
        """
        self.MenuSystem.run()

   

if __name__ == "__main__":
    
    project: MainProject = MainProject("requirements.txt")

    project.run()
    


