import pytest
import pandas as pd
from util.csv_stuff import CSV_DataHolder

def test_generate_from_data_creates_holder():
    df = pd.DataFrame({
        "name": ["Alice", "Bob"],
        "age": [25, 30],
    })

    holder = CSV_DataHolder.generate_from_data(df)

    assert isinstance(holder, CSV_DataHolder)
    assert holder.headers == ["name", "age"]
    assert holder.data == {"name": ["Alice", "Bob"], "age": [25, 30]}
    pd.testing.assert_frame_equal(holder.data_frame, df)

def test_generate_from_data_raises_on_wrong_type():
    with pytest.raises(TypeError):
        CSV_DataHolder.generate_from_data("not a dataframe") # type: ignore
