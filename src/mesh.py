from src.coin import Coin
import config.config as config
import pandas as pd


class Mesh():

    def __init__(self, base_amount: float, filters: filter) -> None:
        self.amount = base_amount
        self.percent_threshold = config.MESH_THRESHOLD / 100
        self.filters = filters

    def get_part_amount(self) -> float:
        part = round((self.amount/config.ORDERS_AMOUNT),
                     self.get_precision(self.filters.lot_size()['stepSize']))
        if self.check_amount(part):
            return part
        else:
            raise ValueError('Вышли за рамки LOT_SIZE фильтра')

    # TODO: Удалить этот метод после создания процесса сетки продажи
    # def create_sell_row(self, current_price: float) -> list:
    #     rows = []
    #     multiplier = self.percent_threshold

    #     for item in range(1, config.ORDERS_AMOUNT + 1):
    #         percent = self.percent_threshold * item
    #         price = current_price * (1 + multiplier)
    #         price = round(price, self.get_precision(
    #             self.filters.price_filter()['tickSize']))
    #         rows.append(
    #             {'процент': percent, 'количество': self.get_part_amount(), 'стоимость': price})
    #         multiplier += self.percent_threshold

    #     return rows

    def create_sell_rows(self, current_price: float) -> list:
        rows = []
        multiplier = self.percent_threshold

        for item in range(1, config.ORDERS_AMOUNT + 1):
            percent = self.percent_threshold * item
            # TODO: Добавить проверку фильтра PRICE_FILTER
            price = current_price * (1 + multiplier)
            price = round(price, self.get_precision(
                self.filters.price_filter()['tickSize']))
            rows.append(
                {'amount': self.get_part_amount(), 'price': price})
            multiplier += self.percent_threshold

        return rows

    def create_buy_rows(self, current_price: float) -> list:
        rows = []
        multiplier = self.percent_threshold

        for item in range(1, config.ORDERS_AMOUNT + 1):
            percent = self.percent_threshold * item
            price = current_price * (1 - multiplier)
            price = round(price, self.get_precision(
                self.filters.price_filter()['tickSize']))
            rows.append({'amount': self.get_part_amount(), 'price': price})

            multiplier += self.percent_threshold

        return rows

    # def create_buy_row(self, current_price: float) -> list:
    #     rows = []
    #     multiplier = self.percent_threshold

    #     for item in range(1, config.ORDERS_AMOUNT + 1):
    #         percent = self.percent_threshold * item
    #         price = current_price * (1 - multiplier)
    #         rows.append({'процент': f'-{percent}',
    #                     'количество': self.get_part_amount(), 'стоимость': price})

    #         multiplier += self.percent_threshold

    #     return rows

    # def create_mesh(self, current_price: float) -> list:
    #     data = self.create_sell_row(current_price=current_price)
    #     data = data + self.create_buy_row(current_price=current_price)

    #     return data

    # def create_mesh_df(self, data):
    #     return pd.DataFrame(data)

    def check_amount(self, amount) -> bool:
        min_lot_size = float(self.filters.lot_size()['minQty'])
        max_lot_size = float(self.filters.lot_size()['maxQty'])
        if amount > min_lot_size and amount < max_lot_size:
            return True

        return False

    def get_precision(self, number: float):
        number = str(number).rstrip('0')
        index = str(number)[::-1].find('.')

        if index == 1 and str(number)[-1] == '0':
            return 0

        return index
