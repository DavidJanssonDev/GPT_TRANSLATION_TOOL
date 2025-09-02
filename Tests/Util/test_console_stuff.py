from util.console_stuff import ConsoleClass

def test_console_printing(capsys):
    ConsoleClass.printing("Hello")
    captured = capsys.readouterr()
    assert "Hello" in captured.out
