from src.coin import Coin
from src.filter import Filter
import config.config as config
import sys


class Trade:

    def __init__(self, coin: Coin,  filter: Filter) -> None:
        self.base_asset = coin.get_base()
        self.asset = coin.get_coin()
        self.coin = coin
        self.filter = filter
        self.base_volume = None
        self.part_volume = None

    ##############################################################
    # Getters
    def get_base_volume(self) -> float:
        return self.base_volume

    ##############################################################
    # Setters
    def set_base_volume(self, volume: float) -> float:
        self.base_volume = volume
    ##############################################################

    def get_volume(self) -> float | None:
        try:
            self.base_volume = float(input('Укажи дробное число: '))
        except ValueError:
            raise ValueError(
                'Количество должно быть вещественным числом, дробный раздетитель - точка')

        if not self.check_lot_amount(amount=self.base_volume):
            raise ValueError(
                f'Заданное количество {self.base_volume} не соответствует минимальному или максимальному ограничению фильтра LOT_SIZE')

        if not self.check_lot_precision(amount=self.base_volume):
            raise ValueError(
                f'Дробная часть базового объёма {self.base_volume} превышает значение фильтра LOT_SIZE, максимальное количестово знаков после запятой {self.filter.number_of_decimals(self.filter.lot_size()["stepSize"])}')

        current_price = Coin.get_current_price(self.asset)
        trade_price = self.base_volume * current_price

        if not self.check_notional(notional_price=trade_price):
            raise ValueError(
                f'Общая стоимость закупки {trade_price} не соответствует фильтру min NOTIONAL {self.filter.notional()["minNotional"]}')

        return self.base_volume

    def calculate_part_amount(self) -> float:
        return float(self.base_volume / config.ORDERS_AMOUNT)

    def get_volume_part(self) -> float | None:
        self.part_volume = self.calculate_part_amount()

        if not self.check_lot_precision(amount=self.part_volume):
            raise ValueError(
                f'Количество {self.part_volume} на линию не соответствует значению фильтра LOT_SIZE, максимальное количестово знаков после запятой {self.filter.number_of_decimals(self.filter.lot_size()["stepSize"])}')

        if not self.check_lot_amount(amount=self.part_volume):
            raise ValueError(
                f'Количество актива {self.part_volume} на линию сетки не соответствует минимальному или максимальному ограничению фильтра LOT_SIZE')

        return self.part_volume
    #########################################################################
    # FILTERS
    #########################################################################

    def check_lot_amount(self, amount: float) -> bool:
        min_lot_size = float(self.filter.lot_size()['minQty'])
        max_lot_size = float(self.filter.lot_size()['maxQty'])
        if amount < min_lot_size or amount > max_lot_size:
            return False

        return True

    def check_lot_precision(self, amount: float) -> bool:
        step_size_precision = int(
            self.filter.number_of_decimals(self.filter.lot_size()['stepSize']))
        part_amount_precision = int(self.filter.number_of_decimals(amount))
        if part_amount_precision > step_size_precision:
            return False

        return True

    def check_notional(self, notional_price: float) -> bool:
        if self.filter.notional()['applyMinToMarket']:
            if notional_price < float(self.filter.notional()['minNotional']):
                return False

        return True

    def check_price_filter(symbol: str) -> bool:
        pass

    #########################################################################
    # DISPLAY INFO
    #########################################################################
    def show_summary(self, base_price: float) -> str:
        return f'\nДля работы скрипта получены следуюшие данные:\n'\
            f'Название торговой пары: {self.asset: >26}\n'\
            f'Количество для покупки {self.base_asset}: {self.base_volume: >22}\n'\
            f'Стоимость актива для покупки: {base_price: >20}\n'\
            f'Обшие затраты на базовую закупку {config.TRADE_PAIR}: {self.base_volume * base_price: >11}\n'

    def show_working_asset(self) -> str:
        return f'\n================================================\n'\
            f'Работаем с массивом ордеров для актива {self.asset}\n'\
            f'================================================\n'
