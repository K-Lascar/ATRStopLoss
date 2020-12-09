import concurrent.futures
from datetime import timedelta, datetime
from alpha_vantage.foreignexchange import ForeignExchange
import os.path
from colorama import Fore
import main

class AlphaForeignExchange:
    def __init__(self, from_symbol, to_symbol):
        self.from_symbol = from_symbol
        self.to_symbol = to_symbol
        self.__alpha_vantage_obj = ForeignExchange(main.get_api_alpha_vantage())
        self.__current_exchange_rate = self.retrieve_current_exchange()
        self.__data_set = self.retrieve_fx_data()

    def retrieve_current_exchange(self):
        """This function retrieves the exchange rate for a given pair."""
        dict_current_rate, _ = \
            self.get_alpha_vantage_obj().get_currency_exchange_rate(
                self.from_symbol, self.to_symbol)
        exchange_rate = dict_current_rate["5. Exchange Rate"]
        return exchange_rate

    def get_current_exchange(self):
        """This is a getter method for a current exchange rate."""
        return self.__current_exchange_rate

    def get_data_set(self):
        """This is the getter method for getting data set."""
        return self.__data_set

    def get_alpha_vantage_obj(self):
        """This is the getter method for getting alpha vantage object."""
        return self.__alpha_vantage_obj

    def retrieve_fx_data(self):
        """This function retrieves fx data for a given pair.
           This includes high, low, close, open values."""
        daily_data, _ = \
            self.get_alpha_vantage_obj().get_currency_exchange_daily(
                from_symbol=self.from_symbol, to_symbol=self.to_symbol)
        data_set = [value for key, value in daily_data.items()]
        return data_set

# Write to a file
def get_fx_data(from_symbol: str, to_symbol: str):
    future_day = timedelta(days=1) + datetime.now()
    new_path = os.getcwd() + "/price_collection_data/forex/"
    if not os.path.isfile(f"{new_path}price-data({from_symbol}-{to_symbol}).json") or \
            datetime.fromtimestamp(os.path.getctime(f"{new_path}\
            price-data({from_symbol}-{to_symbol}).json")) > \
            future_day:

        if (from_symbol, to_symbol) in main.list_of_fx_symbols():
            fx_obj = AlphaForeignExchange(from_symbol, to_symbol)
            data_set = fx_obj.get_data_set()
            executor_thread = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            executor_thread.submit(main.write_to_file, data_set, from_symbol,
            to_symbol, new_path)
            atr_data_set = main.calculate_atr(data_set, "2. high", "3. low",
                "4. close")
            return tuple([atr_data_set, float(data_set[-1]["4. close"])])
        else:
            print(Fore.RED + "RECEIVED INVALID SYMBOL PAIR" + Fore.RESET)
            exit(0)
    current_daily_set = main.read_from_file(from_symbol, to_symbol, new_path)
    return tuple([main.calculate_atr(current_daily_set, "2. high", "3. low",
        "4. close"), float(current_daily_set[-1]["4. close"])])