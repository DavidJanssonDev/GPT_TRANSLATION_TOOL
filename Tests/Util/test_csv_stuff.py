import pandas as pd
import pytest
from util.csv_stuff import CSV_DataHolder

def test_generate_from_data_type_guard():
    with pytest.raises(TypeError):
        CSV_DataHolder.generate_from_data({"a":[1,2]})  # type: ignore # wrong type

def test_generate_from_data_ok(capsys):
    df = pd.DataFrame({"A":[1,2], "B":[3,4]})
    holder = CSV_DataHolder.generate_from_data(df)
    # headers coerced to str
    assert holder.headers == ["A","B"]
    assert holder.data_frame.equals(df.rename(columns=str))
    # prints a success message
    out = capsys.readouterr().out
    assert "Generate Data compleat" in out

