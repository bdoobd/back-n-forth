from src.coin import Coin
import sys
from pprint import pprint

asset_found = False


def run():
    pass


if __name__ == '__main__':
    asset = Coin()

    while not asset_found:
        try:
            coin = input('Укажи название актива для работы: ')

            if asset.check_asset_exist(coin):
                asset.set_coin(coin)
                asset_found = True
            else:
                print('Выбран не существующий актив, попробуй ещё раз')
        except KeyboardInterrupt:
            print('\n\nTerminating script ...')
            sys.exit()
    print('Продолжаем выполение скрипта')
    pprint(asset.get_coin_info(coin))
    # TODO: Из данных о активе вытащить значения фильтров
    # TODO: Запросить количество покупаемых активов
    # TODO: Проверить удовлетворяют ли указанное количество фильтрам актива
    # TODO: Расчитать стоимость запрашиваемого количесва
    # TODO: Проверить есть ли на балансе достаточная сумма

    run()
