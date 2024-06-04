from src.coin import Coin
from src.filter import Filter
from src.wallet import Wallet
from src.mesh import Mesh
from src.order import Order
from src.trade import Trade
from src.trade_log import Trade_Log
from src.check_order import Check_Order
import config.config as config
import pandas as pd
import sys
from pprint import pprint

from src.access import Access
from pathlib import Path
import json
import time


if __name__ == '__main__':
    check = Check_Order('ids.json')
    asset = Coin()
    if check.no_open_orders():
        asset.ask_coin()
        asset.check_coin_level()

        filter = Filter(coin=asset.get_coin())
        trade = Trade(coin=asset, filter=filter)
        wallet = Wallet(coin=asset)
        print(filter.displayFilters())

        while True:
            try:
                trade.set_base_volume(volume=trade.get_volume())
                trade.get_volume_part()

                mesh = Mesh(base_volume=trade.get_base_volume(),
                            filters=filter)
                mesh.set_part_volume(part_volume=trade.part_volume)

                current_price = asset.get_current_price(coin=asset.get_coin())
                mesh.create_sell_rows(current_price=current_price)
                mesh.create_buy_rows(current_price=current_price)

                amount_needed = (trade.get_base_volume() *
                                 current_price) + mesh.calculate_buy_mesh_amount()

                wallet.check_available_balance(total_price=amount_needed)
                break
            except KeyboardInterrupt:
                print('Выполнение скрипта прервано, заканчиваем работу...\n')
                sys.exit()
            except Exception as e:
                print(e)
                continue

        print(trade.show_summary(base_price=current_price))
        print(wallet.display_trade_balances())
        mesh.display_mesh(base_price=current_price)

        confirm_mesh = input(
            'Устраивает ли такая сетка, можем продолжать? [Y/N]: ')
        if not confirm_mesh.upper() == 'Y':
            print('Сетка не устроила, прерываем работу скрипта...')
            sys.exit()

        order = Order(asset.get_base())

        try:
            if order.create_test_market_buy_order(trade.get_base_volume()):
                base_receipt = order.create_market_buy_order(
                    trade.get_base_volume())
        except Exception as e:
            print('Ошибка при обработке базовой покупки')
            print(e)
            sys.exit()
        else:
            base_log = Trade_Log(base_receipt)
            base_log.write_market_order('base_order.json')

            base_price = order.get_base_price(base_receipt)

        mesh.create_sell_rows(current_price=base_price)
        mesh.create_buy_rows(current_price=base_price)

        ids = {f'{asset.get_base()}': order.place_mesh_orders(
            mesh.buys, mesh.sells)}

        log_ids = Trade_Log()
        log_ids.write_ids(ids)
    else:
        ids = check.read_log_file()

    # TODO: Вынести сюда обработку массива ID и соответственно
    # заказ выполеных ордеров
    # loop_orders(ids=ids)
    try:
        working_asset, working_orders = check.loop_orders(ids=ids)
    except ValueError as e:
        print(e)
        # FIXME: Добавить сюда exit? По идее в эту ветку не должны попадать
    print('=================================================')
    print(f'Работаем с массивом ордеров для актива {working_asset}')
    print('=================================================')

    while True:
        for working_order in working_orders:
            # FIXME: Придумать что то покрасивее, чем склеивание двух переменных, может добавить в класс?
            working_data = Order.ask_order(
                f'{working_asset}{config.TRADE_PAIR}', working_order)
            # print(json.dumps(working_data, indent=4))
            if check.check_order_filled(working_data):
                # TODO: Выставить соответствующий выполненному оппозитный ордер
                print(
                    f'Ордер {working_data["side"]} для актива {working_asset} выполнен для {working_data["executedQty"]} шт стоимостью {working_data["price"]}')
            else:
                print(
                    f'Ордер {working_data["side"]} для актива {working_asset} находится в ожидании для {working_data["executedQty"]} шт стоимостью {working_data["price"]}')

        time.sleep(10)

    sys.exit()
    # ===============================================================
    # ===============================================================

    def log_data():
        ids = check.read_log_file()
        ready = []
        opened = []
        failed = []

        if ids:
            print('Найдены идентификаторы выствленых ордеров, запускаем проверку')
            for key, values in ids.items():
                print(f'Актив {key}\n')
                base_coin = asset.strip_quote(key)
                asset.set_coin(base_coin)

                for value in values:
                    order = Order.ask_order(asset.get_coin(), value)

                    if order == None:
                        failed.append({value: None})
                        continue

                    if order['status'] == 'FILLED':
                        ready.append(order)
                    else:
                        opened.append(order['orderId'])
        else:
            print('Лог файл пустой')

        filter = Filter(asset.get_coin())

        if len(ready) > 0:
            # print(json.dumps(ready, indent=4))
            # NOTE: По всей видимости надо делать новый объект ордера на каждую попытку выставить новый ордер и при выключении программы загрузить ордеры из файла ID:шниками
            for item in ready:
                order = Order(asset.get_base())
                print(
                    f'Выполнен {item["side"]} для актива {item["symbol"]} по цене {item["price"]}')
                order_data = order.create_relative_order(
                    order=item, filters=filter)
                print(
                    f'Ордер {order_data[0]} для актива {key} по цене {order_data[1]}\n')

                # TODO: При заказе нового ордера надо удалить ID старого и
                # записать в массив новый ID. После чего объединить открытые и
                # новые ордера
                if order_data:
                    opened.append(order_data['orderId'])

        return {asset.get_coin(): opened}


# def show_summary(coin: Coin, buy_price: float, amount: float) -> str:
#     print(f'\nДля работы скрипта получены следуюшие данные:\n')
#     print(f'Название торговой пары: {coin.get_coin(): >26}')
#     print(f'Количество для покупки {coin.get_base()}: {amount: >21}')
#     print(f'Стоимость актива для покупки: {buy_price: >20}')
#     print(
#         f'Обшие затраты на базовую закупку {config.TRADE_PAIR}: {amount * buy_price: >11}\n')

#     print(Trade_Log.get_balance_string(coin.get_base()))

# def loop_orders(ids: dict) -> None:
#     if len(ids) < 1:
#         print('Нет ордеров для отслеживания')
#         sys.exit()

#     log_ids = Trade_Log()
#     log_ids.write_ids(ids)
#     while True:
#         try:
#             for key, values in ids.items:
#                 print(f'Актив {key} {values}')
#                 # for value in values:
#                 #     print(f'Проверка ордера {value}')
#                 time.sleep(5)
#         except KeyboardInterrupt:
#             print('Прерываем работу скрипта ...')
#             break
#         except Exception as e:
#             print('Возникла ошибка отслеживания')
#             print(e)
#             sys.exit()
##########################################################
# Тестовая функция


def read_json_log(file):
    with open(file) as json_file:
        data = json.load(json_file)

    return data

    # def parse_order(order):
    #     symbol = order['symbol']
    #     id = order['orderId']
    #     status = order['status']
    #     type = order['type']
    #     side = order['side']
    #     price = order['price']
    #     origQty = order['origQty']
    #     execQty = order['executedQty']
    #     cumulativeQQ = order['cummulativeQuoteQty']

    #     if status == 'FILLED':
    #         status_str = 'выполнен'

    #     if status == 'NEW':
    #         status_str = 'выставлен'

    #     if side == 'BUY':
    #         side_str = 'покупка'
    #     else:
    #         side_str = 'продажа'

    #     output = f'{type} ордер {id}/{side_str} актива {symbol} был {status_str} со следующими данными:\n'\
    #         f'- выставленная стоимость {price}\n'\
    #         f'- запрашиваемое количество {origQty}\n'\
    #         f'- полученое количество {execQty}\n'\
    #         f'- получено квотированного актива {cumulativeQQ}\n'

    #     return output
    ##########################################################
    # ===============================================================

    if check.log_file:
        ids = check.read_log_file()
        ready = []
        found_asset = None

        if ids:
            print('Найдены идентификаторы выствленых ордеров, запускаем проверку')
            for key, values in ids.items():
                print(f'Актив {key}\n')
                base_coin = asset.strip_quote(key)
                asset.set_coin(base_coin)

                for value in values:
                    # print(parse_order(Order.ask_order(key, value)))
                    order = Order.ask_order(asset.get_coin(), value)

                    if order['status'] == 'FILLED':
                        ready.append(order)
        else:
            print('Лог файл пустой')

        filter = Filter(asset.get_coin())

        if len(ready) > 0:
            # print(json.dumps(ready, indent=4))
            # TODO: По всей видимости надо делать новый объект ордера на каждую попытку выставить новый ордер и при выключении программы загрузить ордеры из файла ID:шниками
            for item in ready:
                order = Order(asset.get_base())
                print(
                    f'Выполнен {item["side"]} для актива {item["symbol"]} по цене {item["price"]}')
                order_data = order.create_relative_order(
                    order=item, filters=filter)
                print(
                    f'Ордер {order_data[0]} для актива {key} по цене {order_data[1]}\n')

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
            buy_price = Coin.get_current_price(asset.get_coin())
            filter.check_price(buy_price)
            if not filter.check_notional(amount * buy_price):
                raise Exception(
                    f'Запрашиваемая стоимость {buy_price} для покупки не удовлетворяет фильтру NOTIONAL')

            sells = mesh.create_sell_rows(buy_price)
            buys = mesh.create_buy_rows(buy_price)

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
    ids = {f'{asset.get_base()}': []}

    if order.create_test_market_buy_order(quantity=amount):
        try:
            # print('Тест базовой зкупки прошёл успешно')
            receipt = order.create_market_buy_order(quantity=amount)
        except Exception as e:
            print(e)
        else:
            base_price = float(order.get_base_price(receipt))

            base_log = Trade_Log(receipt)
            base_log.write_market_order('base_order.json')

            sells = mesh.create_sell_rows(base_price)
            buys = mesh.create_buy_rows(base_price)

        print(f'\nСоздаём сетку продажи актива {asset.get_base()}\n')
        for item in sells:
            if order.create_test_limit_sell_order(
                    amount=item['amount'], price=item['price']):
                try:
                    # print('Проверен уровень сетки на продажу')
                    receipt = order.create_limit_sell_order(
                        amount=item['amount'], price=item['price'])
                except Exception as e:
                    print('Возникла ошибка при выставлении ордена на продажу')
                    print(e)
                else:
                    # ids[asset.get_coin()].append = receipt['orderId']
                    ids[asset.get_coin()].append(receipt['orderId'])

        for item in buys:
            if order.create_test_limit_buy_order(
                    amount=item['amount'], price=item['price']):
                try:
                    receipt = order.create_limit_buy_order(
                        amount=item['amount'], price=item['price'])
                    # print('Проверен уровень сетки на покупку')
                except Exception as e:
                    print('Возникла ошибка при выставлении ордера на покупку')
                    print(e)
                else:
                    # ids[asset.get_coin()].append = receipt['orderId']
                    ids[asset.get_coin()].append(receipt['orderId'])

    # TODO: Создать какое то отображение выставленых заказов
    if len(ids) < 1:
        print('Нет ордеров для отслеживания')
        sys.exit()

    log_ids = Trade_Log()
    log_ids.write_ids(ids)
    while True:
        try:
            for key, values in ids.items:
                print(f'Актив {key} {values}')
                # for value in values:
                #     print(f'Проверка ордера {value}')
                time.sleep(5)
        except KeyboardInterrupt:
            print('Прерываем работу скрипта ...')
            break
        except Exception as e:
            print('Возникла ошибка отслеживания')
            print(e)
            sys.exit()
