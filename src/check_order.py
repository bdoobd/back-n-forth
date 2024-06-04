from pathlib import Path
from src.trade_log import Trade_Log
import json
import time


class Check_Order:
    def __init__(self, log_file: str) -> None:
        self._log_dir = Trade_Log().log_dir
        self._log_file = self._log_dir / log_file

    def read_log_file(self):
        with open(self._log_file, 'r') as file:
            try:
                data = json.load(file)
            except json.decoder.JSONDecodeError:
                data = {}

        return data if len(data) > 0 else False

    @property
    def log_file(self):
        if not self._log_file.exists() or not self._log_file.is_file():
            return False

        return self._log_file

    def no_open_orders(self) -> bool:
        if not self.log_file or not self.read_log_file():
            return True

        return False

    def loop_orders(self, ids: dict) -> None:
        if len(ids) < 1:
            print('Нет ордеров для отслеживания')
            raise ValueError('Массив ID заказов пуст, нечего отслеживать')

        for key, values in ids.items():
            coin = key
            orders = values

        return [coin, orders]

    def check_order_filled(self, order: dict) -> bool:
        if order['status'] == 'FILLED':
            return True

        return False
