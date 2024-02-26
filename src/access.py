from binance.client import Client as BinanceClient
from binance.exceptions import BinanceAPIException
import config.config as config


class Access:
    _client = None

    def __init__(self) -> None:
        raise RuntimeError(
            'Прямое создание объекта не доступно\nДопускается вызов метода Access.client()')

    @classmethod
    def client(cls):
        if not cls._client:
            access = cls.__new__(cls)
            if (config.TESTNET):
                print('Testing environment')
                cls._client = BinanceClient(
                    config.api_key_test, config.secret_key_test)
                cls._client.API_URL = 'https://testnet.binance.vision/api'
            else:
                print('Production environment')
                cls._client = BinanceClient(config.api_key, config.secret_key)

        return cls._client

    @staticmethod
    def get_api_key() -> str:
        if (config.TESTNET):
            return config.api_key_test
        else:
            return config.api_key
