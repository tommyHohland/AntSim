from enum import Enum, auto


class AntState(Enum):
    ALIVE = auto()
    OLD = auto()
    DEAD = auto()
    LARVA = auto()
    PUPA = auto()

    def __str__(self):
        names = {
            self.ALIVE: "живой",
            self.OLD: "старый",
            self.DEAD: "мертвый",
            self.LARVA: "личинка",
            self.PUPA: "куколка"
        }
        return names.get(self, self.name.lower())