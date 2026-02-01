import random
from ants.base import Ant

class QueenAnt(Ant):
    def __init__(self, config):
        super().__init__(
            ant_type="Королева",
            max_age=config.queen_max_age,
            config=config
        )
        self.eggs_laid = 0
        self.days_since_last_laying = 0
        self.fed_by_workers = 0


    def work(self) -> int:
        if not self.is_alive():
            return 0

        self.days_since_last_laying += 1

        if (self.fed_by_workers >= 3 and
                self.days_since_last_laying >= self.config.queen_egg_laying_interval):

            if random.random() < self.config.queen_egg_laying_chance:
                eggs_count = random.randint(
                    self.config.queen_egg_min_count,
                    self.config.queen_egg_max_count
                )
                self.eggs_laid += eggs_count
                self.days_since_last_laying = 0
                self.fed_by_workers = 0
                print(f"Королева отложила {eggs_count} яиц! Всего: {self.eggs_laid}")
                return eggs_count
        return 0

    def receive_food(self, amount: int) -> None:
        self.fed_by_workers += amount
        self.feed(food_amount=amount * 10)

    def age_one_step(self, current_day: int = 0) -> None:
        super().age_one_step(current_day)