from src.coin import Coin
import config.config as config
import pandas as pd


class Mesh():

    def __init__(self, base_volume: float, filters: filter) -> None:
        self.volume = base_volume
        self.percent_threshold = config.MESH_THRESHOLD / 100
        self.filters = filters
        self.buys = None
        self.sells = None
        self.part_volume = None

    # def get_part_amount(self) -> float:
    #     part = round((self.amount/config.ORDERS_AMOUNT),
    #                  self.get_precision(self.filters.lot_size()['stepSize']))
    #     if self.check_amount(part):
    #         return part
    #     else:
    #         raise ValueError('Вышли за рамки LOT_SIZE фильтра')

    def set_part_volume(self, part_volume: float) -> float:
        self.part_volume = part_volume

    def create_sell_rows(self, current_price: float) -> list:
        rows = []
        multiplier = self.percent_threshold
        line_price = float(current_price)

        for item in range(1, config.ORDERS_AMOUNT + 1):
            price = line_price * (1 + multiplier)
            price = round(price, self.get_precision(
                self.filters.price_filter()['tickSize']))

            self.check_notional_filter(value=price)
            rows.append(
                {'amount': self.part_volume, 'price': price})

            line_price = price

        self.sells = rows

    def create_buy_rows(self, current_price: float) -> list:
        rows = []
        multiplier = self.percent_threshold
        line_price = float(current_price)

        for item in range(1, config.ORDERS_AMOUNT + 1):
            price = line_price * (1 - multiplier)
            price = round(price, self.get_precision(
                self.filters.price_filter()['tickSize']))

            self.check_notional_filter(value=price)
            rows.append({'amount': self.part_volume, 'price': price})

            # multiplier += self.percent_threshold
            line_price = price

        self.buys = rows

    def check_notional_filter(self, value: float) -> float | None:
        line_value = self.part_volume * value
        if not self.filters.check_notional(price=line_value):
            raise ValueError(
                f'Сумма {line_value} на линию сетки на соответствует фильтру NOTIONAL')

    def calculate_buy_mesh_amount(self) -> float:
        total = 0
        for line in self.buys:
            total += (line['amount'] * line['price'])

        return total

    def get_precision(self, number: float):
        number = str(number).rstrip('0')
        index = str(number)[::-1].find('.')

        if index == 1 and str(number)[-1] == '0':
            return 0

        return index
    #########################################################################
    # DISPLAY INFO
    #########################################################################

    def display_mesh(self, base_price: float):
        sells = self.create_sells_df()
        buys = self.create_buys_df()
        base = self.create_base_df(base_price=base_price)

        # buys = pd.DataFrame(self.buys)
        print(pd.concat([sells, base, buys]).to_string(index=False))

    def create_sells_df(self) -> pd.DataFrame:
        sells = pd.DataFrame(self.sells)
        sells = sells.sort_values(by=['price'], ascending=False)
        sells.insert(0, 'action', ['Продажа'] * len(sells))

        return sells

    def create_buys_df(self) -> pd.DataFrame:
        buys = pd.DataFrame(self.buys)
        buys.insert(0, 'action', ['Покупка'] * len(buys))

        return buys

    def create_base_df(self, base_price: float) -> pd.DataFrame:
        row = {'action': 'Базовая покупка',
               'amount': self.volume, 'price': base_price}

        return pd.DataFrame([row])
