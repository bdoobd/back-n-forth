from src.coin import Coin
from src.filter import Filter
from src.wallet import Wallet
from src.mesh import Mesh
from src.order import Order
from src.trade import Trade
from src.trade_log import Trade_Log
from src.history import History
from src.check_order import Check_Order

import sys
import time

if __name__ == '__main__':
    check = Check_Order('ids.json')
    history = History()
    asset = Coin()
    log_ids = Trade_Log()

    if check.no_open_orders():
        asset.ask_coin()
        asset.check_coin_level()
        history.write_history_header()

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

        order = Order(asset.get_base(), history=history)

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

        log_ids.write_ids(ids)
    else:
        ids = check.read_log_file()

    # ==============================================================
    # Обработка массива ID ордеров
    # ==============================================================
    while True:
        try:
            working_asset, working_orders = check.loop_orders(ids=ids)
        except ValueError as e:
            print(e)
            sys.exit()

        asset.set_coin(working_asset)
        filter = Filter(coin=asset.get_coin())
        order = Order(asset.get_base(), history=history)
        trade = Trade(coin=asset, filter=filter)
        tmp_ids = {f'{asset.get_base()}': []}

        print(trade.show_working_asset())

        try:
            check.number_of_orders(asset.get_coin())
        except ValueError as e:
            print(e)
            sys.exit()

        for working_order in working_orders:
            try:
                working_data = Order.ask_order(
                    symbol=asset.get_coin(), id=working_order)
            except Exception as e:
                print(e)
            else:
                print(working_data)
            if check.check_order_filled(working_data):
                history.write_limit_order(order=working_data)

                print(
                    f'Ордер {working_data["side"]} {working_data["orderId"]} для актива {working_asset} выполнен для {working_data["executedQty"]} шт стоимостью {working_data["price"]}')
                print(
                    f'Текущая стоимость актива {Coin.get_current_price(asset.get_coin())}')
                try:
                    reorder = order.create_relative_order(
                        order=working_data, filters=filter)

                except Exception as e:
                    print('Не удалось выставить заказ взамен выполненного')
                    print(e)
                else:
                    tmp_ids[asset.get_base()].append(reorder['orderId'])

            else:
                print(
                    f'Ордер {working_data["side"]} {working_data["orderId"]} для актива {working_asset} находится в ожидании для {working_data["origQty"]} шт стоимостью {working_data["price"]}')
                tmp_ids[asset.get_base()].append(working_order)

        log_ids.write_ids(tmp_ids)
        ids = tmp_ids

        time.sleep(20)
