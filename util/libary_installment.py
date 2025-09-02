from importlib.metadata import distributions 

from dataclasses import dataclass
from rich import inspect

@dataclass
class Libary:

    LibaryName: str 
    LibaryVerstion: str

    def __eq__(self, other)-> bool:
        return True if self.LibaryName == other.LibaryName 


@dataclass
class Intallments:

    FilePath: str

    def read_requirements(self):
        
        libraries: list[Libary] = []

        with open(self.FilePath, "r") as file:
            for line in file:

                # Strip whitespace and ignore comments/empty lines
                line = line.strip()

                if not line or line.startswith("#"):
                    continue
                

                # Split on common version specifiers
                for sep in ["==", ">=", "<=", "~=", ">", "<"]:
                    if sep in line:
                        libaryParts =  line.split(sep)
                        libaryName: str = libaryParts[0].strip()
                        libaryVersion: str = libaryParts[1].strip()
                        
                        libraries.append( Libary(libaryName, libaryVersion))

                        break

        return libraries
    
    def get_current_installed_libaries(self):
        current_libary_list = []
        
        for dist in distributions():
            current_libary_list.append(Libary(dist.metadata["Name"], dist.version))

        return current_libary_list

    def install_required_libraries(self):
        curret_list:list[Libary] = self.get_current_installed_libaries()
        requried_list: list[Libary]  = self.read_requirements()

        libary_missing: list[str]


if __name__ == "__main__":
    installment: Intallments = Intallments("requirements.txt")
    a = installment.read_requirements()
    inspect(a)