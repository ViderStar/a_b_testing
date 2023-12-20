import pandas as pd
import matplotlib.pyplot as plt

from scipy.stats import ttest_ind

df = pd.read_csv('analytic_dataset.csv')
print(df.columns)
# Выделение тестовой когорты пользователей
test_cohort = df[
    ((df['locale'] == 'en') & (df['country'].isin(['US', 'NZ', 'AU', 'GB', 'IN', 'PH'])) |
     (df['locale'] == 'ru') & (df['country'] == 'RU')) &
    (df['tl'].between(4, 5)) &
    (pd.to_datetime(df['event_time']).between('2023-10-05 13:25:00', '2023-10-23 10:00:00')) &
    (df.index % 4 >= 2)
    ]

# Анализ результатов A/B-теста
# Сравнение конверсии в покупку между группами
old_design = df[df.index % 4 < 2]
new_design = df[df.index % 4 >= 2]

old_conversion_rate = (old_design['event_name'] == 'logic_purchase').mean()
new_conversion_rate = (new_design['event_name'] == 'logic_purchase').mean()

print(f'Конверсия в покупку для старого дизайна: {old_conversion_rate}')
print(f'Конверсия в покупку для нового дизайна: {new_conversion_rate}')

# Подготовка визуализации результатов
plt.bar(['Старый дизайн', 'Новый дизайн'], [old_conversion_rate, new_conversion_rate])
plt.ylabel('Конверсия в покупку')
plt.show()


def calculate_funnel_conversion(group):
    registration_count = group[group['event_name'] == 'start_session']['user_id'].nunique()
    onboarding_count = group[group['event_name'] == 'onb_page_showed']['user_id'].nunique()
    warming_up_count = group[group['event_name'] == 'warming_up_showed']['user_id'].nunique()
    dashboard_count = group[group['event_name'] == 'dashboard_showed']['user_id'].nunique()
    content_count = group[group['event_name'] == 'content_opened']['user_id'].nunique()
    purchase_count = group[group['event_name'] == 'logic_purchase']['user_id'].nunique()

    conversion_rates = {
        'Registration': onboarding_count / registration_count,
        'Onboarding': warming_up_count / onboarding_count,
        'Warming Up': dashboard_count / warming_up_count,
        'Dashboard': content_count / dashboard_count,
        'Content': purchase_count / content_count,
        'Purchase': purchase_count / registration_count
    }

    return conversion_rates


old_funnel_conversion = calculate_funnel_conversion(old_design)
new_funnel_conversion = calculate_funnel_conversion(new_design)

print('Конверсия воронки для старого дизайна:')
for step, conversion_rate in old_funnel_conversion.items():
    print(f'{step}: {conversion_rate}')

print('\nКонверсия воронки для нового дизайна:')
for step, conversion_rate in new_funnel_conversion.items():
    print(f'{step}: {conversion_rate}')


def plot_funnel_conversion(conversion_rates, title):
    steps = list(conversion_rates.keys())
    rates = list(conversion_rates.values())

    plt.bar(steps, rates)
    plt.title(title)
    plt.xlabel('Этапы воронки')
    plt.ylabel('Конверсия')
    plt.show()


plot_funnel_conversion(old_funnel_conversion, 'Конверсия воронки для старого дизайна')
plot_funnel_conversion(new_funnel_conversion, 'Конверсия воронки для нового дизайна')

import scipy.stats as stats

# Расчет p-value с использованием t-теста
t_stat, p_value = stats.ttest_ind(old_design['logic_purchase'], new_design['logic_purchase'], equal_var=False)

print(f"t-статистика: {t_stat}")
print(f"p-value: {p_value}")
# Анализ поведения пользователей
user_behavior = df.groupby('user_id')['event_name'].apply(list)
print(user_behavior)

old_users = old_design['user_id'].nunique()
new_users = new_design['user_id'].nunique()

print(f'Общее количество пользователей со старым дизайном: {old_users}')
print(f'Общее количество пользователей с новым дизайном: {new_users}')
total_users = test_cohort['user_id'].nunique()
print(f'Общее количество пользователей в тестовой когорте: {total_users}')

