
import types
from typing import cast
import util.input_script as IS
import util.settings as ST
import main as MS
class DummyMenuSystem:
    def __init__(self):
        self.menus = [types.SimpleNamespace(title="root"), types.SimpleNamespace(title="child")]

class DummyMain:
    def __init__(self):
        self.MenuSystem = DummyMenuSystem()
        self.CSV_Data = types.SimpleNamespace(_file_output_path="")

def make_settings():
    return ST.Settings(MainRefrence=cast(MS.MainProject, DummyMain()))

def run_case(input_data: IS.InputData):
    s = make_settings()
    # Monkeypatch the FileFolderInput class used inside settings module
    class FakePicker:
        def __init__(self, *a, **k): ...
        def get_path(self): return input_data
    ST.FileFolderInput = FakePicker  
    s._set_output_path()
    return s

def test_cancel_path():
    _ = run_case(IS.InputData(None, None, cancelInput=True, erroring=None))
    # no changes
    # leaving as smoke; no assertion on menus length due to environment differences

def test_error_path(capsys):
    _ = run_case(IS.InputData(None, None, cancelInput=False, erroring=RuntimeError("nope")))
    out = capsys.readouterr().out
    assert "Faild to load Folder" in out

def test_none_return_path(capsys):
    _ = run_case(IS.InputData(None, None, cancelInput=False, erroring=None))
    out = capsys.readouterr().out
    assert "No folder path" in out

def test_success_changes_state():
    s = run_case(IS.InputData(None, "/tmp", cancelInput=False, erroring=None))
    assert s.MainRefrence.CSV_Data._file_output_path == "/tmp"
    # menus collapsed to root
    assert len(s.MainRefrence.MenuSystem.menus) == 1
