from src.access import Access
from src.trade_log import Trade_Log
from src.history import History
import config.config as config


class Order:

    def __init__(self, base: str, history: History) -> None:
        self._client = Access.client()
        self._base = base
        self.symbol = base + config.TRADE_PAIR
        self.history = history

    def create_market_buy_order(self, quantity: float) -> None:
        """ Создание MARKET ордера на покупку определённого объёма актива

        Args:
            quantity (float): Объём актива для покупки

        Returns:
            _type_: Квиток с данными выполенного ордера
        """
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

            self.history.write_base_order(order)

            return order

    def create_test_market_buy_order(self, quantity: float) -> bool:
        """ Тестовый ордер типа MARKET для проверки указываемых данных для реального ордера

        Args:
            quantity (float): Количество актива для ордера

        Returns:
            bool: True при успешном ордере в противном случае False
        """
        try:
            self._client.create_test_order(
                symbol=self.symbol,
                side=self._client.SIDE_BUY,
                type=self._client.ORDER_TYPE_MARKET,
                quantity=quantity)
        except Exception as e:
            print(
                f'Тестовый ордер для {quantity} {self.symbol} не удался.')
            print(e)
            return False
        else:
            print(
                f'Тестовый ордер для {quantity} {self.symbol} успешно выполнен.')
            return True

    def create_limit_buy_order(self, amount: float, price: float) -> dict | None:
        """ Создаёт лимитный ордер на покупку

        Args:
            amount (float): Количество актива для покупки
            price (float): Стоимость за штуку актива

        Returns:
            dict | None: Возвращает квиток созданного ордера или None в случае неудачи
        """
        try:
            order = self._client.create_order(
                symbol=self.symbol,
                side=self._client.SIDE_BUY,
                type=self._client.ORDER_TYPE_LIMIT,
                timeInForce=self._client.TIME_IN_FORCE_GTC,
                quantity=amount,
                price=price
            )
        except Exception as e:
            print(
                f'Не удалось создать ордер на покупку {amount} {self.symbol} по цене {price}')
            print(e)
        else:
            print(
                f'Выставлен ордер {order["orderId"]} на покупку {order["origQty"]} {self._base} по цене {order["price"]} ')
            log = Trade_Log(order)
            # print(order)
            log.create_logfile_buy(self._base)

            self.history.write_limit_order(order)

            return order

    def create_limit_sell_order(self, amount: float, price: float) -> dict | None:
        """ Создаёт лимитный ордер на продажу

        Args:
            amount (float): Количество актива для продажи
            price (float): Стоимость за штуку актива

        Returns:
            dict | None: Возвращает квиток созданного ордера или None в случае неудачи
        """
        try:
            order = self._client.create_order(
                symbol=self.symbol,
                side=self._client.SIDE_SELL,
                type=self._client.ORDER_TYPE_LIMIT,
                timeInForce=self._client.TIME_IN_FORCE_GTC,
                quantity=amount,
                price=price
            )
        except Exception as e:
            print(
                f'Не удалось создать ордер на продажу {amount} {self.symbol} по цене {price}')
            print(e)
        else:
            print(
                f'Выставлен ордер {order["orderId"]} на продажу {order["origQty"]} {self._base} по цене {order["price"]} ')
            log = Trade_Log(order)
            # print(order)
            log.create_logfile_sell(self._base)

            self.history.write_limit_order(order)

            return order

    def create_test_limit_sell_order(self, amount: float, price: float) -> bool:
        """ Создаёт тестовый ордер на продажу актива

        Args:
            amount (float): Количество активов на продажу
            price (float): Стоимость одного актива дла продажи

        Returns:
            bool: True при успешном ордере в противном случае False
        """
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
            print(
                f'Тестовый ордер на продажу {amount} {self._base} по цене {price} завершился неудачей')
            print(e)
            return False
        else:
            print(
                f'Тестовый ордер на продажу {amount} {self._base} по цене {price} в порядке')
            return True

    def create_test_limit_buy_order(self, amount: float, price: float) -> bool:
        """ Создаёт тестовый ордер на покупку актива

        Args:
            amount (float): Количество актива для покупки
            price (float): Стоимость за штуку актива

        Returns:
            bool: True если тест завершился удачно, в противном случае False
        """
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
            print(
                f'Тестовый ордер на покупку {amount} {self._base} по цене {price} завершился неудачей')
            print(e)
            return False
        else:
            print(
                f'Тестовый ордер на покупку {amount} {self._base} по цене {price} в порядке')
            return True

    def get_base_price(self, receipt: str) -> str:
        fills = receipt['fills']
        tmp = []
        if len(fills) > 1:
            for item in fills:
                tmp.append(item['price'])
                return tmp.max()

        return fills[0]['price']

    def create_relative_order(self, order: dict, filters: dict) -> dict:
        """ Выставляет ордер взамен выполненному, если выполнилась покупка
            будет выставлена продажа и наоборот

        Args:
            order (dict): Квиток заказа полученый от биржи
            filters (dict): Набор фильтров полученый через API биржи

        Returns:
            dict: Квиток о выставленном ордере.
        """
        # side = self._client.SIDE_BUY if order['side'] == 'SELL' else self._client.SIDE_SELL

        qty = float(order['executedQty'])
        price = float(order['price'])

        if order['side'] == 'BUY':
            order_price = price * \
                ((float(config.MESH_THRESHOLD) / 100) + 1)

            order_price = round(
                order_price, self.get_precision(filters.price_filter()['tickSize']))

            if self.create_test_limit_sell_order(
                    amount=qty, price=order_price):
                reorder = self.create_limit_sell_order(
                    amount=qty, price=order_price)
        else:
            order_price = price * \
                ((100 - float(config.MESH_THRESHOLD)) / 100)
            order_price = round(order_price, self.get_precision(
                filters.price_filter()['tickSize']))

            if self.create_test_limit_buy_order(
                    amount=qty, price=order_price):
                reorder = self.create_limit_buy_order(
                    amount=qty, price=order_price)

        return reorder

    def place_mesh_orders(self, buys: dict, sells: dict) -> list:
        """ Создаёт ордера покупки и продажи согласно сетке

        Args:
            buys (dict): Массив элеменов сетки для покупки
            sells (dict): Массив элеменов сетки для продажи

        Returns:
            list: Массив ID созданных ордеров
        """
        ids = []
        try:
            for item in sells:
                if self.create_test_limit_sell_order(amount=item['amount'], price=item['price']):
                    receipt = self.create_limit_sell_order(
                        amount=item['amount'], price=item['price'])
                    ids.append(receipt['orderId'])
        except Exception as e:
            print('Произошла ошибка при создании ордеров сетки на продажу')
            print(e)

        try:
            for item in buys:
                if self.create_test_limit_buy_order(amount=item['amount'], price=item['price']):
                    receipt = self.create_limit_buy_order(
                        amount=item['amount'], price=item['price'])
                    ids.append(receipt['orderId'])
        except Exception as e:
            print('Произошла ошибка при создании ордеров сетки на покупку')
            print(e)

        return ids

    @staticmethod
    def ask_order(symbol: str, id: int) -> list | None:
        """ Возвращает детальные данные ордера по ID и имени актива

        Args:
            symbol (str): Название торговой пары
            id (int): Идентификатор ордера

        Returns:
            list | None: JSON данные о ордере
        """
        try:
            data = Access.client().get_order(symbol=symbol, orderId=id)
        except Exception:
            return None
        else:
            return data

    @staticmethod
    def get_precision(number: float) -> int:
        """ Возвращает число знаков после запятой до значащей позиции

        Args:
            number (float): Дробное число

        Returns:
            int: Количество знаков после запятой или ноль, если таких нет.
        """
        number = str(number).rstrip('0')
        index = str(number)[::-1].find('.')

        if index == 1 and str(number)[-1] == '0':
            return 0

        return index
