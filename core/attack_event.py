import random
from typing import Dict, List

from core.events import EventType, ColonyEvent


class AttackEvent(ColonyEvent):
    def __init__(self, config):
        super().__init__(EventType.ATTACK, config)
        self.attacker_types = ["чужие муравьи", "жуки", "пауки", "грызуны"]
        self.attacker = random.choice(self.attacker_types)
        self.strength = random.randint(1, 10) * self.severity

    def execute(self, colony) -> Dict:
        result = {
            "success": False,
            "food_lost": 0,
            "ants_lost": [],
            "message": ""
        }

        defense_strength = len(colony.soldiers) * 3
        defense_strength += len(colony.workers) * 0.5

        if len(colony.soldiers) == 0:
            defense_strength *= 0.3
            result["message"] = f"{self.attacker} атакуют колонию! Нет солдат для защиты!"
        else:
            result["message"] = f"{self.attacker} атакуют колонию! Солдаты вступают в бой!"

        if defense_strength >= self.strength:
            result["success"] = True
            result["message"] += " Атака отражена! Потери минимальны."

            food_lost_percentage = 0.05 * self.severity
            result["food_lost"] = int(colony.food_storage * food_lost_percentage)
            colony.food_storage -= result["food_lost"]

            soldier_losses = self._calculate_soldier_losses(colony, victory=True)
            result["ants_lost"] = soldier_losses

        else:
            result["success"] = False
            result["message"] += f" Защита провалена! {self.attacker} проникли в колонию."

            food_lost_percentage = 0.3 + (0.4 * self.severity)
            if len(colony.soldiers) == 0:
                food_lost_percentage = 0.8

            result["food_lost"] = int(colony.food_storage * food_lost_percentage)
            colony.food_storage = max(0, colony.food_storage - result["food_lost"])

            ant_losses = self._calculate_ant_losses(colony)
            result["ants_lost"] = ant_losses

        return result

    def _calculate_soldier_losses(self, colony, victory: bool) -> List:
        losses = []

        if not colony.soldiers:
            return losses

        loss_chance = 0.1 + (0.2 * self.severity)

        soldiers_to_remove = []
        for soldier in colony.soldiers:
            if random.random() < loss_chance:
                soldier.die("погиб в бою", colony.day)
                soldiers_to_remove.append(soldier)
                losses.append(soldier)

        for soldier in soldiers_to_remove:
            if soldier in colony.soldiers:
                colony.soldiers.remove(soldier)

        return losses

    def _calculate_ant_losses(self, colony) -> List:
        losses = []

        if colony.workers:
            worker_loss_percentage = 0.2 + (0.3 * self.severity)
            workers_to_lose = int(len(colony.workers) * worker_loss_percentage)
            workers_to_lose = max(1, min(workers_to_lose, len(colony.workers)))

            workers_to_remove = random.sample(colony.workers, workers_to_lose)
            for worker in workers_to_remove:
                worker.die("погиб при атаке", colony.day)
                losses.append(worker)
                colony.workers.remove(worker)

        if colony.soldiers:
            soldier_loss_percentage = 0.5 + (0.4 * self.severity)
            soldiers_to_lose = int(len(colony.soldiers) * soldier_loss_percentage)
            soldiers_to_lose = max(1, min(soldiers_to_lose, len(colony.soldiers)))

            soldiers_to_remove = random.sample(colony.soldiers, soldiers_to_lose)
            for soldier in soldiers_to_remove:
                soldier.die("погиб в бою", colony.day)
                losses.append(soldier)
                colony.soldiers.remove(soldier)

        return losses

    def get_description(self) -> str:
        strength_desc = (
            "слабая" if self.strength < 3
            else "средняя" if self.strength < 7
            else "сильная"
        )
        return f"{self.attacker} готовятся к {strength_desc} атаке на колонию"
