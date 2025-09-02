from typing import Any
from rich.console import Console

class ConsoleClass: 

    __console: Console = Console()


    @staticmethod
    def printing(message: Any):
        """
        Printing to the console
        """
        
        ConsoleClass.__console.print(message)

    