"""
    Ключ для определения типа торговли.
    Если ключ установлен в True, то скрипт запускается в тестовом режиме.
    Для нормальной торговли установить ключ в False.
    Пример: TESTNET = False
"""
TESTNET = True

# Ключи доступа
# Ключи для нормальной аутетификации на Binance
api_key = 'api_key'
secret_key = 'secret_key'

# Ключи для тестов
api_key_test = 'api_key'
secret_key_test = 'secret_key'

# Интересующая торговая пара
TRADE_PAIR = 'USDT'

# Базовый URL Binance
BASE_URL = 'https://api.binance.com'

# Количество ордеров (сетки)
ORDERS_AMOUNT = 5

# Шаг торговой сетки в процентах
MESH_THRESHOLD = 2

# Массив наименований активов для исключения из поиска
UNWANTED = ['EURUSDT', 'GBPUSDT', 'JPYUSDT', 'USDUSDT', 'DOWN', 'UP']

# Количество дней в прошлом для запроса исторических данных
KLINE_DAYS = 20
