import random
from collections import defaultdict
from typing import Dict, Any, List

from ants.larva import Larva
from ants.queen import QueenAnt
from ants.soldier import SoldierAnt
from ants.worker import WorkerAnt
from core.ant_state import AntState
from core.attack_event import AttackEvent


class DeathStatistics:

    def __init__(self):
        self.total_deaths = 0
        self.deaths_by_cause = defaultdict(int)
        self.deaths_by_type = defaultdict(int)
        self.deaths_by_age_group = defaultdict(int)
        self.daily_deaths = []
        self.dead_ants = []

    def record_death(self, ant, cause: str, day: int):
        self.total_deaths += 1
        self.deaths_by_cause[cause] += 1
        self.deaths_by_type[ant.ant_type] += 1

        if ant.age < 5:
            age_group = "молодые (<5 дней)"
        elif ant.age < 20:
            age_group = "взрослые (5-20 дней)"
        else:
            age_group = "пожилые (>20 дней)"
        self.deaths_by_age_group[age_group] += 1

        death_record = {
            "day": day,
            "ant_type": ant.ant_type,
            "age": ant.age,
            "cause": cause,
            "future_type": getattr(ant, 'future_type', None) if isinstance(ant, Larva) else None
        }
        self.daily_deaths.append(death_record)
        self.dead_ants.append(ant)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_deaths": self.total_deaths,
            "by_cause": dict(self.deaths_by_cause),
            "by_type": dict(self.deaths_by_type),
            "by_age": dict(self.deaths_by_age_group),
            "daily_deaths": len(self.daily_deaths)
        }

    def print_statistics(self):
        if self.total_deaths == 0:
            print("Статистика смертности: нет смертей")
            return

        print("\nСТАТИСТИКА СМЕРТНОСТИ:")
        print(f"Всего смертей: {self.total_deaths}")

        print(f"\nПо причинам смерти:")
        for cause, count in sorted(self.deaths_by_cause.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.total_deaths) * 100
            print(f"     • {cause}: {count} ({percentage:.1f}%)")

        print(f"\n   По типам муравьев:")
        for ant_type, count in sorted(self.deaths_by_type.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / self.total_deaths) * 100
            print(f"     • {ant_type}: {count} ({percentage:.1f}%)")

        print(f"\n   По возрастным группам:")
        for age_group, count in self.deaths_by_age_group.items():
            percentage = (count / self.total_deaths) * 100
            print(f"     • {age_group}: {count} ({percentage:.1f}%)")

    def print_daily_deaths(self, day: int):
        todays_deaths = [d for d in self.daily_deaths if d["day"] == day]

        if todays_deaths:
            print(f"\nСмерти за день {day}:")
            for death in todays_deaths:
                future_info = f" (будущий {death['future_type']})" if death['future_type'] else ""
                print(f"   • {death['ant_type']}{future_info}, возраст {death['age']} дней: {death['cause']}")


class AntColony:
    def __init__(self, name: str, config):
        self.name = name
        self.config = config

        self.queen = QueenAnt(config)
        self.workers: List[WorkerAnt] = []
        self.soldiers: List[SoldierAnt] = []
        self.larvae: List[Larva] = []
        self.pupae: List[Larva] = []

        self.death_stats = DeathStatistics()
        self.events_log = []  # НОВОЕ: лог событий

        self.food_storage = config.initial_food
        self.day = 0

        self._initialize_colony()

    def _initialize_colony(self) -> None:
        print(f"Создаем колонию '{self.name}'...")
        for _ in range(self.config.initial_workers):
            self.workers.append(WorkerAnt(self.config))

    def add_larva(self, count: int = 1) -> None:
        for _ in range(count):
            self.larvae.append(Larva(self.config))

    def _process_pupae(self) -> None:
        remaining_pupae = []
        newly_hatched = []

        for pupa in self.pupae:
            if not pupa.is_alive():
                if pupa.state == AntState.DEAD and pupa.death_cause:
                    self.death_stats.record_death(pupa, pupa.death_cause, self.day)
                continue

            pupa.work()
            pupa.age_one_step(self.day)

            if pupa.growth_progress >= self.config.pupa_growth_duration:
                new_ant = self._create_ant_from_pupa(pupa)
                if new_ant:
                    newly_hatched.append(new_ant)
                    print(f"🎉 {new_ant.ant_type} вылупился из куколки!")
            else:
                remaining_pupae.append(pupa)

        self.pupae = remaining_pupae

        if newly_hatched:
            self._print_hatching_stats(newly_hatched)

    def _create_ant_from_pupa(self, pupa: Larva):
        if pupa.future_type == "worker":
            new_ant = WorkerAnt(self.config)
            self.workers.append(new_ant)
            return new_ant
        elif pupa.future_type == "soldier":
            new_ant = SoldierAnt(self.config)
            self.soldiers.append(new_ant)
            return new_ant
        return None

    def _print_hatching_stats(self, newly_hatched: List) -> None:
        stats = {"worker": 0, "soldier": 0}

        for ant in newly_hatched:
            if isinstance(ant, WorkerAnt):
                stats["worker"] += 1
            elif isinstance(ant, SoldierAnt):
                stats["soldier"] += 1

        print(f"\nВылупилось: рабочих={stats['worker']}, "
              f"солдат={stats['soldier']}")

    def simulate_day(self) -> None:
        self.day += 1
        print(f"\n{'=' * 50}")
        print(f"День {self.day}")
        print(f"{'=' * 50}")

        self._check_for_events()

        total_food = self._collect_food()

        self._feed_colony()

        eggs_laid = self.queen.work()
        if eggs_laid > 0:
            self.add_larva(eggs_laid)

        self._process_larvae()

        self._process_pupae()

        self._age_colony()

        if self.config.show_detailed_stats:
            self.death_stats.print_daily_deaths(self.day)

        self._print_statistics()

    def _check_for_events(self) -> None:
        if (self.day >= self.config.min_days_for_attack and
                random.random() < self.config.attack_chance):
            attack_event = AttackEvent(self.config)
            self._handle_attack_event(attack_event)

    def _handle_attack_event(self, attack_event: AttackEvent) -> None:
        print(f"\nСОБЫТИЕ: {attack_event.get_description()}")

        result = attack_event.execute(self)

        print(result["message"])

        if result["food_lost"] > 0:
            print(f"Потеряно пищи: {result['food_lost']}")
            print(f"Остаток пищи: {self.food_storage}")

        if result["ants_lost"]:
            ants_by_type = {}
            for ant in result["ants_lost"]:
                ant_type = ant.ant_type
                ants_by_type[ant_type] = ants_by_type.get(ant_type, 0) + 1

            print("Потери среди муравьев:")
            for ant_type, count in ants_by_type.items():
                print(f"  {ant_type}: {count}")

            for ant in result["ants_lost"]:
                if ant.death_cause:
                    self.death_stats.record_death(ant, ant.death_cause, self.day)

        event_log = {
            "day": self.day,
            "type": "attack",
            "success": result["success"],
            "food_lost": result["food_lost"],
            "ants_lost": len(result["ants_lost"]),
            "description": result["message"]
        }
        self.events_log.append(event_log)

        print(f"Солдаты в колонии: {self._count_live_ants(self.soldiers)}")

        if len(self.soldiers) == 0 and self.day >= self.config.min_days_for_attack:
            print("ВНИМАНИЕ: В колонии не осталось солдат для защиты!")

    def _collect_food(self) -> int:
        total_food = 0
        dead_workers = []

        for i, worker in enumerate(self.workers):
            if worker.is_alive():
                food = worker.work()
                total_food += food
            else:
                dead_workers.append((i, worker))

        for i, worker in reversed(dead_workers):
            self.workers.pop(i)
            if worker.death_cause:
                self.death_stats.record_death(worker, worker.death_cause, self.day)
            print(f"Рабочий муравей умер (причина: {worker.death_cause})")

        self.food_storage += total_food
        print(f"\nСобрано пищи: {total_food}. Всего в хранилище: {self.food_storage}")
        return total_food

    def _feed_colony(self) -> None:
        queen_food_needed = 3
        if self.food_storage >= queen_food_needed:
            self.queen.receive_food(queen_food_needed)
            self.food_storage -= queen_food_needed
            print(f"👑 Королева получила {queen_food_needed} единиц пищи")

        for larva in self.larvae:
            if self.food_storage >= 1:
                larva.feed(food_amount=15)
                self.food_storage -= 1

        all_adults = self.workers + self.soldiers
        for ant in all_adults:
            if self.food_storage >= 1 and ant.is_alive():
                ant.feed(food_amount=10)
                self.food_storage -= 1

    def _process_larvae(self) -> None:
        dead_larvae = []
        larvae_to_pupate = []

        for i, larva in enumerate(self.larvae):
            if not larva.is_alive():
                dead_larvae.append((i, larva))
                continue

            larva.work()
            larva.age_one_step(self.day)

            if not larva.is_alive():
                dead_larvae.append((i, larva))
            elif larva.state == AntState.PUPA:
                dead_larvae.append((i, larva))
                larvae_to_pupate.append(larva)

        for i, larva in reversed(dead_larvae):
            self.larvae.pop(i)
            if larva.state == AntState.DEAD and larva.death_cause:
                self.death_stats.record_death(larva, larva.death_cause, self.day)

        self.pupae.extend(larvae_to_pupate)

    def _age_colony(self) -> None:
        was_alive = self.queen.is_alive()
        self.queen.age_one_step(self.day)
        if was_alive and not self.queen.is_alive() and self.queen.death_cause:
            self.death_stats.record_death(self.queen, self.queen.death_cause, self.day)

        for ant_list in [self.workers, self.soldiers]:
            dead_ants = []
            for ant in ant_list:
                was_alive = ant.is_alive()
                ant.age_one_step(self.day)
                if was_alive and not ant.is_alive() and ant.death_cause:
                    self.death_stats.record_death(ant, ant.death_cause, self.day)
                    dead_ants.append(ant)

            for dead_ant in dead_ants:
                if dead_ant in ant_list:
                    ant_list.remove(dead_ant)

    def _print_statistics(self) -> None:
        print(f"\nСтатистика колонии '{self.name}':")
        print(f"Королева: здоровье={self.queen.health}, возраст={self.queen.age}")
        print(f" Рабочие: {self._count_live_ants(self.workers)}")
        print(f"Солдаты: {self._count_live_ants(self.soldiers)}")

        larva_stats = self._get_larva_type_stats()
        print(f"Личинки: {len(self.larvae)} ({larva_stats})")
        print(f"Куколки: {len(self.pupae)}")
        print(f"Запас пищи: {self.food_storage}")
        print(f"Всего живых муравьев: {self.get_total_ants()}")
        print(f"Всего смертей: {self.death_stats.total_deaths}")

        if self.events_log:
            recent_events = [e for e in self.events_log if e["day"] == self.day]
            if recent_events:
                print(f"События сегодня: {len(recent_events)}")

        if self.larvae:
            print(f"\nБудущее поколение личинок:")
            worker_count = len([l for l in self.larvae if l.future_type == "worker"])
            soldier_count = len([l for l in self.larvae if l.future_type == "soldier"])

            print(f"Будущих рабочих: {worker_count}")
            print(f"Будущих солдат: {soldier_count}")

    def _get_larva_type_stats(self) -> str:
        stats = {"worker": 0, "soldier": 0}

        for larva in self.larvae:
            if larva.future_type in stats:
                stats[larva.future_type] += 1

        return f"будущих рабочих: {stats['worker']}, будущих солдат: {stats['soldier']}"

    def _count_live_ants(self, ants_list: List) -> int:
        return len([ant for ant in ants_list if ant.is_alive()])

    def get_total_ants(self) -> int:
        total = 1 if self.queen.is_alive() else 0
        total += self._count_live_ants(self.workers)
        total += self._count_live_ants(self.soldiers)
        return total

    def is_alive(self) -> bool:
        return self.queen.is_alive() and self.get_total_ants() > 0

    def get_statistics(self) -> Dict[str, Any]:
        larva_stats = {"worker": 0, "soldier": 0}
        for larva in self.larvae:
            if larva.future_type in larva_stats:
                larva_stats[larva.future_type] += 1

        death_summary = self.death_stats.get_summary()

        return {
            "name": self.name,
            "day": self.day,
            "queen": {
                "health": self.queen.health,
                "age": self.queen.age,
                "eggs_laid": self.queen.eggs_laid,
                "is_alive": self.queen.is_alive(),
                "death_info": self.queen.get_death_info() if not self.queen.is_alive() else None
            },
            "population": {
                "workers": self._count_live_ants(self.workers),
                "soldiers": self._count_live_ants(self.soldiers),
                "larvae": len(self.larvae),
                "pupae": len(self.pupae),
                "total_live": self.get_total_ants(),
                "total_ever_created": self.get_total_ants() + death_summary["total_deaths"]
            },
            "larva_types": larva_stats,
            "death_statistics": death_summary,
            "resources": {
                "food": self.food_storage
            },

            "events": {
                "total_events": len(self.events_log),
                "attack_events": len([e for e in self.events_log if e["type"] == "attack"]),
                "successful_defenses": len([e for e in self.events_log if e.get("success", False)]),
                "recent_events": self.events_log[-5:] if self.events_log else []
            }
        }

    def print_final_statistics(self):
        print("")
        print("ИТОГОВАЯ СТАТИСТИКА КОЛОНИИ")
        print("")

        print(f"\nКолония: {self.name}")
        print(f"Дней существования: {self.day}")
        print(f"Королева: {self.queen.get_death_info() if not self.queen.is_alive() else 'жива'}")

        if self.queen.is_alive():
            print(f"   • Возраст: {self.queen.age} дней")
            print(f"   • Здоровье: {self.queen.health}")
            print(f"   • Отложено яиц: {self.queen.eggs_laid}")

        self.death_stats.print_statistics()

        if self.events_log:
            print(f"\n📊 События колонии:")
            attack_events = [e for e in self.events_log if e["type"] == "attack"]
            if attack_events:
                print(f"  Атак на колонию: {len(attack_events)}")
                successful = len([e for e in attack_events if e.get("success", False)])
                print(f"  Успешно отражено: {successful}")
                print(f"  Потеряно муравьев в атаках: {sum(e.get('ants_lost', 0) for e in attack_events)}")
                print(f"  Потеряно пищи в атаках: {sum(e.get('food_lost', 0) for e in attack_events)}")