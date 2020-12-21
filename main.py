from pprint import pprint
import numpy
import talib
from click._compat import raw_input
from datetime import datetime, timedelta
from json import dump, loads
from colorama import Fore
from itertools import permutations
from distutils.util import strtobool
import forex
import stock
import crypto
# Useful Command for env python3 -m pip install colorama

def list_of_fx_symbols():
    """This function returns all the possible fx permutations (Using ECB Data)"""
    fx_pairs = ['USD', 'JPY', 'BGN', 'CZK', 'DKK', 'GBP', 'HUF', 'PLN', 'RON',
                'SEK', 'CHF', 'ISK', 'NOK', 'HRK', 'RUB', 'TRY', 'AUD', 'BRL',
                'CAD', 'CNY', 'HKD', 'IDR', 'ILS', 'INR', 'KRW', 'MXN', 'MYR',
                'NZD', 'PHP', 'SGD', 'THB', 'ZAR', 'EUR']
    return permutations(fx_pairs, 2)

# Best Data for Crypto!
def get_api_crypto_watch():
    """Retrieves api from crypto watch"""
    return "<https://cryptowat.ch/products/cryptocurrency-market-data-api>"

# BEST OVERALL DATA!
def get_api_alpha_vantage():
    """Retrieves api from alpha vantage"""
    return "<https://www.alphavantage.co/support/#api-key>"

def retrieve_raw_data_list(data_set, key) -> list:
    """Retrieves the raw data in a list format using the passed key."""
    data_set_list = list(map(lambda x: x[key], data_set))
    return data_set_list

def calculate_atr(data_set, high_key, low_key, close_key, time_period=14):
    """Calculates the ATR from a given data_set using the open, high, close
    values."""
    data_set.reverse()
    high_values = numpy.array(retrieve_raw_data_list(data_set, high_key),
    dtype=float)
    low_values = numpy.array(retrieve_raw_data_list(data_set, low_key),
    dtype=float)
    close_values = numpy.array(retrieve_raw_data_list(data_set, close_key),
    dtype=float)
    atr_collection = talib.ATR(high_values, low_values, close_values,
    timeperiod=time_period)
    numpy.set_printoptions(suppress=True)
    return atr_collection

def write_to_file(data_set, from_symbol: str, to_symbol, path: str) -> None:
    """This function will output a given data_set into a specific file"""
    file_path = f"{path}price-data({from_symbol}-{to_symbol}).json" \
        if to_symbol is not None \
        else f"{path}price-data({from_symbol}).json"
    output_stream = open(file_path, "w")
    dump(data_set, output_stream)
    output_stream.close()

def read_from_file(from_symbol: str, to_symbol, path: str):
    """This function will retrieve a given data_set from a specific file"""
    file_path = f"{path}price-data({from_symbol}-{to_symbol}).json" \
        if to_symbol is not None \
        else f"{path}price-data({from_symbol}).json"
    input_stream = open(file_path, "r")
    price_data = loads(input_stream.read())
    input_stream.close()
    return price_data

# This function will print the pnl if the user specifies it.
def print_pnl(check_profitable, profit_or_loss) -> None:

    # If user has said a true value we will return PNL.
    if strtobool(check_profitable): # Change to bool type
        if profit_or_loss > 0:
            print(Fore.GREEN + f"{profit_or_loss}" + Fore.RESET)
        else:
            print(Fore.RED + f"{profit_or_loss}" + Fore.RESET)

def print_result(entry_price, atr_data, recent_price) -> None:
    """Prints the result to the user"""
    atr_pos = raw_input("Enter Position Type (S/L): ").upper()
    multi_factor = 1.5

    # Ego boosting question.
    check_profitable = raw_input("Would you like to see if your profitable \
    (Y/N)? ").upper()
    if atr_pos == 'S':
        stop_loss = entry_price + atr_data[-1] * multi_factor
        print(f"STOP LOSS: {stop_loss}\n")
        profit_or_loss = entry_price - recent_price
        print_pnl(check_profitable, profit_or_loss)
    elif atr_pos == "L":
        stop_loss = entry_price - atr_data[-1] * multi_factor
        print(f"STOP LOSS: {stop_loss}\n")
        profit_or_loss = recent_price - entry_price
        print_pnl(check_profitable, profit_or_loss)

def retrieve_entry_position() -> float:
    """This function retrieves the entry position from user"""
    entry = 0
    while True:
        try:
            entry = float(raw_input("Enter Entry Position: "))
        except ValueError:
            print(Fore.RED + "Enter valid entry position!!!" + Fore.RESET)
            continue
        else:
            break
    return entry

def main() -> None:
    while True:
        print(Fore.GREEN + """
      /$$$$$$ /$$$$$$$$/$$$$$$$        /$$$$$$$ /$$$$$$$  /$$$$$$  /$$$$$$
     /$$__  $|__  $$__| $$__  $$      | $$__  $| $$__  $$/$$__  $$/$$__  $$
    | $$  \ $$  | $$  | $$  \ $$      | $$  \ $| $$  \ $| $$  \ $| $$  \__/
    | $$$$$$$$  | $$  | $$$$$$$/      | $$$$$$$| $$$$$$$| $$  | $| $$ /$$$$
    | $$__  $$  | $$  | $$__  $$      | $$____/| $$__  $| $$  | $| $$|_  $$
    | $$  | $$  | $$  | $$  \ $$      | $$     | $$  \ $| $$  | $| $$  \ $$
    | $$  | $$  | $$  | $$  | $$      | $$     | $$  | $|  $$$$$$|  $$$$$$/
    |__/  |__/  |__/  |__/  |__/      |__/     |__/  |__/\______/ \______/
                                                                            """
              + Fore.RESET)
        print(Fore.LIGHTMAGENTA_EX + f"<<<         CRYPTO(C)             >>>"
        + Fore.RESET)
        print(Fore.LIGHTCYAN_EX + f"<<<         STOCKS(S)             >>>" +
        Fore.RESET)
        print(Fore.LIGHTBLUE_EX + f"<<<         FOREX(F)             >>>" +
        Fore.RESET)
        type_of_conversion = raw_input("Enter Type of Conversion: ").upper()

        entry = retrieve_entry_position()

        if type_of_conversion.upper() in ["C", "S", "F"]:
            if type_of_conversion.upper() == "C":
                first_pair = raw_input("Enter First Pair: ").upper()
                sec_pair = raw_input("Enter Second Pair: ").upper()
                atr_data, recent_price = crypto.get_crypto_data(first_pair, sec_pair)
                print_result(entry, atr_data, recent_price)
            elif type_of_conversion.upper() == "S":
                ticker = raw_input("Enter Ticker: ")
                atr_data, recent_price = stock.get_stock_data(ticker)
                print_result(entry, atr_data, recent_price)
            elif type_of_conversion.upper() == "F":
                first_pair = raw_input("Enter First Pair: ").upper()
                sec_pair = raw_input("Enter Second Pair: ").upper()
                atr_data, recent_price = forex.get_fx_data(first_pair, sec_pair)
                print_result(entry, atr_data, recent_price)
        else:
            print("PROGRAM WILL EXIT!")
            exit(0)

if __name__ == "__main__":
    main()
