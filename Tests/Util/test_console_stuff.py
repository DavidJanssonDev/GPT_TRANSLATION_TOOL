import util.console_stuff as cs

def test_console_methods_smoke(capsys):
    cs.ConsoleClass.printing("hello")
    cs.ConsoleClass.clear()  # shouldn't raise
    cs.ConsoleClass.wait(0)  # fast
    out = capsys.readouterr().out
    assert "hello" in out