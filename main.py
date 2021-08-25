"""
This POC tries to use data and analytics to find the options trades to
maximize profits.

The ideal process is as follows:

1. Create Earnings Calendar & Options objects and run to acquire Earnings
    Calendar Data & Valid Options List for Analysis

2. Validate data for weekly option symbols

3. Remove the symbols with a negative surprise & negative earnings

4. Get company summary & profile information

5. Get stock price history looking for stocks above SMA-20

6. Get option chain and look for profitable trading strategies


SYNTAX: python main.py
"""
import logging
import sys
import json
# import pyppdf.patch_pyppeteer
from requests_html import HTMLSession
# from pprint import pprint
# import pandas as pd
import os

import earnings_calendar
import options
import stocks
import price_history
import options_chain


###############################################################################
# ENABLE LOGGING
###############################################################################

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)-8s %(message)s",
    filename="logs/moneypress.log",
    filemode="a"
)
logger = logging.getLogger(__name__)


###############################################################################
# COMMON FUNCTIONS
###############################################################################


def get_symbol():
    """
    Functions get symbol if one is provided via command line. Eventually, this
    should run analysis on only the symbol provided.

    Args:
        None. Function gets arguments provided at the command line.

    Raises:
        None.

    Returns:
        None.
    """
    symbol = None
    try:
        if len(sys.argv) == 2:
            symbol = sys.argv[1].upper()
        else:
            symbol = input("Enter valid symbol: ")
    except Exception as e:
        error_message = f"ERROR ({e}): Invalid symbol. Enter 'python main.py [symbol]'"
        print(error_message)
        logging.error(error_message)
    return symbol


def get_web_content(url, elements):
    session = HTMLSession()
    r = session.get(url)
    # r.html.render()
    for element in elements:
        xpath = elements[element]["xpath"]
        try:
            elements[element]["value"] = r.html.xpath(xpath)[0].text
            elements[element]["attr"] = r.html.xpath(xpath)[0].attrs
            # print(r.html.xpath(xpath)[0].attrs)
        except Exception as e:
            logging.error(f"{e} | {element} | {xpath}")
            print(f"{e} | {element} | {xpath}")
    return elements


###############################################################################
# SAVE LOCAL DATA & LOAD LOCAL DATA LOGIC
###############################################################################
def save_local_data(data):
    # Check if directory exists.
    if not os.path.exists('data'):
        os.makedirs('data')
    # Save data.
    with open('data/moneypress_suggestions.json', 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))
        print("Money Press data saved.")
    return


def load_local_data():
    with open('data/moneypress_suggestions.json') as json_file:
        data = json.load(json_file)
        print(data)
        print("Money Press Suggestions data loaded.")
    return data


###############################################################################
# SAVE CLOUD DATA & LOAD CLOUD DATA
###############################################################################
def save_cloud_data(self):
    # TODO: Add feature to save data to cloud storage
    return


def load_cloud_data(self):
    # TODO: Add feature to load data from cloud storage
    return


###############################################################################
# MAIN SCRIPT PROCESS
###############################################################################
if __name__ == "__main__":
    '''
    1. Find long option no more than 60 days out
    2.
    '''
    #symbol = "btc-usd"
    #symbol = "WDAY"
    symbol = "TXT"
    #symbol = input("Enter symbol: ")
    #stock_history = stock_history.StockHistory(symbol)
    #stock_history.run()
    #option_chain = options_chain.OptionsChain(symbol)
    #option_chain.run()

    # Create Earnings Calendar & Options Objects
    ec = earnings_calendar.EarningsCalendar()
    opt = options.Options()

    # Acquire Earnings Calendar Data & Valid Options List for Analysis
    ec.run(source_local=False)
    opt.run(source_local=False)  # When was the last time the weekly option list changed?

    # Validate data for weekly option symbols
    data = opt.options_data
    valid_weekly_options = opt.validate_weekly_options(ec.earnings_calendar_data)
    print(valid_weekly_options)
    print(f"Current record count: {len(valid_weekly_options)}")

    # Remove the symbols with negative earnings

    # Remove the symbols with a negative surprise
    for symbol in list(valid_weekly_options):
        try:
            if valid_weekly_options[symbol]['Surprise(%)'] < 0 and valid_weekly_options[symbol]['Reported EPS'] < 0.10:
                valid_weekly_options.pop(symbol)
        except Exception as e:
            print(e)
            valid_weekly_options.pop(symbol)
    print(f"Updated record count after removing negative surprises: {len(valid_weekly_options)}")

    save_local_data(valid_weekly_options)

    # Get company summary & profile information
    for symbol in list(valid_weekly_options):
        # Create Stocks Company Profile object.
        s = stocks.CompanyProfile(symbol)
        s.run()

    # Get stock price history looking for stocks above SMA-20

    # Get option chain and look for profitable trading strategies
