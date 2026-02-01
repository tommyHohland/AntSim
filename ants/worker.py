import random
from ants.base import Ant


class WorkerAnt(Ant):
    def __init__(self, config):
        super().__init__(
            ant_type="Рабочий",
            max_age=config.worker_max_age,
            config=config
        )
        self.food_carried = 0


    def work(self) -> int:
        if not self.is_alive():
            return 0

        self.food_carried = random.randint(1, 3)
        print(f"Рабочий нашел {self.food_carried} единиц пищи")
        return self.food_carried

    def age_one_step(self, current_day: int = 0) -> None:
        super().age_one_step(current_day)