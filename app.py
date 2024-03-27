from src.coin import Coin
from src.filter import Filter
from src.wallet import Wallet
from src.mesh import Mesh
from src.order import Order
from src.trade_log import Trade_Log
import config.config as config
import pandas as pd
import sys
from pprint import pprint

from src.access import Access


def ask_coin():
    while True:
        try:
            coin = input('Укажи базовый актив для работы: ')
            if asset.check_asset_exist(coin):
                asset.register_coin(coin)
                break
            else:
                print('Выбран не существующий актив, попробуй ещё раз')
        except KeyboardInterrupt:
            print('\n\nСкрипт закончил работу ...')
            sys.exit()
    print(f'Продолжаем выполнение скрипта с парой {asset.get_coin(): >10}')


def check_coin_level(coin: Coin):
    return coin.check_price_level()


if __name__ == '__main__':
    asset = Coin()

    ask_coin()

    try:
        check_coin_level(coin=asset)
    except ValueError as e:
        print(e)
        confirm_level = input('Хочешь продолжить? Y/N: ')
        if not confirm_level.upper() == 'Y':
            sys.exit()

    filter = Filter(asset.get_coin())

    print(filter.displayFilters())

    # TODO: Попробовать вынести блоки кода в отдельные функции
    while True:
        try:
            amount = float(
                input('Задай количество для покупки (дробный знак - точка): '))

            if filter.check_lot_size(amount):
                print(
                    '\nЗаданное количество для покупки удовлетворяет фильтру LOT_SIZE\n')

            part_amount = amount / config.ORDERS_AMOUNT
            print(
                f'\nСоздаём сетку продажи на {config.ORDERS_AMOUNT} позиций по {part_amount} {asset.get_base()} на позицию\n')

            if not filter.check_notional(
                    part_amount * float(asset.get_average_price())):
                raise Exception(
                    f'ВНИМАНИЕ!!! Количество актива на продажу для сетки не удовлетворяет фильтру NOTIONAL, при средней стоимости актива на продажу должно быть выставлено не менее {round(float(filter.notional()["minNotional"]) / float(asset.get_average_price()), 0)} {asset.get_base()}\n')
            filter.check_lot_size(part_amount)

        except ValueError:
            print(
                '\nВведено не верное значение количества для покупки, попробуй ещё раз\n')
            continue
        except KeyboardInterrupt:
            print('\nВызвано прерывание работы скрирта, выход ...\n')
            sys.exit()
        except Exception as e:
            print(e)
            continue

        mesh = Mesh(base_amount=amount, filters=filter)

        try:
            buy_price = float(
                input('Укажи стоимость базового актива для покупки (LIMIT ORDER): '))

            filter.check_price(buy_price)
            if not filter.check_notional(amount * buy_price):
                raise Exception(
                    'Запрашиваемая стоимость для покупки не удовлетворяеь фильтру NOTIONAL')

            sells = mesh.create_sell_rows(buy_price)
            buys = mesh.create_buy_rows(buy_price)

            pprint(sells)
            pprint(buys)

            for item in sells:
                if not filter.check_notional(item['amount'] * item['price']):
                    raise Exception(
                        f'Количество {asset.get_base()} {item["amount"]} для продажи по цене {item["price"]} не удовлетворяет фильтру NOTIONAL\n')

            for item in buys:
                if not filter.check_notional(item['amount'] * item['price']):
                    raise Exception(
                        f'Количество {asset.get_base()} {item["amount"]} для покупки по цене {item["price"]} не удовлетворяет фильтру NOTIONAL\n')

            break
        except ValueError:
            print('\nУказана не верная цена для покупки, попробуй ещё раз\n')
            continue
        except KeyboardInterrupt:
            print('\nВызвано прерывание работы скрирта, выход ...\n')
            sys.exit()
        except Exception as e:
            print(e)
            continue

    print(f'\nДля работы скрипта получены следуюшие данные:\n')
    print(f'Название торговой пары: {asset.get_coin(): >26}')
    print(f'Количество для покупки {asset.get_base()}: {amount: >21}')
    print(f'Стоимость актива для покупки: {buy_price: >20}')
    print(
        f'Обшие затраты на базовую закупку {config.TRADE_PAIR}: {amount * buy_price: >11}\n')

    print(Trade_Log.get_balance_string(asset.get_base()))

    acceptance = input('\nУстраивает ли данная стратегия? Y/N: ')
    if not acceptance.upper() == 'Y':
        print('\nСтратегия не устроила, скрипт заканчивает работу ...\n')
        sys.exit()

    mesh_buy_price = amount * float(asset.get_average_price())
    for item in buys:
        mesh_buy_price += float(item['price'])

    print(f'Общая потребность в квотируемом активе {mesh_buy_price}')

    wallet = Wallet()
    if not wallet.check_balance(asset=config.TRADE_PAIR, order_price=mesh_buy_price):
        print(
            f'Сумма ордеров на покупку {mesh_buy_price} превышает имеющуюся в распоряжении сумму')
        sys.exit()

    order = Order(asset.get_base())

    if order.create_limit_buy_order(
            amount=amount, price=buy_price):
        print(f'\nСоздаём сетку продажи актива {asset.get_base()}\n')
        for item in sells:
            part_order = order.create_limit_sell_order(
                amount=item['amount'], price=item['price'])

        for item in buys:
            part_order = order.create_limit_buy_order(
                amount=item['amount'], price=item['price'])
