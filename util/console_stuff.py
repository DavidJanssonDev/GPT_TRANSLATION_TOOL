from time import sleep
from typing import Any
from rich.console import Console

class ConsoleClass:
    """
    The class that Handels printing can clearing the terminal
    """
    __console: Console = Console()


    @staticmethod
    def printing(message: Any):
        """
        Printing to the console
        """
        
        ConsoleClass.__console.print(message)

    @staticmethod
    def clear():
        """
        Clear the console 
        """
        ConsoleClass.__console.clear()
    
    @staticmethod
    def wait(seconds: float) -> None:
        return sleep(seconds)