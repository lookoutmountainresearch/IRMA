
import logging
# from lxml.html.clean import Cleaner
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from datetime import datetime
import os
import json
from statistics import mean, pstdev

###############################################################################
# MODULE INFO
###############################################################################
__author__ = "Matthew Hess <matt@lookoutmountainresearch.com>"
__email__ = "matt@lookoutmountainresearch.com"
__status__ = "Prototype"  # "Prototype", "Development", or "Production"
__version__ = "0.0.1"
__date__ = "2021-06-09"
__copyright__ = "Copyright 2021, Lookout Mountain Research, LLC"
__license__ = "Proprietary"
__maintainer__ = "Matthew Hess"
__credits__ = []


###############################################################################
# ENABLE LOGGING
#
# REWRITE using native Python standard library.
###############################################################################

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)-8s %(message)s",
    filename="logs/price_history.log",
    filemode="a"
)
logger = logging.getLogger(__name__)


def print_to_screen(msg):
    '''
    Function prints message to screen.
    '''
    print(msg)
    return


def write_to_log(msg, log_level):
    '''
    Function that writes messages to the standard log.

        Args:
            Message - The message to be written/displayed.
            Log Level - Determines the log level for logging.
                DEBUG
                INFO
                WARNING
                ERROR
                CRITICAL

        Raises:
            CRITICAL - Raises in correct log level.

        Returns:
            None.
    '''
    log_levels = ["DEBUG",
                    "INFO",
                    "WARNING",
                    "ERROR",
                    "CRITICAL",
                    "EXCEPTION"]
    log_level_caps = log_level.upper()
    if log_level_caps not in log_levels:
        logger.critical(f"{log_level_caps} not valid log level.")
        print_to_screen(f"{log_level_caps} not valid log level.")
    else:
        if log_level_caps == "DEBUG":
            logger.debug(msg)
        elif log_level_caps == "INFO":
            logger.info(msg)
        elif log_level_caps == "WARNING":
            logger.warning(msg)
        elif log_level_caps == "ERROR":
            logger.error(msg)
        elif log_level_caps == "CRITICAL":
            logger.critical(msg)
        elif log_level_caps == "EXCEPTION":
            logger.exception(msg)
    return


def log_print(msg, log_level, log_only_bool):
    '''
    Function that writes messages to the standard log and to the screen.

        Args:
            Message - The message to be written/displayed.
            Log Level - Determines the log level for logging.
            Log Only - True/False to determine if logs message and prints to
                the screen or writes to the log only.

        Raises:
            None.

        Returns:
            None.
    '''
    if log_only_bool is True:
        write_to_log(msg, log_level)
    else:
        write_to_log(msg, log_level)
        print_to_screen(msg)
    return


###############################################################################
# STOCK HISTORY CLASS TO GET A LIST OF STOCK PRICES FOR A SYMBOL
###############################################################################
class PriceHistory():
    '''
    The PriceHistory class gets the price history for a given symbol and runs
    analysis on the price history. The analysis is stored as class variable
    data with options to save data to local directory or cloud storage.

    Example:
        ph = PriceHistory("GE")
        ph.run()
        print(ph.current_sma)
        print(ph.current_stdev)   
    '''

    def __init__(self, symbol):
        """
        Instance contains the following variables:
            * Symbol - Symbol of company used to gather data.
            * CONFIG URL - URL used to get the data.
            * CONFIG Save Path - Path and file name to save the data locally.
            * CONFIG Period Length - The number of historical records to
                analyze.
            * Price History Data - Data collected for price history. Format is
                a dictionary.
            * SMA Data - Simple moving average data. Data saved as dictionary.
            * Standard Deviation Data - Standard Deviation of the price close
                data.

        """
        # CONFIGURATION
        self.symbol = symbol
        self.config_url = f"https://finance.yahoo.com/quote/{self.symbol}/history?p={self.symbol}"
        self.config_save_path = f'data/price_history_by_symbol/{self.symbol}.json'
        self.config_period_length = 20
        # DATA
        self.price_history_data = {}
        self.current_price = -1
        self.sma_data = {}
        self.standard_deviation_data = {}
        # ANALYSIS METRICS
        self.close_trend_days = [1, 3, 9]
        self.close_trend_data = []
        self.is_trend_positive = ""             # boolean
        self.is_close_greater_than_sma = ""     # boolean
        self.is_close_nearer_2_stdev = ""       # boolean
        return

    def convert_date_to_seconds(self, ex_date_str):
        '''
        Provide a valid date and function will convert date to seconds from
        1/1/1970.

        Args:
            date (str): Requires date in string format '%Y-%m-%d'.

        Raises:
            None.

        Returns:
            Seconds (seconds): Number of seconds between date given
                and 1970-01-01.
        '''
        start_date_str = '1970-01-01'
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        ex_date = datetime.strptime(ex_date_str, '%b %d, %Y')
        difference = (ex_date - start_date)
        date_in_seconds = int(difference.total_seconds())
        log_print(f'''Calcuated seconds between "{start_date_str}"
            and "{ex_date_str}" to be {date_in_seconds} .''',
            "DEBUG", True)
        return date_in_seconds

    def scrape_price_history(self):
        '''
        Function scrapes data from the price history webpage and returns
        the results.

        Args:
            None. URL is set in the __init__ function.

        Raises:
            CRITICAL - if status_code is anything other than 200
            CRITICAL - if no response from the website

        Returns:
            webpage_results (obj)
        '''
        session = HTMLSession()
        log_print("HTML Session started.", "INFO", False)

        # Get contents of the page
        try:
            webpage_results = session.get(self.config_url)

            # Render page results
            # webpage_results.html.render(scrolldown=250)

            # Get status code for web results
            status = webpage_results.status_code

            if status == 200:
                log_print(f"Recieved results from {self.config_url}", "INFO", True)
            else:
                log_print(f"Returned status code: {status}", "CRITICAL", False)
                webpage_results = ""
        except Exception as e:
            log_print(f"No response from web - {e}", "CRITICAL", False)
            webpage_results = ""
        return webpage_results

    def get_price_history_data(self):
        '''
        Gets the price history data and processes the headings & rows into
        a Python dictionary; utilimately saving the data to either the
        local filesystem or cloud storage.

        Args:
            None.

        Raises:
            None.

        Returns:
            None.
        '''
        webpage_html = self.scrape_price_history()

        # Find table data headings
        headings_xpath = '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/thead'
        headings_results = webpage_html.html.xpath(headings_xpath, first=True)
        headings_soup = BeautifulSoup(headings_results.html, "lxml")
        headings_html = headings_soup.find_all("th")
        headings = []
        for heading in headings_html:
            headings.append(heading.text.strip("*"))
            # self.price_history_data[heading.text.strip("*")] = []

        # Set table data to variable.
        stock_history_table_xpath = '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody'
        stock_history_table_data = webpage_html.html.xpath(
            stock_history_table_xpath, first=True)
        stock_history_soup = BeautifulSoup(
            stock_history_table_data.html, "lxml")

        # Find rows in the table
        stock_history_rows = stock_history_soup.find_all("tr")

        # Cycle through each row of the table, validate data, & set to dictionary
        for row in stock_history_rows:
            cells = row.find_all("td")
            if len(cells) == 7:
                self.price_history_data[self.convert_date_to_seconds(cells[0].text)] = {
                    headings[0]: cells[0].text,
                    headings[1]: float(cells[1].text.replace(",", "")),
                    headings[2]: float(cells[2].text.replace(",", "")),
                    headings[3]: float(cells[3].text.replace(",", "")),
                    headings[4]: float(cells[4].text.replace(",", "")),
                    headings[5]: float(cells[5].text.replace(",", "")),
                    headings[6]: int(cells[6].text.replace(",", ""))
                }
        # Validation
        log_print(headings, "DEBUG", True)
        log_print(self.price_history_data, "DEBUG", True)
        self.save_local_data(self.price_history_data)
        return

    def get_simple_moving_average_data(self):
        '''
        Populates the self.sma_data object variable with all the simple moving
        averages based on period length.

        Args:
            None.

        Raises:
            None.

        Return:
            None. Sets the self.sma_data list variable.
        '''

        # Set start and end to get list of values
        end = len(self.price_history_data)
        start = end - self.config_period_length

        # Get a list of indexes
        index = []
        for date_index in self.price_history_data:
            index.append(date_index)
        log_print(f"Date Indexes: {index}", "DEBUG", True)

        # Loop through each period until at the end of the data
        while start > 0:
            log_print(index[start:end], "DEBUG", True)
            values = []
            for entry in index[start:end]:
                values.append(self.price_history_data[entry]['Close'])
            key = self.convert_date_to_seconds(self.price_history_data[entry]["Date"])
            self.sma_data[str(key)] = mean(values)
            start -= 1
            end -= 1
        #self.sma_data.reverse()
        log_print(f"SMA Data: {self.sma_data}", "DEBUG", True)
        return

    def get_simple_moving_average(self, day):
        '''
        Retrieves simple moving average from the class given a day.

        Args:
            Day - Format of date, YYYY-MM-DD.

        Raises:
            CRITICAL - Invalid date or date format
            WARNING - No record exists

        Return:
            Simple moving average as float
        '''
        # Check if the variable is a valid date
        try:
            valid_date = datetime.strptime(day, '%Y-%m-%d')
        except Exception as e:
            log_print(e, "ERROR", False)
        
        # Check for record and return value.
        date_seconds = self.convert_date_to_seconds(valid_date)
        sma = self.sma_data[date_seconds]
        if sma == "":
            sma = -1
            log_print(f"WARNING: SMA does not exist. Returned {sma}.",
                "WARNING", False)
        else:
            sma = sma
        return sma

    def get_standard_deviation_data(self):
        '''
        Populates the self.standard_deviation_data object variable with all
        the standard deviations based on period length.

        Args:
            None.

        Raises:
            None.

        Return:
            None. Sets the self.sma_data list variable.
        '''

        # Set start and end to get list of values
        end = len(self.price_history_data)
        start = end - self.config_period_length

        # Get a list of indexes
        index = []
        for date_index in self.price_history_data:
            index.append(date_index)
        log_print(f"Date Indexes: {index}", "DEBUG", True)

        # Loop through each period until at the end of the data
        while start > 0:
            log_print(index[start:end], "DEBUG", True)
            values = []
            for entry in index[start:end]:
                values.append(self.price_history_data[entry]['Close'])
            key = self.convert_date_to_seconds(self.price_history_data[entry]["Date"])
            self.standard_deviation_data[str(key)] = pstdev(values)
            start -= 1
            end -= 1
        #self.standard_deviation_data.reverse()
        log_print(f"ST DEV Data: {self.standard_deviation_data}", "DEBUG", True)
        return

    def get_standard_deviation(self, day):
        '''
        Retrieves standard deviation of close prices from the class given a
        day.

        Args:
            Day - Format of date, YYYY-MM-DD.

        Raises:
            CRITICAL - Invalid date or date format
            WARNING - No record exists

        Return:
            Standard deviation as float
        '''
        # Check if the variable is a valid date
        try:
            valid_date = datetime.strptime(day, '%Y-%m-%d')
        except Exception as e:
            log_print(e, "ERROR", False)
        
        # Check for record and return value.
        date_seconds = self.convert_date_to_seconds(valid_date)
        stdev = self.standard_deviation_data[date_seconds]
        if stdev == "":
            stdev = -1
            log_print(f"WARNING: Standard Deviation does not exist. Returned {stdev}.",
                "WARNING", False)
        else:
            stdev = stdev
        return

    ###########################################################################
    # ANALYTICS LOGIC
    ###########################################################################



    def run_analytics(self):
        return

    ###########################################################################
    # SAVE LOCAL DATA & LOAD LOCAL DATA LOGIC
    ###########################################################################
    def save_local_data(self, data):
        '''
        Saves data to local filesystem under a directory
            data/price_history_by_symbol/[symbol].json.

        Args:
            data (dict): Dictionary data to be saved as json in file

        Raises:
            None.

        Returns:
            None. Saves data in file named
                data/price_history_by_symbol/[symbol].json.
        '''
        save_path = self.config_save_path.strip(f'/{self.symbol}.json')
        # Check if directory exists.
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        # Save data.
        with open(self.config_save_path, 'w') as outfile:
            json.dump(data, outfile, sort_keys=True,
                      indent=4, separators=(',', ': '))
            print("Price History data saved.")
        return

    def load_local_data(self):
        '''
        Loads profile data from a local file called [symbol].json in a
        directory named data/price_history_by_symbol/[symbol].json. Returns
        data in a Python dictionary format.

        Args:
            None.

        Raises:
            CRITICAL: Logs critical message if file doesn't exist.

        Returns:
            data (dict): updates data in profile_data attribute the profile
                data in the data/price_history_by_symbol/[symbol].json file.
        '''
        with open(self.config_save_path) as json_file:
            data = json.load(json_file)
            self.earnings_calendar_data = data
            print("Stock History data loaded.")
        return data

    ###########################################################################
    # RUN COMMAND
    ###########################################################################
    def run(self, **kwargs):
        '''
        Populates price history information about either a company or ETF. If
        no source is specified, data will be sourced from web.

        Args:
            OPTIONAL source_web (bool): kwargs used to get options list from
                the web. By default, if no kwargs are specified, run will get
                data from the web.
            OPTIONAL source_local (bool): kwargs to load data from
                data/option.json if exists. If option.json does not exist,
                function will get data from the web.

        Raises:
            None.

        Returns:
            None.
        '''

        # Set Python kwargs to variable
        log_print(kwargs, "INFO", False)
        web_data_arg = kwargs.get("source_web", False)
        local_data_arg = kwargs.get("source_local", False)

        if local_data_arg is not False or web_data_arg is True:
            self.get_price_history_data()
        else:
            self.price_history_data = self.load_local_data()
        print("running simple moving averages")
        self.get_simple_moving_average_data()
        self.get_standard_deviation_data()
        return


if __name__ == "__main__":
    symbol = "MSFT"
    sh = PriceHistory(symbol)
    sh.run(source_web=True)
    #print(sh.price_history_data)
    #print(f"Number of stock history records: {len(sh.price_history_data)}")
    #print(f"Simple Moving Averages: {sh.sma_data}")
    #print(len(sh.sma_data))
    #print(f"Standard Deviations: {sh.standard_deviation_data}")
    #print(len(sh.standard_deviation_data))
