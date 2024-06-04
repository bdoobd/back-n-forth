from src.access import Access
import config.config as config
import pandas as pd
import requests
import sys


class Coin:

    def __init__(self) -> None:
        self._client = Access.client()
        self._coin_list = self._create_coins_list()
        self._coin = None
        self._klines = None
        self._min = None
        self._max = None

    def _create_coins_list(self) -> list:
        """Создаёт список активов фильтрованый согласно значению из конфига TRADE_PAIR

        Returns:
            list: Список активов
        """
        coins = self._client.get_all_tickers()
        filtered = [coin['symbol']
                    for coin in coins if config.TRADE_PAIR == coin['symbol'][-4:]]
        cleaned = [coin for coin in filtered if coin not in config.UNWANTED]
        return cleaned

    @property
    def coin_list(self) -> list:
        return self._coin_list

    def set_coin(self, coin: str) -> None:
        """Устанавливает название базового актива и торговой пары

        Args:
            coin (str): Название базового актива
        """
        self._base = coin.upper()
        self._coin = self._base + config.TRADE_PAIR

    def get_coin(self) -> str:
        """Возвращает название торговой пары

        Returns:
            str: Название торговой пары
        """
        return self._coin

    def get_base(self) -> str:
        """Возвращает название базового актива

        Returns:
            str: Базовый актив
        """
        return self._base

    def register_coin(self, coin: str) -> None:
        """Регестрирует в объекте свойства связанные с активом

        Args:
            coin (str): Название базового актива
        """
        self.set_coin(coin)
        self._klines = self.klines_to_df()
        self.kline_min_max()

    def check_asset_exist(self, name: str) -> bool:
        asset = name.upper() + config.TRADE_PAIR
        if asset in self.coin_list:
            return True

        return False

    def get_coin_info(self, coin: str) -> dict:
        return self._client.get_symbol_info(coin)

    def get_klines(self) -> list:
        data = self._client.get_historical_klines(
            symbol=self._coin, interval=self._client.KLINE_INTERVAL_1HOUR, start_str=config.KLINE_DAYS)

        return data

    def klines_to_df(self) -> pd.DataFrame:
        data = pd.DataFrame(self.get_klines())
        data = data.iloc[:, :5]
        columns = ['OpenTime', 'Open', 'High', 'Low', 'Close']
        data.columns = columns
        data.set_index('OpenTime', inplace=True)
        data.index = pd.to_datetime(data.index, unit='ms')
        return data

    def get_closes(self) -> pd.Series:
        return self.klines_to_df()['Close'].astype(float)

    def kline_min_max(self) -> None:
        close = self.get_closes()
        self._min = float(close.min())
        self._max = float(close.max())

    def check_price_level(self) -> bool:
        min_level = self.get_closes().quantile(.25)
        max_level = self.get_closes().quantile(.75)

        if self.get_current_price(self._coin) < min_level:
            raise ValueError(
                f'\nТекущая стоимость акитва менее 25% {config.KLINE_DAYS} дневного периода')

        if self.get_current_price(self._coin) > max_level:
            raise ValueError(
                f'\nТекущая стоимость актива выше 25% {config.KLINE_DAYS} дневного периода')

        return True

    def get_average_price(self):
        return self._client.get_avg_price(symbol=self._coin)['price']

    def strip_quote(self, coin: str) -> str:
        return coin.replace(config.TRADE_PAIR, '')

    @staticmethod
    def get_current_price(coin: str) -> float:
        """ Получает текущую стоимость активая по его названию

        Args:
            coin (str): Название актива

        Returns:
            float: Стоимость актива
        """
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

    def ask_coin(self) -> str:
        """Запрашивает у пользователя название базового актива.
        Устанавливает свойство актива согласно выбраному пользователем.
        При указании не существующего актива повторяет запрос.
        Прерывает выполнение метода по Ctrl + C

        Returns:
            str: Название базового актива
        """
        while True:
            try:
                asset_base = input('Укажи базовый актив для работы: ')
                if self.check_asset_exist(asset_base):
                    self.register_coin(asset_base)
                    break
                else:
                    print('Выбран не существующий актив, попробуй ещё раз')
            except KeyboardInterrupt:
                print('\n\nСкрипт закончил работу ...')
                sys.exit()
        print(
            f'Продолжаем выполнение скрипта с парой {self.get_coin(): >20}\n')

        return self.get_base()

    def check_coin_level(self) -> bool:
        try:
            self.check_price_level()
        except ValueError as e:
            print(e)
            confirm_level = input('Хочешь продолжить? Y/N: ')
            if not confirm_level.upper() == 'Y':
                print(
                    f'Актив {self.get_base()} не подошёл для работы, завершаем работу скрипта ...\n')
                sys.exit()

        return True
