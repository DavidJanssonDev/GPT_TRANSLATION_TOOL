
import types
from typing import cast
import util.menu_stuff as MS
import main as M

class DummyCSV:
    _file_loaded = False
    _file_output_path = ""

class DummyTranslate:
    def __init__(self):
        self.called = False
    def _transalate(self):
        self.called = True

class DummySettings:
    def __init__(self, main):
        self.main = main
        self._set_output_path_called = False
    def _set_output_path(self):
        self._set_output_path_called = True

class DummyMainProject:
    def __init__(self):
        self.CSV_Data = DummyCSV()
        self.TransalteSystem = DummyTranslate()
        self.settings = DummySettings(self)
        self.MenuSystem = types.SimpleNamespace(menus=[MS.Menu("root")])

    def _load_csv(self):
        self.CSV_Data._file_loaded = True

def test_menuitem_enabled_and_submenu():
    submenu = MS.Menu("Sub")
    menuitem1 = MS.MenuItem(title="A", action=lambda:None, enabled=True)
    menuitem2 = MS.MenuItem(title="B", submenu=submenu, enabled=lambda: False)

    assert menuitem1.is_enabled() is True
    assert menuitem2.is_enabled() is False
    assert not menuitem1.is_submenu()
    assert menuitem2.is_submenu()

def test_menu_adders_and_effective_choices():
    menu_top = MS.Menu("Top")
    menu_top.add_action("Do", "desc", lambda: None)
    menu_sub = MS.Menu("Sub")
    menu_top.add_submenu("More", "desc2", menu_sub, enabled=True)
    assert len(menu_top.items) == 2

    mainproject = DummyMainProject()
    system = MS.MenuSystem(cast(M.MainProject, mainproject))
    system.menus[:] = [menu_top]

    eff = system._effective_choices()
    # Two items + exit since root
    assert len(eff) == 3
    assert eff[-1]["type"] == "exit"

def test_build_table_rows_root_and_back():
    mainproject = DummyMainProject()
    system = MS.MenuSystem(cast(M.MainProject, mainproject))
    # root has Exit visible
    rows = system._build_table_rows()
    assert any("Exit" in row[0] for row in rows)

    # add submenu and go into it
    menu_sub = MS.Menu("Sub")
    system.current.add_submenu("To sub", "x", menu_sub)
    system.menus.append(menu_sub)
    rows2 = system._build_table_rows()
    # now expect a Back option
    assert any("Back" in row[0] for row in rows2)

def test_activate_choice_index_navigation_and_action():
    mainproject = DummyMainProject()
    system = MS.MenuSystem(cast(M.MainProject, mainproject))
    # Use a clean root menu so indices are predictable in tests
    system.menus = [MS.Menu('Root')]
    # Setup: one action and one submenu
    called = {"action": False}
    
    def act(): 
        called["action"] = True
    
    menu_sub = MS.Menu("S")
    system.current.add_action("Act", "x", act)
    system.current.add_submenu("Sub", "y", menu_sub)

    # Build effective choices: [item0, item1, exit]
    assert system._activate_choice_index(0) is True   # triggers action
    assert called["action"] is True

    # enter submenu
    assert system._activate_choice_index(1) is True
    assert system.current.title == "S"

    # now 'back' exists; select it
    idx_back = system._effective_choices().index({"type": "back"})
    assert system._activate_choice_index(idx_back) is True
    assert system.current.title != "S"

    # select exit at root -> return False
    idx_exit = system._effective_choices().index({"type": "exit"})
    assert system._activate_choice_index(idx_exit) is False
