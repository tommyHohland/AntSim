import random
from ants.base import Ant
from core.ant_state import AntState


class Larva(Ant):
    def __init__(self, config, future_type=None):
        super().__init__(
            ant_type="Личинка",
            max_age=100,
            config=config
        )
        self.state = AntState.LARVA
        self.growth_progress = 0
        self.growth_stage = "larva"

        if future_type is None:
            self.future_type = self._determine_future_type()
        else:
            self.future_type = future_type

        self._init_future_type_characteristics()

    def _determine_future_type(self) -> str:
        rand = random.random()
        if rand < self.config.worker_chance:
            return "worker"
        elif rand < self.config.worker_chance + self.config.soldier_chance:
            return "soldier"
        else:
            return "drone"

    def _init_future_type_characteristics(self):
        self.future_attributes = {
            "max_age": 0,
            "strength": 0,
            "speed": 0,
            "description": ""
        }

        if self.future_type == "worker":
            self.ant_type = "Личинка (будущий рабочий)"
            self.future_attributes = {
                "max_age": self.config.worker_max_age,
                "strength": 5,
                "speed": 2.0,
                "description": "🐜 Рабочий муравей"
            }
        elif self.future_type == "soldier":
            self.ant_type = "Личинка (будущий солдат)"
            self.future_attributes = {
                "max_age": self.config.soldier_max_age,
                "strength": 15,
                "speed": 1.5,
                "description": "⚔️ Солдат"
            }
        elif self.future_type == "drone":
            self.ant_type = "Личинка (будущий трутень)"
            self.future_attributes = {
                "max_age": self.config.drone_max_age,
                "strength": 3,
                "speed": 3.0,
                "description": "🐝 Трутень"
            }

    def move(self) -> None:
        if self.is_alive():
            print(f"Личинка (будет {self.get_future_type_name()}) шевелится")

    def work(self) -> None:
        if not self.is_alive() or self.state == AntState.PUPA:
            return

        self.growth_progress += 1

        if self.hunger >= self.config.hunger_threshold:
            if random.random() < self.config.larva_starvation_chance:
                self.die("голод (личинка)", self.config.current_day if hasattr(self.config, 'current_day') else None)
                print(f" Личинка (будущий {self.get_future_type_name()}) умерла от голода")
                return

        if self.growth_progress >= self.config.larva_growth_duration:
            self.state = AntState.PUPA
            self.growth_stage = "pupa"
            self.growth_progress = 0
            print(f"Личинка превратилась в куколку (будет {self.get_future_type_name()})")
        else:
            print(f"Личинка (будет {self.get_future_type_name()}) растет: "
                  f"{self.growth_progress}/{self.config.larva_growth_duration}")

    def age_one_step(self, current_day: int = 0) -> None:
        if not self.is_alive():
            return

        self.age += 1
        self.hunger += 15

        if self.hunger >= self.config.hunger_threshold:
            self.health = max(0, self.health - self.config.hunger_damage * 2)

        if self.health <= 0:
            self.die("низкое здоровье (личинка)", current_day)

    def get_future_type_name(self) -> str:
        type_names = {
            "worker": "рабочий",
            "soldier": "солдат",
            "drone": "трутень"
        }
        return type_names.get(self.future_type, self.future_type)

    def __str__(self) -> str:
        if self.is_alive():
            return f"Личинка(возраст={self.age}, будущий={self.get_future_type_name()}, здоровье={self.health})"
        else:
            return f"Личинка(возраст при смерти={self.age}, будущий={self.get_future_type_name()}, причина={self.death_cause})"