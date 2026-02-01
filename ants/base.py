from abc import ABC, abstractmethod
import random
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from core.config import SimulationConfig

from core.ant_state import AntState


class Ant(ABC):

    def __init__(
            self,
            ant_type: str,
            max_age: int,
            config: 'SimulationConfig'
    ):
        self.ant_type = ant_type
        self.max_age = max_age
        self.config = config

        self.health = 100
        self.hunger = 0
        self.age = 0
        self.state = AntState.ALIVE
        self.diseased = False
        self.injured = False

        self.death_cause: Optional[str] = None
        self.death_day: Optional[int] = None

    def try_get_disease(self) -> bool:
        if random.random() < self.config.disease_chance:
            self.diseased = True
            self.health = max(0, self.health - 10)
            return True
        return False

    def try_get_injury(self) -> bool:
        if random.random() < self.config.injury_chance:
            self.injured = True
            self.health = max(0, self.health - 15)
            return True
        return False

    def age_one_step(self, current_day: int = 0) -> None:
        if self.state == AntState.DEAD:
            return

        self.age += 1
        self.hunger += 10

        if self.hunger >= self.config.hunger_threshold:
            self.health = max(0, self.health - self.config.hunger_damage)
            if self.health <= 0:
                self.die("голод", current_day)

        if self.try_get_disease() and self.health <= 0:
            self.die("болезнь", current_day)

        if self.try_get_injury() and self.health <= 0:
            self.die("травма", current_day)

        if self.age >= self.max_age and self.state == AntState.ALIVE:
            self.state = AntState.OLD

        if self.state == AntState.OLD:
            if random.random() < self.config.old_age_death_chance:
                self.die("старость", current_day)

        if self.health <= 0 and self.state != AntState.DEAD:
            self.die("низкое здоровье", current_day)

    def die(self, cause: str = "неизвестно", day: Optional[int] = None) -> None:
        self.state = AntState.DEAD
        self.death_cause = cause
        self.death_day = day

    def feed(self, food_amount: int = 25) -> None:
        self.hunger = max(0, self.hunger - food_amount)
        if self.hunger < self.config.hunger_threshold:
            self.health = min(100, self.health + 5)

    def is_alive(self) -> bool:
        return self.state != AntState.DEAD

    def get_death_info(self) -> str:
        if self.state != AntState.DEAD or not self.death_cause:
            return "жив"
        day_info = f" на день {self.death_day}" if self.death_day else ""
        return f"умер от {self.death_cause}{day_info}"

    def __str__(self) -> str:
        if self.is_alive():
            return f"{self.ant_type}(возраст={self.age}, здоровье={self.health}, состояние={self.state})"
        else:
            return f"{self.ant_type}(возраст при смерти={self.age}, причина={self.death_cause})"