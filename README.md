# Создание и сопровождение торговой сетки на Binance

## Настойка

> Конфигурационный файл находится по пути `./config/config.py`

Ключ **TESTNET** определяет, будет ли работа скрипта происходить в тестовом режиме или боевом.

- Значение **True** - использование в тестовом режиме. Используются тестовые ключи и точка подключения к Binance.
- Значение **False** - ключи и подключение в режмие торговли на бирже.

**TRADE_PAIR** - название квотируемого актива, который планируется использовать при торговле.

**ORDERS_AMOUNT** - количество линий сетки для продажи и покупки. В итоге кличество ордеров x2.

**MESH_THRESHOLD** - шаг сетки в процентах.

**UNWANTED** - Список торговых пар исключённых из анализа активов. Не используется на данный момент.

**KLINE_DAYS** - количество дней для исторической выборки актива. Данные используются для анализа состояния актива.

## Запуск скрипта

> Для создания и сопровождения торовой сетки запустить файл `./app.py`

- **cd** в папку с проектом
- для Windows: `python.exe app.py`
- для Linux/MacOS X: `python3 app.py`

## Работа скрипта

При первом запуске будет запрошен базовый актив для работы (регистронезависимый ввод) и количество для базовой закупки.

После создания торговой сетки скрипт будет проверять состояние LIMIT ордеров в цикле. При выполнении какого либо из ордеров будет выставлен обратный ордер с данными из выполенного ордера.

После выключения и повторного запуска скрпита запрос актива и количества опускается и сразу начинается проверка состояния ордеров.

## Проверка статистики

> Для проверки выполенных ордеров и израсходованных/полученых средствах запустить файл `./get_history.py`

- **cd** в папку с проектом
- для Windows: `python.exe get_history.py`
- для Linux/MacOS X: `python3 get_history.py`

:moneybag:
