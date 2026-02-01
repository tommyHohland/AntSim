import sys
import time
from core.config import SimulationConfig
from core.colony import AntColony


def print_welcome(config: SimulationConfig) -> None:
    print("=" * 60)
    print("         СИМУЛЯЦИЯ МУРАВЬИНОЙ КОЛОНИИ")
    print("=" * 60)
    print("\nКоролева откладывает яйца")
    print("Рабочие собирают пищу")
    print("Солдаты охраняют колонию")
    print("Личинки растут и превращаются в куколок")
    print("=" * 60)
    print("\n Параметры конфигурации:")
    print(f"  Шанс развития в рабочего: {config.worker_chance * 100:.0f}%")
    print(f"  Шанс развития в солдата: {config.soldier_chance * 100:.0f}%")
    print(f"  Шанс болезни: {config.disease_chance * 100:.0f}%")
    print(f"  Шанс травмы: {config.injury_chance * 100:.0f}%")
    print(f"  Шанс смерти от старости: {config.old_age_death_chance * 100:.0f}%")
    print("\nСлучайные события:")
    print(f"  Шанс атаки на колонию: {config.attack_chance * 100:.0f}% в день")
    print(f"  Первая атака возможна с дня: {config.min_days_for_attack}")
    print("=" * 60)


def main():
    config = SimulationConfig()

    print_welcome(config)

    if error := config.validate():
        print(f"Ошибка в конфигурации: {error}")
        return 1

    colony_name = input("\nВведите название колонии: ").strip() or "Антлантида"

    try:
        max_days_input = input("Сколько дней симулировать? (по умолчанию 30): ").strip()
        max_days = int(max_days_input) if max_days_input else 30

        auto_mode_input = input("Автоматический режим? (y/n, по умолчанию n): ").strip().lower()
        auto_mode = auto_mode_input == 'y' if auto_mode_input else False

        detailed_stats_input = input(
            "Показывать детальную статистику смертности? (y/n, по умолчанию y): ").strip().lower()
        config.show_detailed_stats = detailed_stats_input != 'n' if detailed_stats_input else True
    except ValueError:
        print("Неверный формат ввода, использую значения по умолчанию")
        max_days = 30
        auto_mode = False
        config.show_detailed_stats = True

    print(f"\nНачинаем симуляцию колонии '{colony_name}' на {max_days} дней...")
    colony = AntColony(colony_name, config)

    for day in range(max_days):
        colony.simulate_day()

        if not colony.is_alive():
            print(f"\n Колония '{colony_name}' погибла на день {colony.day}!")
            break

        if not auto_mode and day < max_days - 1:
            try:
                input("\n⏎ Нажмите Enter для следующего дня...")
            except KeyboardInterrupt:
                print("\n\nСимуляция прервана пользователем")
                break
        elif auto_mode:
            time.sleep(0.5)

    colony.print_final_statistics()

    stats = colony.get_statistics()

    print("\n" + "=" * 60)
    print("ДОПОЛНИТЕЛЬНАЯ СТАТИСТИКА")
    print("=" * 60)

    print(f"\n👥 Демографическая статистика:")
    print(f"  Всего создано муравьев: {stats['population']['total_ever_created']}")
    print(f"  Муравьев на старте: {config.initial_workers + 1}")
    print(f"  Муравьев в конце: {stats['population']['total_live']}")
    print(f"  Общая смертность: {stats['death_statistics']['total_deaths']}")

    if stats['population']['total_ever_created'] > 0:
        mortality_rate = (stats['death_statistics']['total_deaths'] / stats['population']['total_ever_created']) * 100
        print(f"  Уровень смертности: {mortality_rate:.1f}%")

    print(f"\nЛичинки:")
    print(f"  Всего личинок: {stats['population']['larvae']}")
    print(f"  Будущих рабочих: {stats['larva_types']['worker']}")
    print(f"  Будущих солдат: {stats['larva_types']['soldier']}")

    print(f"\nРесурсы:")
    print(f"  Остаток пищи: {stats['resources']['food']}")

    print(f"\nСтатистика событий:")
    print(f"  Всего событий: {stats['events']['total_events']}")
    print(f"  Атак на колонию: {stats['events']['attack_events']}")
    print(f"  Успешно отражено атак: {stats['events']['successful_defenses']}")

    if colony.is_alive():
        print(f"\nКолония '{colony_name}' успешно выжила!")
    else:
        print(f"\nКолония '{colony_name}' не выжила.")

    save_stats = input("\nСохранить статистику в файл? (y/n): ").strip().lower()
    if save_stats == 'y':
        try:
            with open(f"{colony_name}_statistics.txt", "w", encoding="utf-8") as f:
                f.write(f"Статистика колонии '{colony_name}'\n")
                f.write("=" * 50 + "\n")
                f.write(f"Дней: {stats['day']}\n")
                f.write(f"Всего создано муравьев: {stats['population']['total_ever_created']}\n")
                f.write(f"Смертей: {stats['death_statistics']['total_deaths']}\n")
                f.write(f"Остаток пищи: {stats['resources']['food']}\n")
                f.write(f"Атак на колонию: {stats['events']['attack_events']}\n")
                f.write(f"Успешно отражено атак: {stats['events']['successful_defenses']}\n")
                f.write("\nПричины смерти:\n")
                for cause, count in stats['death_statistics']['by_cause'].items():
                    f.write(f"  {cause}: {count}\n")
                f.write("\nПоследние события:\n")
                for event in stats['events']['recent_events']:
                    f.write(f"  День {event['day']}: {event['description']}\n")
            print(f"Статистика сохранена в файл {colony_name}_statistics.txt")
        except Exception as e:
            print(f"Ошибка при сохранении статистики: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())