import pandas as pd

# Загрузка данных из JSON файла
df = pd.read_json('trial_task.json')

# Преобразование вложенных данных в DataFrame
df = pd.json_normalize(
    df.to_dict('records'), 'products',
    ['order_id', 'warehouse_name', 'highway_cost'])

# Вычисляем общее количество товаров в заказе и тариф доставки для каждого склада
df['total_quantity'] = df.groupby('order_id')['quantity'].transform('sum')
df['tariff'] = df['highway_cost'] / df['total_quantity']
print(df.groupby('warehouse_name')['tariff'].mean())

# Вычисляем доход, расход и прибыль для каждого товара
df['income'] = df['price'] * df['quantity']
df['expenses'] = df['tariff'] * df['quantity']
df['profit'] = df['income'] - df['expenses']

# Суммируем количество, доход, расход и прибыль по каждому товару
summary = df.groupby('product').agg(
    {'quantity': 'sum', 'income': 'sum', 'expenses': 'sum', 'profit': 'sum'})
print(summary)

# Создаем таблицу с идентификатором заказа и прибылью от заказа
order_profit = df.groupby('order_id')['profit'].sum().reset_index().rename(
    columns={'profit': 'order_profit'})

# Вычисляем среднюю прибыль заказов
average_order_profit = order_profit['order_profit'].mean()
print(order_profit)
print("Средняя прибыль заказов: ", average_order_profit)

# Вычисляем процент прибыли каждого продукта к общей прибыли склада
warehouse_profit = df.groupby(['warehouse_name', 'product'])[
    'profit'].sum().reset_index()
warehouse_profit['percent_profit_product_of_warehouse'] = \
    warehouse_profit.groupby('warehouse_name')['profit'].transform(
        lambda x: x / x.sum() * 100)

# Сортируем процент прибыли по убыванию
warehouse_profit = warehouse_profit.sort_values(
    'percent_profit_product_of_warehouse', ascending=False)

# Проверяем, что 'percent_profit_product_of_warehouse' имеет числовой тип
warehouse_profit['percent_profit_product_of_warehouse'] = pd.to_numeric(
    warehouse_profit['percent_profit_product_of_warehouse'], errors='coerce')
print(
    warehouse_profit[['warehouse_name', 'product', 'profit',
                      'percent_profit_product_of_warehouse']])

# Вычисляем накопленный процент
warehouse_profit['accumulated_percent_profit_product_of_warehouse'] = \
    warehouse_profit.groupby('warehouse_name')[
        'percent_profit_product_of_warehouse'].cumsum()
print(
    warehouse_profit[['warehouse_name', 'product', 'profit',
                      'percent_profit_product_of_warehouse',
                      'accumulated_percent_profit_product_of_warehouse']])


# Назначаем категории на основании накопленного процента
def assign_category(percentage):
    if percentage <= 70:
        return 'A'
    elif percentage <= 90:
        return 'B'
    else:
        return 'C'


warehouse_profit['category'] = warehouse_profit[
    'accumulated_percent_profit_product_of_warehouse'].apply(assign_category)

print(
    warehouse_profit[['warehouse_name', 'product', 'profit',
                      'percent_profit_product_of_warehouse',
                      'accumulated_percent_profit_product_of_warehouse',
                      'category']])
