from ants.base import Ant

class SoldierAnt(Ant):
    def __init__(self, config):
        super().__init__(
            ant_type="Солдат",
            max_age=config.soldier_max_age,
            config=config
        )

    def work(self) -> None:
        if not self.is_alive():
            return

        self.try_get_injury()

    def age_one_step(self, current_day: int = 0) -> None:
        super().age_one_step(current_day)