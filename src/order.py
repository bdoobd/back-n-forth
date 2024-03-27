from src.access import Access
from src.trade_log import Trade_Log
import config.config as config


class Order:

    def __init__(self, base: str) -> None:
        self._client = Access.client()
        self._base = base
        self.symbol = base + config.TRADE_PAIR

    def create_market_order(self, quantity: float) -> None:
        try:
            order = self._client.create_order(
                symbol=self.symbol,
                side=self._client.SIDE_BUY,
                type=self._client.ORDER_TYPE_MARKET,
                quantity=quantity
            )
        except Exception as e:
            print(e)
        else:
            print('Базовая покупка прошла успешно')
            log = Trade_Log(order)
            log.create_logfile_buy(self._base)
            return order

    def create_test_market_order(self, quantity: float) -> bool:
        try:
            test_order = self._client.create_test_order(
                symbol=self.symbol,
                side=self._client.SIDE_BUY,
                type=self._client.ORDER_TYPE_MARKET,
                quantity=quantity)
        except Exception as e:
            print(e)
            return False
        else:
            print('Тестовая заявка прошла успешно.')
            return True

    def create_limit_order(self, amount: float, price: float):
        try:
            self._client.create_test_order(
                symbol=self.symbol,
                side=self._client.SIDE_SELL,
                type=self._client.ORDER_TYPE_LIMIT,
                timeInForce=self._client.TIME_IN_FORCE_GTC,
                quantity=amount,
                price=price
            )
        except Exception as e:
            print(e)
        else:
            print(
                f'Выставлен ордер на продажу {amount} {self._base} по цене {price} ')

    def create_limit_sell_order(self, amount: float, price: float):
        try:
            self._client.create_test_order(
                symbol=self.symbol,
                side=self._client.SIDE_SELL,
                type=self._client.ORDER_TYPE_LIMIT,
                timeInForce=self._client.TIME_IN_FORCE_GTC,
                quantity=amount,
                price=price
            )
        except Exception as e:
            print(e)
        else:
            print(
                f'Выставлен ордер на продажу {amount} {self._base} по цене {price}')
            return True

    def create_limit_buy_order(self, amount: float, price: float) -> None | bool:
        try:
            self._client.create_test_order(
                symbol=self.symbol,
                side=self._client.SIDE_BUY,
                type=self._client.ORDER_TYPE_LIMIT,
                timeInForce=self._client.TIME_IN_FORCE_GTC,
                quantity=amount,
                price=price
            )
        except Exception as e:
            print(e)
        else:
            print(
                f'Выставлен ордер на покупку {amount} {self._base} по цене {price} ')
            return True
