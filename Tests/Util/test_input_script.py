import os
import tempfile
import pytest
from prompt_toolkit.document import Document

import util.input_script as ip

def test_file_validator_ok():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        f.write(b"A,B\n1,2\n")
        path = f.name
    try:
        v = ip.FileFolderInput.FileValidator(["*.csv"])
        v.validate(Document(path))
    finally:
        os.remove(path)

def test_file_validator_ext_check():
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        f.write(b"A,B\n1,2\n")
        path = f.name
    try:
        v = ip.FileFolderInput.FileValidator(["*.csv"])
        with pytest.raises(Exception):
            v.validate(Document(path))
    finally:
        os.remove(path)

def test_folder_validator_ok(tmp_path):
    v = ip.FileFolderInput.FolderValidator()
    v.validate(Document(str(tmp_path)))

def test_get_path_file_flow_reads_csv(tmp_path, monkeypatch):
    csv_path = tmp_path / "x.csv"
    csv_path.write_text("A,B\n1,2\n")
    picker = ip.FileFolderInput("msg", ip.InputModeEnum.File, "*.csv")
    # bypass UI by returning a function that yields our path
    picker._selected_type = lambda: (lambda: str(csv_path))
    data = picker.get_path()
    assert data.dataPath == str(csv_path)
    assert not data.cancelInput
    assert data.dataFile is not None

def test_get_path_folder_flow(tmp_path, monkeypatch):
    picker = ip.FileFolderInput("msg", ip.InputModeEnum.Folder, None)
    picker._selected_type = lambda: (lambda: str(tmp_path))
    data = picker.get_path()
    assert data.dataPath == str(tmp_path)
    assert data.dataFile is None
