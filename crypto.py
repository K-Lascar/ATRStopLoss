from datetime import datetime, timedelta
# from alpha_vantage.cryptocurrencies import CryptoCurrencies
import concurrent.futures
import requests
import main
import os.path

def get_crypto_data(base_symbol: str, market_symbol: str, limit=1, all_data='true'):
    """Retrieves Crypto Data for a given base_symbol/market_symbol i.e. BTC/USD"""
    new_path = os.getcwd() + "/price_collection_data/crypto/"
    future_day = timedelta(days=1) + datetime.now()
    if not os.path.isfile(f"{new_path}price-data({base_symbol}-{market_symbol}).json") or \
        datetime.fromtimestamp(os.path.getctime(f"{new_path}price-data({base_symbol}-{market_symbol}).json")) \
            > future_day:

        """URL Retrieving Price Information"""
        api = main.get_api_crypto_watch()
        base_url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={base_symbol}&tsym={market_symbol}&limit={limit}&allData={all_data}&api_key={api}"
        response = requests.get(base_url)
        if response.json()["Response"] == "Success":

            # 7 step indicates weekly data collected.
            weekly_data = response.json()["Data"]["Data"][::7]
            weekly_data.reverse()
            executor_thread = \
                concurrent.futures.ThreadPoolExecutor(max_workers=1)
            executor_thread.submit(main.write_to_file, weekly_data, base_symbol,
            market_symbol, new_path)
            atr_collection = main.calculate_atr(weekly_data, "high", "low", "close")

            return tuple([atr_collection, weekly_data[-1]["close"]])
        else:
            print(response.json()["Message"])
            exit(0)
    weekly_data = main.read_from_file(base_symbol, market_symbol, new_path)
    return tuple([main.calculate_atr(weekly_data, "high", "low", "close"),
    weekly_data[0]["close"]])


# ALPHA VANTAGE - HAS LESS CRYPTO DATA!
# def get_crypto_data(symbol: str, market: str):
#     # future_day = timedelta(days=1) + datetime.now()
#     alpha_vantage_obj = CryptoCurrencies(key=get_api_alpha_vantage())
#     try:
#         weekly_data, meta_data = alpha_vantage_obj.get_digital_currency_weekly(symbol=symbol, market=market)
#     except ValueError:
#         print("Invalid Value Provided")
#         exit(0)
#     else:
#         print(weekly_data)
#         print(datetime.now() - timedelta(weeks=22))
#         # print(talib.AVGPRICE())
#         data_set = [value for key, value in weekly_data.items()]
#         high_values = list(map(lambda x: x["2b. high (USD)"], data_set))
#         high_values.reverse()
#         high = numpy.array(high_values, dtype=float)
#         print(high)
#         print(talib.EMA(high))
#         atr_collection = calculate_atr(data_set, "2b. high (USD)", "3b. low (USD)", "4b. close (USD)")
#         return atr_collection