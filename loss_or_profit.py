from pathlib import Path
import pandas as pd
import sys


def read_file() -> pd.DataFrame:
    log_dir = Path('./logs')
    log_dir.exists() or log_dir.mkdir()

    log_file = log_dir / 'history.csv'

    if not log_file.exists() and not log_file.is_file():
        raise FileExistsError(f'No log file {log_file} found')

    dtypes = {
        "Symbol": "category",
        "Type": "category",
        "Side": "category",
        "Status": "category",
        "Qty": "float",
        "Price": "float"
    }

    data = pd.read_csv(log_file, dtype=dtypes)

    data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms')

    # data.set_index('Timestamp')

    return data


def split_data(data: pd.DataFrame) -> pd.DataFrame:
    filled = data['Status'] == 'FILLED'
    new = data['Status'] == 'NEW'

    ready = data[filled]
    working = data[new]

    return {'filled': ready, 'new': working}


def create_parts(data_splitted: pd.DataFrame) -> pd.DataFrame:
    grouped = data_splitted.groupby(['Type', 'Side'])

    sells = grouped.get_group(('LIMIT', 'SELL'))
    buys = grouped.get_group(('LIMIT', 'BUY'))
    base = grouped.get_group(('MARKET', 'BUY'))

    return {'sells': sells, 'buys': buys, 'base': base}


def handle_data(part: pd.DataFrame) -> pd.DataFrame:
    part.set_index('Timestamp', inplace=True)
    part.insert(len(part.columns), 'TOTAL', part['Qty'] * part['Price'])
    # TODO: Удалть дупликаты
    part.drop_duplicates(subset='OrderID', keep='first', inplace=True)

    return part


def get_total(data: pd.DataFrame) -> float:
    totals = data['TOTAL']

    return totals.sum()


def display_data(name: str, data: pd.DataFrame):
    print(f'\n{name}\n')
    print(data)


def main():
    raw_data = read_file()

    filled = split_data(raw_data)['filled']
    sells = create_parts(filled)['sells']
    buys = create_parts(filled)['buys']
    base = create_parts(filled)['base']

    sell_data = handle_data(sells)
    buy_data = handle_data(buys)

    base.set_index('Timestamp', inplace=True)
    base.insert(len(base.columns), 'TOTAL', base['Price'])

    display_data('Базовая покупка:', base)
    base_total = get_total(base)
    print(f'Затраты на базовую покупку: {base_total}')
    display_data('Выполненные ордера на покупку:', buy_data)
    buy_total = get_total(buy_data)
    print(f'Итог выполненных ордеров на покупку: {buy_total}')

    display_data('Выполненные ордера на продажу:', sell_data)
    sell_total = get_total(sell_data)
    print(f'Итог выполненных ордеров на продажу: {sell_total}')

    print(
        f'\nДоходность данного замеса: {sell_total - (buy_total + base_total)}\n')
    # print(sell_data)
    # print(buy_data)
    # print(base)


if __name__ == '__main__':
    main()
