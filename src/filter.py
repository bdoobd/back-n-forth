from src.access import Access
from src.coin import Coin


class Filter:

    def __init__(self, coin: str) -> None:
        self._client = Access.client()
        self._coin = coin.upper()
        self.coin_info = self._client.get_symbol_info(self._coin)
        self._filters = self._filters()

    def _filters(self) -> list:
        return self.coin_info['filters']

    # # FIXME: После вытаскивания всех фильтров удалить этот метод
    # def get_filters(self) -> list:
    #     return self._filters

    def price_filter(self):
        for filter in self._filters:
            if filter['filterType'] == 'PRICE_FILTER':
                return filter

    def lot_size(self):
        for filter in self._filters:
            if filter['filterType'] == 'LOT_SIZE':
                return filter

    def notional(self):
        for filter in self._filters:
            if filter['filterType'] == 'NOTIONAL':
                return filter

    # def dict_string_to_float(self, dict: dict, filter_items: list) -> dict:
    #     return {key: float(value) for (key, value) in dict.items() if key in filter_items}

    def displayFilters(self):
        return f'\nТекущая стоимость {self._coin} {Coin.get_current_price(self._coin): >23}\n'\
            f'\nФильтры для {self._coin: >10}\n'\
            f'PRICE FILTER:\n'\
            f'{"":>5}минимальное вложение {self.price_filter()["minPrice"]: >24}\n'\
            f'{"":>5}максимальное вложение {self.price_filter()["maxPrice"]: >23}\n'\
            f'{"":>5}шаг вложения {self.price_filter()["tickSize"]: >32}\n'\
            f'LOT SIZE:\n'\
            f'{"":>5}минимальное количество {self.lot_size()["minQty"]: >22}\n'\
            f'{"":>5}максимальное количество {self.lot_size()["maxQty"]:>21}\n'\
            f'{"":>5}шаг добавления {self.lot_size()["stepSize"]:>30}\n'\
            f'NOTIONAL: (price * quantity)\n'\
            f'{"":>5}минимальное значение {self.notional()["minNotional"]: >24}\n'\
            f'{"":>5}максимальное значение {self.notional()["maxNotional"]:>23}\n'\
            f'{"":>5}стоимость по умолчанию {self.notional()["avgPriceMins"]:>22}\n'

    def check_lot_size(self, volume: float) -> bool:
        if (volume > float(self.lot_size()['maxQty']) or volume < float(self.lot_size()['minQty'])):
            raise Exception(
                'Количество не попадает под политику фильтра LOT SIZE')

        step_size = float(self.number_of_decimals(self.lot_size()['stepSize']))
        amount_precision = float(self.number_of_decimals(volume))

        if amount_precision > step_size:
            raise Exception(
                f'Разрядность количества не попадает под фильтр LOT_SIZE, количество десятичных знаков не более {step_size} шт\n')

        return True

    def check_notional(self, price: float) -> bool:
        if price < float(self.notional()['minNotional']):
            return False

        return True

    def check_price(self, price: float) -> bool:
        if price < float(self.price_filter()['minPrice']) or price > float(self.price_filter()['maxPrice']):
            raise Exception('Стоимость не соответствует фильтру PRICE_FILTER')

        tick_size = float(self.number_of_decimals(
            self.price_filter()['tickSize']))
        price_precision = float(self.number_of_decimals(price))

        if price_precision > tick_size:
            raise Exception(
                f'Разрядность стоимости не соответствует фильтру PRICE_FILTER, максимальное количество занков после запятой {tick_size}\n')

        return True

    def number_of_decimals(self, number) -> int:
        num_str = str(number)
        num_str = num_str.rstrip('0')
        dot = num_str.find('.')

        return len(num_str[dot + 1:])
