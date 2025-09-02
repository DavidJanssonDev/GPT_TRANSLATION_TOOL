from subprocess import run, CompletedProcess



class MainProject:
    def __init__(self, File_path) -> None:
        self.Requirements_File_path = File_path

    def check_pip_installations(self) -> None:
        
        librarys = []

        with open(self.Requirements_File_path, "r") as file:
            for line in file:

                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                for sep in  ["==", ">=", "<=", "~=", ">", "<"]:
                    if sep in line:
                        line = line.split(sep)[0].strip()
                        break 






