import pandas as pd
from pathlib import Path
import sys

pd.options.mode.copy_on_write = True


def read_file():
    data_dir = Path('./logs')
    data_dir.exists() or data_dir.mkdir()

    data_file = data_dir / 'history.csv'

    if not data_file.exists() and not data_file.is_file():
        raise FileNotFoundError('Не найден файл с данными, выход...')

    dtypes = {
        "Symbol": "category",
        "Type": "category",
        "Side": "category",
        "Status": "category",
        "Qty": "float",
        "Price": "float"
    }

    data = pd.read_csv(data_file, dtype=dtypes)

    data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms')

    data.set_index('Timestamp')

    return data


def handle_group(grouped, group: tuple) -> pd.DataFrame:
    group = grouped.get_group(group)

    duplicates = group['OrderID'].duplicated(keep='first')

    if not all(duplicates):
        group = group.drop_duplicates(subset='OrderID')

    return group


if __name__ == '__main__':
    try:
        data = read_file()
    except FileNotFoundError as e:
        print(e)
        sys.exit()

    data.insert(len(data.columns), 'Row total', data['Qty'] * data['Price'])

    multi_index = data.groupby(by=['Side', 'Status'])

    try:
        sell_filled = handle_group(multi_index, ('SELL', 'FILLED'))
        buy_filled = handle_group(multi_index, ('BUY', 'FILLED'))
    except KeyError:
        print('\n***** Ещё нет выполненных LIMIT ордеров *****\n')
        sys.exit()

    print('\nВыполенные ордера на покупку')
    print(buy_filled)

    buy_total = buy_filled['Row total'].sum()

    print(f'Всего вложено в покупку: {buy_total}')

    print('\nВыполенные ордера на продажу')
    print(sell_filled)

    sell_total = sell_filled['Row total'].sum()

    print(f'Всего получено при продаже: {sell_total}')

    totals = multi_index.sum('Row total')

    print(f'\nДоходность данного предприятия: {sell_total - buy_total}')

    # print(totals)

    # buy_amount = totals.loc[(
    #     slice('BUY'), slice('FILLED')), 'Row total'].values

    # print(f'Вложено в покупку {buy_amount}')
