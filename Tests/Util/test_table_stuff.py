import util.table_stuff as ts

def test_console_table_exists():
    obj = ts.ConsoleTable()
    assert isinstance(obj, ts.ConsoleTable)