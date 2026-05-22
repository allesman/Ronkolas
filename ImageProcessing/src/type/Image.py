from dataclasses import dataclass, field

@dataclass
class Image:
    width:  int
    height: int
    #pixels: TODO

    #config
    mode:           str     #RGB or GRAY
    source_path:    str