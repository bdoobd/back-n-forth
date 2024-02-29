from src.access import Access


class Wallet:

    def __init__(self) -> None:
        self._client = Access.client()
        self._account_info = self._account_information()

    def _account_information(self) -> dict:
        return self._client.get_account()

    def get_all_balances(self) -> list:
        return self._account_info['balances']

    def get_balance(self, coin: str):
        for asset in self.get_all_balances():
            if asset['asset'] == coin:
                return asset
