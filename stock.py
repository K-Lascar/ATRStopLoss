from alpha_vantage.timeseries import TimeSeries
from datetime import timedelta, datetime
import concurrent.futures
from click._compat import raw_input
import os.path
import main

class AlphaStockTimeSeries:
    def __init__(self, ticker):
        self.ticker = ticker
        self.__alpha_vantage_obj = TimeSeries(main.get_api_alpha_vantage())
        self.__data_set = self.retrieve_stock_data()

    def retrieve_stock_data(self):
        """This function will retrieve the stock data set."""
        while True:
            try:
                weekly_data, meta_data = \
                self.get_alpha_vantage_obj().get_weekly(self.ticker)
            except ValueError:
                print("INVALID TICKER")
                ticker = raw_input("Enter a valid ticker: ")
                self.set_ticker(ticker=ticker)
            else:
                weekly_data_set = [value for key, value in weekly_data.items()]
                return weekly_data_set

    def get_data_set(self):
        """This is the getter method for getting data set."""
        return self.__data_set

    def get_alpha_vantage_obj(self):
        """This is the getter method for getting alpha vantage object."""
        return self.__alpha_vantage_obj

    def set_ticker(self, ticker):
        """This function will set the ticker."""
        self.ticker = ticker

def get_stock_data(ticker: str):
    future_day = timedelta(days=1) + datetime.now()
    new_path = os.getcwd() + "/price_collection_data/stock/"
    if not os.path.isfile(f"{new_path}price-data({ticker}).json") or \
            datetime.fromtimestamp(os.path.getctime(f"{new_path}\
            price-data({ticker}).json")) > future_day:
        stock_obj = AlphaStockTimeSeries(ticker)
        data_set = stock_obj.get_data_set()
        executor_thread = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        executor_thread.submit(main.write_to_file, data_set, ticker, None, new_path)
        atr_collection = main.calculate_atr(data_set, "2. high", "3. low",
            "4. close")
        return tuple([atr_collection, float(data_set[-1]["4. close"])])
    current_weekly_set = main.read_from_file(ticker, None, new_path)
    return tuple([main.calculate_atr(current_weekly_set, "2. high", "3. low",
                 "4. close"), float(current_weekly_set[0]["4. close"])])