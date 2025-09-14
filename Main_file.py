import pandas as pd
import numpy as np


# Шлях до файлів
file1_path = 'LTV.csv'
file2_path = 'Spend.csv'

# Розрахунок LTV
print("--- Починаємо розрахунок LTV (Завдання 1.1) ---")

# Завантажуємо дані про транзакції
try:
    transactions_df = pd.read_csv(file1_path)
except FileNotFoundError:
    print(f"Помилка: Файл '{file1_path}' не знайдено. Перевірте шлях до файлу.")
    exit()

# Очищення даних: залишаємо тільки успішні транзакції
valid_transactions_df = transactions_df[transactions_df['refunded'] == False].copy()
print(f"Завантажено {len(transactions_df)} транзакцій. Після фільтрації повернень залишилось: {len(valid_transactions_df)}")

# Розрахунок LTV для 'tenwords_1w_7.99_7free'
df_7_99 = valid_transactions_df[valid_transactions_df['product_id'] == 'tenwords_1w_7.99_7free']
total_payments_7_99 = len(df_7_99)
unique_users_7_99 = df_7_99['user_id'].nunique()
avg_payments_7_99 = total_payments_7_99 / unique_users_7_99 if unique_users_7_99 > 0 else 0
ltv_7_99 = avg_payments_7_99 * 7.99
print(f"\nПродукт 'tenwords_1w_7.99_7free':")
print(f"  - Розрахований LTV: ${ltv_7_99:.2f}")

# Розрахунок LTV для 'tenwords_1w_9.99_offer'
df_9_99 = valid_transactions_df[valid_transactions_df['product_id'] == 'tenwords_1w_9.99_offer']
total_payments_9_99 = len(df_9_99)
unique_users_9_99 = df_9_99['user_id'].nunique()
avg_payments_9_99 = total_payments_9_99 / unique_users_9_99 if unique_users_9_99 > 0 else 0
ltv_9_99 = 0.5 + (avg_payments_9_99 - 1) * 9.99 if avg_payments_9_99 >= 1 else 0.5
print(f"Продукт 'tenwords_1w_9.99_offer':")
print(f"  - Розрахований LTV: ${ltv_9_99:.2f}")

# LTV для 'tenwords_lifetime_limited_49.99' - це просто його ціна
ltv_lifetime = 49.99
print(f"Продукт 'tenwords_lifetime_limited_49.99':")
print(f"  - LTV (одноразовий платіж): ${ltv_lifetime:.2f}")

# Створюємо словник з розрахованими LTV для подальшого використання
LTV_MAP = {
    'tenwords_lifetime_limited_49.99': ltv_lifetime,
    'tenwords_1w_7.99_7free': ltv_7_99,
    'tenwords_1w_9.99_offer': ltv_9_99
}
print("\n--- Розрахунок LTV завершено. ---")


# Підготовка даних для Power BI
print("\n--- Починаємо підготовку фінального файлу для Power BI ---")

# 2.1. Визначаємо дату залучення та LTV для кожного користувача
valid_transactions_df['purchase_date'] = pd.to_datetime(valid_transactions_df['purchase_date'])
valid_transactions_df.sort_values(by=['user_id', 'purchase_date'], inplace=True)
acquisitions_df = valid_transactions_df.drop_duplicates(subset='user_id', keep='first').copy()
acquisitions_df['ltv'] = acquisitions_df['product_id'].map(LTV_MAP)
print(f"Визначено {len(acquisitions_df)} унікальних користувачів, що здійснили покупку.")

# Агрегуємо прогнозований дохід (Total LTV)
revenue_df = acquisitions_df.groupby(['purchase_date', 'media_source', 'country_code']).agg(
    total_ltv=('ltv', 'sum'),
    new_users=('user_id', 'count')
).reset_index()
revenue_df.rename(columns={'purchase_date': 'date'}, inplace=True)
print("Агреговано прогнозований дохід (Total LTV).")

# Завантаження та підготовка даних про витрати (Spend)
try:
    costs_df = pd.read_csv(file2_path)
    # Перетворюємо дату в правильний формат
    costs_df['date'] = pd.to_datetime(costs_df['date'])
    # На випадок, якщо є дублікати, агрегуємо витрати
    costs_df = costs_df.groupby(['date', 'media_source', 'country_code']).agg(
        cost=('cost', 'sum')
    ).reset_index()
    print(f"Завантажено та оброблено дані про витрати з '{file2_path}'.")
except FileNotFoundError:
    print(f"Помилка: Файл '{file2_path}' не знайдено. Створюємо порожню таблицю витрат.")
    costs_df = pd.DataFrame(columns=['date', 'media_source', 'country_code', 'cost'])

# 2.4. Об'єднання даних про доходи та витрати
final_df = pd.merge(
    revenue_df,
    costs_df,
    on=['date', 'media_source', 'country_code'],
    how='outer'
)

# Заповнюємо пропуски нулями
final_df[['total_ltv', 'new_users', 'cost']] = final_df[['total_ltv', 'new_users', 'cost']].fillna(0)
print("Об'єднано дані про доходи та витрати.")

# Розрахунок ROMI (Буде окремо порахований у Power BI)
final_df['romi'] = np.where(
    final_df['cost'] > 0,
    (final_df['total_ltv'] - final_df['cost']) / final_df['cost'],
    0
)
print("Розраховано ROMI.")

# Збереження файлу для аналізу
output_filename = 'data_for_powerbi.csv'
final_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
print(f"\n--- Підготовку завершено! ---")
print(f"Фінальний файл '{output_filename}' збережено.")
print("Колонки у файлі:", final_df.columns.tolist())