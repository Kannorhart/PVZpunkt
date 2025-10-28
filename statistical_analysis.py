import json
from scipy import stats
import numpy as np
import os

def perform_statistical_tests():
    """
    Загружает результаты моделирования и выполняет статистические тесты
    для сравнения различных сценариев.
    """
    if not os.path.exists('результаты_моделирования.json'):
        print("Файл 'результаты_моделирования.json' не найден.")
        return

    with open('результаты_моделирования.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Извлечение данных
    scenarios = data['сценарии']
    mean_waiting_times_per_replication = data.get('mean_waiting_times_per_replication')
    if not mean_waiting_times_per_replication:
        print("Ключ 'mean_waiting_times_per_replication' не найден в файле результатов.")
        return

    served_clients = data['обслуженные_клиенты']
    dropout_clients = data['клиенты_отказались']

    # --- T-тест для среднего времени ожидания ---
    print("--- T-тест для среднего времени ожидания (сравнение с базовым сценарием) ---")
    base_mean_waiting_times = mean_waiting_times_per_replication[0]
    for i in range(1, len(scenarios)):
        scenario_name = scenarios[i]
        scenario_mean_waiting_times = mean_waiting_times_per_replication[i]

        # Выполнение t-теста
        t_stat, p_value = stats.ttest_ind(base_mean_waiting_times, scenario_mean_waiting_times, equal_var=False)

        print(f"\nСценарий: {scenario_name}")
        print(f"  Среднее время ожидания (базовый): {np.mean(base_mean_waiting_times):.3f}")
        print(f"  Среднее время ожидания ({scenario_name}): {np.mean(scenario_mean_waiting_times):.3f}")
        print(f"  T-статистика: {t_stat:.3f}")
        print(f"  P-значение: {p_value:.5f}")

        if p_value < 0.05:
            print("  Результат: Разница статистически значима.")
        else:
            print("  Результат: Разница не является статистически значимой.")

    # --- Z-тест для долей отказов ---
    print("\n--- Z-тест для долей отказов (сравнение с базовым сценарием) ---")
    base_total_clients = served_clients[0] + dropout_clients[0]
    base_dropouts = dropout_clients[0]

    for i in range(1, len(scenarios)):
        scenario_name = scenarios[i]
        total_clients = served_clients[i] + dropout_clients[i]
        dropouts = dropout_clients[i]

        # Пропорции
        p1 = base_dropouts / base_total_clients
        p2 = dropouts / total_clients

        # Объединенная пропорция
        p_pool = (base_dropouts + dropouts) / (base_total_clients + total_clients)

        # Z-статистика
        se = np.sqrt(p_pool * (1 - p_pool) * (1/base_total_clients + 1/total_clients))
        z_stat = (p1 - p2) / se

        # P-значение
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))

        print(f"\nСценарий: {scenario_name}")
        print(f"  Доля отказов (базовый): {p1:.3f}")
        print(f"  Доля отказов ({scenario_name}): {p2:.3f}")
        print(f"  Z-статистика: {z_stat:.3f}")
        print(f"  P-значение: {p_value:.5f}")

        if p_value < 0.05:
            print("  Результат: Разница в долях отказов статистически значима.")
        else:
            print("  Результат: Разница не является статистически значимой.")

if __name__ == "__main__":
    perform_statistical_tests()
