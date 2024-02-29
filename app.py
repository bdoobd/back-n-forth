from src.coin import Coin
from src.filter import Filter
from src.wallet import Wallet
import config.config as config
import pandas as pd
import sys
from pprint import pprint

asset_found = False

if __name__ == '__main__':
    asset = Coin()

    while not asset_found:
        try:
            coin = input('Укажи базовый актив для работы: ')
            if asset.check_asset_exist(coin):
                asset.set_coin(coin)
                asset_found = True
            else:
                print('Выбран не существующий актив, попробуй ещё раз')
        except KeyboardInterrupt:
            print('\n\nTerminating script ...')
            sys.exit()
    print('Продолжаем выполнение скрипта')

    # TODO: Из данных о активе вытащить значения фильтров
    filter = Filter(asset.get_coin())

    print(filter.displayFilters())
    # TODO: Запросить количество покупаемых активов

    while True:
        try:
            amount = float(
                input('Задай количество для покупки (дробный знак - точка): '))
            break
        except ValueError:
            print('Введено не верное значение, попробуй ещё раз\n')
            continue

    # TODO: Проверить удовлетворяют ли указанное количество фильтрам актива

    try:
        filter.check_amount(amount)
    except Exception as e:
        print(e)
    # TODO: Расчитать стоимость запрашиваемого количесва
    current_price = Coin.get_current_price(asset.get_coin())
    print(f'Текущая стоимость актива: {current_price: >14}')
    print(
        f'Сумма для покупки: {amount * current_price: >21}')

    amount_accept = input('\nУстраивает ли такая стоимость? Y/N: ')
    if amount_accept.upper() == 'Y':
        print(f'Создаём базовый ордер на количество {amount} шт')
    else:
        print('Значение не устроило, скрипт заканчивает работу ...')
        sys.exit()

    # TODO: Проверить есть ли на балансе достаточная сумма
    wallet = Wallet()
    balance = wallet.get_balance(config.TRADE_PAIR)

    asset_balance_free = balance['free']
    asset_balance_locked = balance['locked']

    balance_str = f'\nБаланс актива {config.TRADE_PAIR} в кошельке:\n'\
        f'{"": >10}Свободно: {asset_balance_free: >17}\n'\
        f'{"": >10}Зарезервировано: {asset_balance_locked: >5}\n'

    print(balance_str)

    # TODO: Создать сетку с помощью pandas на покупку и продажу
    data = [
        {'процент': f'{0.03:.1%}', 'количество': f'{amount / 3}',
            'стоимость': f'{current_price * 1.03}'},
        {'процент': f'{0.02:.1%}', 'количество': f'{amount / 3}',
            'стоимость': f'{current_price * 1.02}'},
        {'процент': f'{0.01:.1%}', 'количество': f'{amount / 3}',
            'стоимость': f'{current_price * 1.01}'},
        {'процент': f'0.0%', 'количество': amount, 'стоимость': f'{current_price}'},
        {'процент': f'-{0.01:.1%}', 'количество': f'{amount / 3}',
            'стоимость': f'{current_price * 0.99}'},
        {'процент': f'-{0.02:.1%}', 'количество': f'{amount / 3}',
            'стоимость': f'{current_price * 0.98}'},
        {'процент': f'-{0.03:.1%}', 'количество': f'{amount / 3}',
            'стоимость': f'{current_price * 0.97}'},

    ]
    mesh = pd.DataFrame(
        data, index=['продажа', 'продажа', 'продажа', 'текушая покупка', 'покупка', 'покупка', 'покупка'])
    # mesh = pd.DataFrame(data, index=[1, 2, 3, 4, 5, 6, 7])
    print('\nПример сетки')
    print(mesh)
