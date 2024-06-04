from src.access import Access
from src.coin import Coin
import config.config as config


class Wallet:

    def __init__(self, coin: Coin) -> None:
        self._client = Access.client()
        self.coin = coin

    def get_balance(self):
        all_balances = self._client.get_account()['balances']

        for asset in all_balances:
            if asset['asset'] == self.coin.get_base():
                return asset

    def check_balance(self, asset: str, order_price: float) -> bool:
        if float(self.get_balance(asset)['free']) < order_price:
            return False

        return True

    def check_available_balance(self, total_price: float) -> bool | None:
        if total_price > self.get_asset_balance(config.TRADE_PAIR):
            raise ValueError(
                f'Требуемое для покупки{config.TRADE_PAIR} {total_price} количество актива больше имеющегося на балансе {self.get_asset_balance(config.TRADE_PAIR)}')

        return True

    # NOTE: Тестовый метод
    @staticmethod
    def get_asset_balance(coin: str) -> float | bool:
        data = Access.client().get_account()['balances']
        for item in data:
            if item['asset'] == coin:
                return float(item['free'])

        return False

    #########################################################################
    # DISPLAY INFO
    #########################################################################

    def display_trade_balances(self) -> str:
        return f'Баланс базового актива {self.coin.get_base()}: {Wallet.get_asset_balance(coin=self.coin.get_base()):>21}\n'\
            f'Баланс квотируемого актива {config.TRADE_PAIR}: {Wallet.get_asset_balance(coin=config.TRADE_PAIR):>16}\n'
