from src.access import Access


class Filter:

    def __init__(self, coin: str) -> None:
        self._client = Access.client()
        self._coin = coin.upper()
        self.coin_info = self._client.get_symbol_info(self._coin)
        self._filters = self._filters()

    def _filters(self) -> list:
        return self.coin_info['filters']

    # FIXME: После вытаскивания всех фильтров удалить этот метод
    def get_filters(self) -> list:
        return self._filters

    def price_filter(self):
        for filter in self._filters:
            if filter['filterType'] == 'PRICE_FILTER':
                return self.dict_string_to_float(filter, ['minPrice', 'maxPrice', 'tickSize'])

    def lot_size(self):
        for filter in self._filters:
            if filter['filterType'] == 'LOT_SIZE':
                return self.dict_string_to_float(filter, ['minQty', 'maxQty', 'stepSize'])

    def notional(self):
        for filter in self._filters:
            if filter['filterType'] == 'NOTIONAL':
                return self.dict_string_to_float(filter, ['minNotional', 'maxNotional', 'avgPriceMins'])

    def dict_string_to_float(self, dict: dict, filter_items: list) -> dict:
        return {key: float(value) for (key, value) in dict.items() if key in filter_items}

    def displayFilters(self):
        return f'\nФильтры для {self._coin: >10}\n'\
            f'PRICE FILTER:\n'\
            f'{"":>5}минимальное вложение {self.price_filter()["minPrice"]: >14f}\n'\
            f'{"":>5}максимальное вложение {self.price_filter()["maxPrice"]: >13f}\n'\
            f'{"":>5}шаг вложения {self.price_filter()["tickSize"]: >22f}\n'\
            f'LOT SIZE:\n'\
            f'{"":>5}минимальное количество {self.lot_size()["minQty"]: >12f}\n'\
            f'{"":>5}максимальное количество {self.lot_size()["maxQty"]:>11f}\n'\
            f'{"":>5}шаг добавления {self.lot_size()["stepSize"]:>20f}\n'\
            f'NOTIONAL: (price * quantity)\n'\
            f'{"":>5}минимальное значение {self.notional()["minNotional"]: >14f}\n'\
            f'{"":>5}максимальное значение {self.notional()["maxNotional"]:>13f}\n'\
            f'{"":>5}стоимость по умолчанию {self.notional()["avgPriceMins"]:>12f}\n'

    def check_amount(self, amount: float) -> bool:
        # FIXME: Поправить вывод из метода lot_size, нужен float для посчётов
        if (amount > self.lot_size()['maxQty'] or amount < self.lot_size()['minQty']):
            raise ValueError(
                'Количество не попадает под политику фильтра LOT SIZE')
        # FIXME: Расчитать сумму на основании количества
        # if (amount > self.price_filter()['maxQty'] or amount < self.price_filter()['minQty']):
        #     raise ValueError(
        #         'Количество не попадает под политику фильтра PRICE_FILTER')
        # FIXME: Расчитать значение для этого раздела
        # if (amount > self.notional()['maxNotional'] or amount < self.notional()['minNotional']):
        #     raise ValueError(
        #         'Количество не попадает под политику фильтра NOTIONAL')

        return True
