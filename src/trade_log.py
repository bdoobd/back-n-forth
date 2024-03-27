from pathlib import Path
from datetime import datetime
from src.wallet import Wallet
import config.config as config

import json


class Trade_Log:
    def __init__(self, order) -> None:
        self.log_dir = self.check_log_dir(Path('logs'))
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

    # FIXME: Эта сторка уже встречается в потоке главного модуля, надо использовать её

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
