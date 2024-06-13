from pathlib import Path
from datetime import datetime
from src.wallet import Wallet
import config.config as config

import json


class Trade_Log:
    def __init__(self, order={}) -> None:
        self.log_dir = self.check_log_dir(Path('./logs'))
        self.receipt = order
        self.symbol = self.set_symbol()
        try:
            self.log_file = self.log_dir / self.create_file_name(self.symbol)
        except NameError as e:
            print(e)

    def check_log_dir(self, path: str) -> None:
        if not path.exists():
            try:
                path.mkdir()
            except Exception as e:
                print('Не могу создать папку для логов\n')
                print(e)

        return path

    def set_symbol(self) -> None:
        if len(self.receipt) == 0:
            return 'NoAsset'

        return self.receipt['symbol']

    def create_file_name(self, symbol: str) -> None:
        if self.receipt == None:
            raise NameError('Нет данных квитка заказа')

        datetime_str = datetime.now().strftime('%Y-%m-%d**%H_%M_%S')

        return f'{symbol}_{datetime_str}.log'

    def create_header(self) -> str:
        return f'Дата файла: {datetime.now().strftime("%d.%m.%Y")}\n'\
            f'Название актива: {self.symbol}\n'\


    @staticmethod
    def get_balance_string(coin: str) -> str:
        return f'\nБаланс базового актива {coin}: {Wallet.get_asset_balance(coin):>19}\n'\
            f'Баланс котируемого актива {config.TRADE_PAIR}: {Wallet.get_asset_balance(config.TRADE_PAIR):>15}\n'

    def create_logfile_buy(self, base_asset: str) -> None:
        with open(self.log_file, 'w', encoding='UTF-8') as file:
            file.write(self.create_header())
            # TODO: Надо ли снять баланс в кошельке до и после продажи/покупки
            file.write(json.dumps(self.receipt, indent=4))
            file.write(self.get_balance_string(base_asset))

    def create_logfile_sell(self, base_asset: str) -> None:
        with open(self.log_file, 'w', encoding='UTF-8') as file:
            file.write(self.create_header())
            # TODO: Надо ли снять баланс в кошельке до и после продажи/покупки
            file.write(json.dumps(self.receipt, indent=4))
            file.write(self.get_balance_string(base_asset))

    def write_market_order(self, name: str) -> None:
        log_file = self.log_dir / name
        data = {}

        data['symbol'] = self.receipt['symbol']
        data['id'] = self.receipt['orderId']

        fills = self.receipt['fills']
        data['price'] = []
        data['quantity'] = []

        if len(fills) > 1:
            for item in fills:
                data['price'].append(item['price'])
                data['quantity'].append(item['qty'])
        else:
            data['price'].append(fills[0]['price'])
            data['quantity'].append(fills[0]['qty'])

        try:
            with open(log_file, 'w') as file:
                file.write(json.dumps(data, indent=4))
        except Exception as e:
            print('Ошибка записи лог файла')
            print(e)
        # else:
        #     return data

    def write_limit_order(self, name: str) -> None:
        log_file = self.log_dir / name
        data = {}

        data['symbol'] = self.receipt['symbol']
        data['id'] = self.receipt['orderId']
        data['price'] = self.receipt['price']
        data['quantity'] = self.receipt['origQty']

        try:
            with open(log_file, 'w') as file:
                file.write(json.dumps(data, indent=4))
        except Exception as e:
            print('Ошибка записи лог файла')
            print(e)

    def write_ids(self, ids: dict) -> None:
        log_file = self.log_dir / 'ids.json'
        try:
            with open(log_file, 'w') as file:
                json.dump(ids, file)
        except Exception as e:
            print('Не удалось записать идентификаторы в файл')
            print(e)
