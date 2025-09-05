from util.libary_installment import Libary, Intallments

def test_libary_cmd_builder():
    lib = Libary("pandas", "2.2.2")
    cmd = lib.get_installment_cmd()
    assert "pip" in cmd and "install" in cmd and "pandas==2.2.2" in cmd[-2]

def test_eq():
    assert Libary("x","1") == Libary("x","1")
    assert Libary("x","1") != Libary("x","2")

def test_read_requirements_and_missing(tmp_path):
    req = tmp_path / "req.txt"
    req.write_text("pandas==2.2.2\n# comment\nrich>=13.7.1\n")
    inst = Intallments(str(req))
    libs = inst.read_requirements()
    names = [libaryClasses.LibaryName for libaryClasses in libs]
    assert "pandas" in names and "rich" in names

    current = [Libary("pandas","2.2.2")]
    missing = inst.get_missing_libraries(current, libs)
    # rich missing because version is not exact in current set
    assert any(libaryClasses.LibaryName == "rich" for libaryClasses in missing)

def test_pip_install_invokes_subprocess(monkeypatch):
    captured = []
    def fake_run(cmd, check):
        captured.append((tuple(cmd), check))
        class R: 
            pass
        return R()
    monkeypatch.setattr("subprocess.run", fake_run)
    Intallments("x").pip_install([Libary("abc","1.0.0")])
    assert captured and captured[0][1] is True

