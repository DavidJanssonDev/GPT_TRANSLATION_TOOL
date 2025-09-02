from util.table_stuff import ConsoleTable

def test_console_table_exists():
    # Just check instantiation since it's currently a placeholder
    table = ConsoleTable()
    assert isinstance(table, ConsoleTable)
