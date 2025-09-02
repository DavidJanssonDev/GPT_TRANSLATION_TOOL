import sys 
import subprocess

from importlib.metadata import distributions
from packaging.version import Version
from dataclasses import dataclass


@dataclass
class Libary:

    LibaryName: str 
    LibaryVerstion: str

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, Libary)
            and self.LibaryName == other.LibaryName
            and self.LibaryVerstion == other.LibaryVerstion
        )

    def get_installment_cmd(self) -> list[str]:
        # Force the exact version, even if a higher one is installed
        # --upgrade ensures downgrades happen cleanly when exact version differs
        # --force-reinstall guarantees replacement of an already-present dist
        return [
            sys.executable, "-m", "pip", "install",
            "--upgrade", "--force-reinstall",
            f"{self.LibaryName}=={self.LibaryVerstion}",
            "-qqq",
        ]



@dataclass
class Intallments:

    FilePath: str

    def read_requirements(self) -> list[Libary]:
        libraries: list[Libary] = []
        with open(self.FilePath, "r") as file:
            for line in file:
                line:str = line.strip()
                if not line or line.startswith("#"):
                    continue
                for sep in ["==", ">=", "<=", "~=", ">", "<"]:
                    if sep in line:
                        name, ver = (part.strip() for part in line.split(sep, 1))
                        libraries.append(Libary(name, ver))
                        break
        return libraries
    
    
    def get_current_installed_libaries(self) -> list[Libary]:
        return [Libary(dist.metadata["Name"], dist.version) for dist in distributions()]
    
    def get_missing_libraries(self, current: list[Libary], required: list[Libary]) -> list[Libary]:
        """
        Return items where the exact version is NOT installed.
        That includes: not installed, older, or newer than required.
        """
        cur = {lib.LibaryName.lower(): lib.LibaryVerstion for lib in current}
        missing: list[Libary] = []
        for req in required:
            name = req.LibaryName.lower()
            if name not in cur or Version(cur[name]) != Version(req.LibaryVerstion):
                missing.append(req)
        return missing
    

    def pip_install(self, install_libraries: list[Libary]) -> None:
        for library in install_libraries:
            print(f"Installing exact version: {library.LibaryName}=={library.LibaryVerstion}")
            subprocess.run(library.get_installment_cmd(), check=True)



    def install_required_libraries(self) -> None:
        curret_list:list[Libary] = self.get_current_installed_libaries()

        print(f"Current amount of libraries installed on python: {len(curret_list)}")

        requried_list: list[Libary]  = self.read_requirements()

        print(f"Current amount of libaries needed to run: {len(requried_list)}")

        missing_list: list[Libary] = self.get_missing_libraries(curret_list, requried_list)

        print(f"Current amount missing: {len(missing_list)}")

        self.pip_install(missing_list)



if __name__ == "__main__":
    installment: Intallments = Intallments("requirements.txt")
    installment.install_required_libraries()
    