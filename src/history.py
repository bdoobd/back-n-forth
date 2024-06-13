from pathlib import Path
import sys


class History:

    def __init__(self) -> None:
        self.log_dir = self.check_log_dir(Path('./logs'))
        self.log_file = self.log_dir / 'history.csv'
        self.headers = self.get_headers()

    def check_log_dir(self, dir_path: str) -> None:
        """ Проверяет наличие папки для логов и при отсутствии пытается её создать

        Args:
            dir_path (str): Путь к папке для логов
        """
        if not dir_path.exists():
            try:
                dir_path.mkdir()
            except Exception as e:
                print('Не удалось создать папку логов')
                print(e)
                sys.exit()

        return dir_path

    def get_headers(self) -> str:
        """ Заголовки для сsv файла

        Returns:
            str: Строка содержащая заголовк столбцов данных
        """
        return 'Timestamp,OrderID,Symbol,Type,Side,Qty,Price,Status\n'

    def write_history_header(self) -> None:
        """ Записывает заголовки столбцов для данных в файл
        """
        with open(self.log_file, 'w', encoding='UTF-8') as file:
            file.write(self.headers)

    def write_base_order(self, order: dict) -> None:
        """ Записывает в файл csv данные о базовом ордере

        Args:
            order (dict): Данные ордера
        """
        symbol = order['symbol']
        order_id = order['orderId']
        timestamp = order['workingTime']
        order_type = order['type']
        order_side = order['side']
        status = order['status']

        if len(order['fills']) > 1:
            qty = price = 0
            for trade in order['fills']:
                qty += trade['qty']
                price += trade['price']
        else:
            qty = order['fills'][0]['qty']
            price = order['fills'][0]['price']

        order_string = f'{timestamp},{order_id},{symbol},{order_type},{order_side},{qty},{price},{status}\n'

        with open(self.log_file, 'a', encoding='UTF-8') as file:
            file.write(order_string)

    def write_limit_order(self, order: dict) -> None:
        """ Записывает в файл csv данные лимитного ордера

        Args:
            order (dict): Данные ордера
        """
        symbol = order['symbol']
        order_id = order['orderId']
        # timestamp = order['workingTime']
        timestamp = order['updateTime'] if order['status'] == 'FILLED' else order['workingTime']
        order_type = order['type']
        order_side = order['side']
        status = order['status']
        price = order['price']
        qty = order['executedQty'] if order['status'] == 'FILLED' else order['origQty']

        order_string = f'{timestamp},{order_id},{symbol},{order_type},{order_side},{qty},{price},{status}\n'

        with open(self.log_file, 'a', encoding='UTF-8') as file:
            file.write(order_string)
