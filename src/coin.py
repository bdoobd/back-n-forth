from src.access import Access
import config.config as config
import requests


class Coin:
    def __init__(self) -> None:
        self._client = Access.client()
        self._coin_list = self._create_coins_list()
        self._coin = None

    def _create_coins_list(self) -> list:
        coins = self._client.get_all_tickers()
        filtered = [coin['symbol']
                    for coin in coins if config.TRADE_PAIR == coin['symbol'][-4:]]
        cleaned = [coin for coin in filtered if coin not in config.UNWANTED]
        return cleaned

    @property
    def coin_list(self) -> list:
        return self._coin_list

    def set_coin(self, coin: str) -> None:
        self._base = coin.upper()
        self._coin = self._base + config.TRADE_PAIR

    def get_coin(self) -> str:
        return self._coin

    def get_base(self) -> str:
        return self._base

    def check_asset_exist(self, name: str) -> bool:
        asset = name.upper() + config.TRADE_PAIR
        if asset in self.coin_list:
            return True

        return False

    def get_coin_info(self, coin: str) -> dict:
        return self._client.get_symbol_info(coin)

    @staticmethod
    def get_current_price(coin: str) -> float:
        url = config.BASE_URL + '/api/v3/ticker/price'

        headers = {
            'X-MBX-APIKEY': Access.get_api_key()
        }

        params = {
            'symbol': coin
        }

        response = requests.get(url, params=params, headers=headers)
        data = response.json()

        return float(data['price'])
