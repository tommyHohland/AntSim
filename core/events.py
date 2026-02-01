from enum import Enum, auto
from typing import Dict
import random
from abc import ABC, abstractmethod


class EventType(Enum):
    ATTACK = auto()

    def __str__(self):
        names = {
            self.ATTACK: "атака на колонию",
        }
        return names.get(self, self.name.lower())


class ColonyEvent(ABC):
    def __init__(self, event_type: EventType, config):
        self.event_type = event_type
        self.config = config
        self.severity = random.uniform(0.1, 1.0)

    @abstractmethod
    def execute(self, colony) -> Dict:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass


