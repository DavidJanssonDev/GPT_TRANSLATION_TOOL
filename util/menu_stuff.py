from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, List, Any, TypeAlias, TYPE_CHECKING
from tabulate import tabulate

import questionary
from .console_stuff import ConsoleClass

if TYPE_CHECKING:
    from main import MainProject


Tabulate_type: TypeAlias = list[list[str]]


#region DATACLASSES 

@dataclass
class MenuItem:
    title: str
    description: str = ""
    action: Callable[[], None] | None = None    # leaf action
    submenu: Menu | None = None               # or a submenu
    enabled: bool | Callable[[],bool] = True
    

    def is_enabled(self) -> bool:
        return self.enabled() if callable(self.enabled) else self.enabled

    def is_submenu(self) -> bool:
        return self.submenu is not None


@dataclass
class Menu:
    title: str
    items: list[MenuItem] = field(default_factory=list)

    def add_action(self, title: str, description: str, action: Callable[[], None], enabled: bool | Callable[[], bool] = True) -> "Menu":
        self.items.append(MenuItem(title=title, description=description, action=action, enabled=enabled))
        return self

    def add_submenu(self, title: str, description: str, submenu: Menu, enabled: bool | Callable[[], bool] = True) -> "Menu":
        self.items.append(MenuItem(title=title, description=description, submenu=submenu, enabled=enabled))
        return self

#region MENU SYSTEM CLASS

class MenuSystem:
    
    
    def __init__(self,main_project: MainProject, tablefmt: str = "fancy_grid") -> None:
        
        self.main: MainProject = main_project # refrence to the main project

        self.menus: list[Menu] = self.setup_menus()
        self.tablefmt = tablefmt

        # Hooks
        self.on_before_render: Callable[[Menu], None] | None = None
        self.on_after_action: Callable[[Menu, MenuItem], None] | None = None



    @property
    def current(self) -> Menu:
        """
        Gets the Current aktiv menu

        Returns:
            Menu: Current aktiv menu
        """
        return self.menus[-1]



    def _build_table_rows(self) -> Tabulate_type:
        """
        Builds the table that tabulate is showing

        Returns:
            Tabulate_type: table
        """
        rows: Tabulate_type = []
        for item in self.current.items:
            kind = "→" if item.is_submenu() else "•"
            marker = ""
            marker = "" if item.is_enabled() else " (disabled)"

            rows.append([f"{kind} {item.title}{marker}", item.description])

        # Synthetic rows
        if len(self.menus) > 1 :
            rows.append(["↩ Back", "Return to previous menu"])
        if self._is_root():
            rows.append(["⏻ Exit", "Close the menu"])
        return rows

    def _render(self) -> None:
        if self.on_before_render:
            self.on_before_render(self.current)
        ConsoleClass.clear()
        ConsoleClass.printing(f"\n=== {self.current.title} ===")
        ConsoleClass.printing(tabulate(self._build_table_rows(), headers=["Title", "Description"], tablefmt=self.tablefmt))

    def _is_root(self) -> bool:
        return len(self.menus) == 1

    def _effective_choices(self) -> List[Any]:
        """
        Build list of choices in visual order mapping to:
          {"type": "item", "item": MenuItem} | {"type": "back"} | {"type": "exit"}
        Disabled items are selectable-disabled.
        """
        effective = [{"type": "item", "item": item} for item in self.current.items]
        if len(self.menus) > 1 :
            effective.append({"type": "back"})

        if self._is_root():
            effective.append({"type": "exit"})
        return effective

    def _ask_select(self) -> int | None:
        eff = self._effective_choices()
        if not eff:
            return None

        choices = []
        for idx, ch in enumerate(eff):
            if ch["type"] == "item":
                menuItem: MenuItem = ch["item"]
                label = f"{'→' if menuItem.submenu is not None else '•'} {menuItem.title} — {menuItem.description}"
                choices.append(
                    questionary.Choice(title=label, value=idx, disabled=None if menuItem.is_enabled() else "disabled")
                    )
            elif ch["type"] == "back":
                choices.append(questionary.Choice(title="↩ Back — Return to previous menu", value=idx))
            else:  # exit (root only)
                choices.append(questionary.Choice(title="⏻ Exit — Close the menu", value=idx))

        return questionary.select(
            self.current.title, 
            choices=choices,
            instruction="",
            qmark=""
            ) \
        .ask()

    def _activate_choice_index(self, index: int) -> bool:
        effective_choices = self._effective_choices()
        if not (0 <= index < len(effective_choices)):
            return True  # ignore and continue

        choice = effective_choices[index]
        
        if choice["type"] == "exit":      # only present on root
            ConsoleClass.printing("Goodbye!")
            return False              # stop loop

        if choice["type"] == "back":      # only present on submenus
            self.menus.pop()
            return True

        # Item
        menuItem: MenuItem = choice["item"]
        
        if not menuItem.is_enabled():
            ConsoleClass.printing("This option is disabled.")
            return True

        if menuItem.submenu is not None:
            self.menus.append(menuItem.submenu)
            return True

        if menuItem.action:
            menuItem.action()
            if self.on_after_action:
                self.on_after_action(self.current, menuItem)
        return True

    def setup_menus(self) -> list[Menu]:

        temp_list: list[Menu] = []

        sett_output_path_menu: Menu = Menu("Sett Output path") \
            .add_action("Sett", "sett output path", self.main.settings._set_output_path)
        
        sett_path_menu: Menu = Menu("Sett Paths") \
            .add_submenu("Change output Path", "Sett where the output file should be placed at", sett_output_path_menu)
        
        load_settings_menu: Menu = Menu("Settings") \
            .add_submenu("Set File Path", "Change output & input path", sett_path_menu)
        
        main_menu: Menu = Menu("Main Menu") \
            .add_action("Translate", "Translate", self.main.TransalteSystem._transalate, enabled=lambda: self.main.CSV_Data._file_loaded) \
            .add_action("Load File","CSV menu", self.main._load_csv) \
            .add_submenu("Settings", "Settings for the progra",load_settings_menu)
        
        temp_list.append(main_menu)

        return temp_list

    def run(self) -> None:
        while True:
            self._render()
            idx = self._ask_select()
            
            if idx is None:          # cancelled
                ConsoleClass.printing("Goodbye!")
                break
            
            if not self._activate_choice_index(idx):
                break