from dataclasses import dataclass


@dataclass
class Settings:
    OutputPath: str
    InputPath:  str


    def _set_output_path(self):
        pass
    
