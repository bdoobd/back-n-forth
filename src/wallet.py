from src.access import Access
import config.config as config


class Wallet:

    def __init__(self) -> None:
        self._client = Access.client()
        # FIXME: Эта информация достаточно динамична, нет смысла получать её при создании класса. Суммы в кошельке меняются при каждой покупке/продаже.
        # Вывести в отдельный метод, может даже статический
        # self._account_info = self._account_information()

    # def _account_information(self) -> dict:
    #     return self._client.get_account()

    # def get_all_balances(self) -> list:
    #     return self._account_info['balances']

    def get_balance(self, coin: str):
        all_balances = self._client.get_account()['balances']

        for asset in all_balances:
            if asset['asset'] == coin:
                return asset

    def check_balance(self, asset: str, order_price: float) -> bool:
        if float(self.get_balance(asset)['free']) < order_price:
            return False

        return True

    # def quote_balance_info(self):
    #     balance = self.get_balance(config.TRADE_PAIR)

    #     asset_balance_free = float(balance['free'])
    #     asset_balance_locked = float(balance['locked'])

    #     return f'\nБаланс актива {config.TRADE_PAIR} в кошельке:\n'\
    #         f'{"": >10}Свободно: {asset_balance_free: >17}\n'\
    #         f'{"": >10}Зарезервировано: {asset_balance_locked: >10}\n'

    # NOTE: Тестовый метод
    @staticmethod
    def get_asset_balance(coin: str) -> float | bool:
        data = Access.client().get_account()['balances']
        for item in data:
            if item['asset'] == coin:
                return float(item['free'])

        return False
