from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class SimulationConfig:
    disease_chance: float = 0.3
    injury_chance: float = 0.3
    old_age_death_chance: float = 0.70
    hunger_damage: int = 20
    hunger_threshold: int = 100

    queen_egg_laying_chance: float = 0.8
    queen_egg_laying_interval: int = 3
    queen_egg_min_count: int = 1
    queen_egg_max_count: int = 5

    larva_growth_duration: int = 3
    pupa_growth_duration: int = 2
    larva_starvation_chance: float = 0.3

    worker_chance: float = 0.6
    soldier_chance: float = 0.4

    initial_workers: int = 20
    initial_food: int = 100
    queen_max_age: int = 50
    worker_max_age: int = 30
    soldier_max_age: int = 25

    show_detailed_stats: bool = True

    attack_chance: float = 0.15
    min_days_for_attack: int = 5

    def validate(self) -> Optional[str]:
        probabilities = [
            (self.disease_chance, "disease_chance"),
            (self.injury_chance, "injury_chance"),
            (self.old_age_death_chance, "old_age_death_chance"),
            (self.queen_egg_laying_chance, "queen_egg_laying_chance"),
            (self.larva_starvation_chance, "larva_starvation_chance"),
            (self.worker_chance + self.soldier_chance, "sum of development chances"),
            (self.attack_chance, "attack_chance")
        ]

        for value, name in probabilities:
            if not 0 <= value <= 1:
                return f"{name} must be between 0 and 1, got {value}"

        if self.queen_egg_min_count > self.queen_egg_max_count:
            return "queen_egg_min_count cannot be greater than queen_egg_max_count"

        return None