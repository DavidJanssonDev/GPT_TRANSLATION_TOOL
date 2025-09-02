from util.input_script import input_csv_type, InputData

def test_inputdata_defaults():
    data = InputData(None)
    assert data.dataFile is None
    assert data.cancelInput is False
    assert data.erroring is None

def test_get_csv_input_invalid(monkeypatch):
    # Monkeypatch fileopenbox to simulate "cancel"
    import util.input_script
    monkeypatch.setattr(util.input_script, "fileopenbox", lambda **kwargs: None)
    result = input_csv_type()
    assert isinstance(result, InputData)
    assert result.dataFile is None
    assert isinstance(result.erroring, FileExistsError)
