from dataclasses import dataclass, field

@dataclass
class ASCII:
    grid:   list[list[str]]
    width:  int
    height: int

    #TODO:
    #potentielle config var's:
    charset:    str

    #potentielle var's für logging & testing: