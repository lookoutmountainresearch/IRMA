
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
        self.close_trend_average = 0.00
        self.is_trend_positive = ""             # boolean
        self.is_close_greater_than_sma = ""     # boolean
        self.is_close_nearer_2_stdev = ""       # boolean
        self.price_history_score = 0.00
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

//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr[1]/td[2]

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

        # Get current price
        current_price_xpath = '//*[@id="quote-header-info"]/div[3]/div[1]/div[1]/span[1]'
        current_price_results = webpage_html.html.xpath(current_price_xpath, first=True)
        self.current_price = current_price_results.text
        log_print("INFO: Set current price.", "INFO", False)

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
        log_print("INFO: Set price history data.", "INFO", False)
        log_print(headings, "DEBUG", True)
        log_print(self.price_history_data, "DEBUG", True)
        self.save_local_data()
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

        log_print("INFO: Getting simple moving average data.", "INFO", False)

        # Set start and end to get list of values
        absolute_end = len(self.price_history_data) - 1

        # Get a list of indexes
        index = []
        for date_index in self.price_history_data:
            index.append(date_index)
        index.sort()
        log_print(f"Date Indexes: {index}", "DEBUG", True)

        # Loop through each period until at the end of the data
        subset_length = self.config_period_length
        cycle = 0
        while subset_length == self.config_period_length:
            end = absolute_end - cycle
            start = end - self.config_period_length
            end_key = index[end]
            log_print(index[start:end], "DEBUG", True)
            values = []
            for entry in index[start:end]:
                values.append(self.price_history_data[entry]['Close'])
            subset_length = len(values)
            if subset_length == self.config_period_length:
                key = self.convert_date_to_seconds(self.price_history_data[end_key]["Date"])
                self.sma_data[str(key)] = mean(values)
            cycle += 1
   
        log_print(f"SMA Data: {self.sma_data}", "DEBUG", True)
        self.save_local_data()
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

        log_print("INFO: Getting standard deviation data.", "INFO", False)

        # Set start and end to get list of values
        absolute_end = len(self.price_history_data) - 1

        # Get a list of indexes
        index = []
        for date_index in self.price_history_data:
            index.append(date_index)
        index.sort()
        log_print(f"Date Indexes: {index}", "DEBUG", True)

        # Loop through each period until at the end of the data
        subset_length = self.config_period_length
        cycle = 0
        while subset_length == self.config_period_length:
            end = absolute_end - cycle
            start = end - self.config_period_length
            end_key = index[end]
            log_print(index[start:end], "DEBUG", True)
            values = []
            for entry in index[start:end]:
                values.append(self.price_history_data[entry]['Close'])
            subset_length = len(values)
            if subset_length == self.config_period_length:
                key = self.convert_date_to_seconds(self.price_history_data[end_key]["Date"])
                self.standard_deviation_data[str(key)] = pstdev(values)
            cycle += 1
   
        #self.standard_deviation_data.reverse()
        log_print(f"ST DEV Data: {self.standard_deviation_data}", "DEBUG", True)
        self.save_local_data()
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

    # Check price trends - Is price history on upward trend?
    def check_price_history_trends(self):
        '''
        This function is used to determine if the close price for a symbol is
        trending up or down.

        Args:
            None. Configure the ranges for trend analysis by setting the
            self.close_trend_days in the object variable. For instance, if 1, 
            3, & 9 are provided, analysis ranges will be 0-1, 1-3, and 3-9
            days. An average of all ranges will determine if trend is positive
            (True) or negative (False).

        Raises:
            CRITICAL - Cannot divid by zero.

        Returns:
            None. The function sets the self.close_trend_average and
            self.is_trend_positive object variables.
        '''
        # Get day in seconds for each in range and set to dictionary
        price_history_days = []
        for each_day in self.price_history_data:
            price_history_days.append(each_day)

        trend_ranges = {}
        trend_ranges_counter = 1

        for day in self.close_trend_days:
            # Find the start range
            if trend_ranges == {}:
                start_range = price_history_days[len(price_history_days)-1]
            else:
                start_range = trend_ranges[trend_ranges_counter-1][1]

            # Find the end range
            day_location = len(price_history_days) - self.close_trend_days[trend_ranges_counter-1]
            end_range = price_history_days[day_location-1]
            
            # Store the range
            trend_ranges[trend_ranges_counter] = [start_range, end_range]

            trend_ranges_counter += 1
        
        log_print(price_history_days, "DEBUG", True)
        log_print(trend_ranges, "DEBUG", True)

        # Calcuate the trends given the ranges
        # Formula for slope given to points is m=(y2-y1)/(x2-x1)
        # x will be date in seconds (trend_ranges)
        # y will be close price (self.price_history_data)
        for range in trend_ranges:
            x1 = trend_ranges[range][1]
            x2 = trend_ranges[range][0]
            y1 = self.price_history_data[x1]["Close"]
            y2 = self.price_history_data[x2]["Close"]
            try:
                m = (y2-y1)/(x2-x1)
            except Exception as e:
                log_print(e, "CRITICAL", False)
            self.close_trend_data.append(m)

        # Get average and determine is trend is positive/negative
        self.close_trend_average = mean(self.close_trend_data)
        if self.close_trend_average > 0:
            self.is_trend_positive = True
        else:
            self.is_trend_positive = False
        log_print(f"INFO: Average price history trend: {self.close_trend_average}", "DEBUG", False)
        log_print(f"INFO: Is trend positive? {self.is_trend_positive}", "DEBUG", False)

        self.save_local_data()
        return

    # Price check 1 - Is current price above SMA?
    def price_check_sma(self):
        '''
        Checks to see if last close price is above SMA.

        Args:
            None.

        Raises:
            None.

        Returns:
            None. However, the functions sets the is_close_greater_than_sma
            object variable.
        '''
        # Get list of index days.
        price_history_days = []
        for each_day in self.price_history_data:
            price_history_days.append(each_day)
        price_history_days.sort()
        last_day = price_history_days[-1]
        
        # Get last close price.
        last_close_price = self.price_history_data[last_day]['Close']

        # Get last SMA
        last_sma_value = self.sma_data[str(last_day)]

        # Compare last close price to the SMA
        if last_close_price > last_sma_value:
            self.is_close_greater_than_sma = True
        else:
            self.is_close_greater_than_sma = False
        
        log_print(f"INFO: Is last close greater than SMA? {self.is_close_greater_than_sma}",
            "DEBUG", False)
        self.save_local_data()
        return

    # Price check 2 - Is current price above or near SMA + 2 st dev?
    def price_check_stdev(self):
        '''
        Description...

        Args:
            ...

        Raises:
            None.

        Returns:
            ...
        '''
        # Get list of index days.
        price_history_days = []
        for each_day in self.price_history_data:
            price_history_days.append(each_day)
        price_history_days.sort()
        last_day = price_history_days[-1]
        
        # Get last close price.
        last_close_price = self.price_history_data[last_day]['Close']

        # Get last SMA
        last_sma_value = self.sma_data[str(last_day)]

        # Calculate a percent of standard deviation above SMA
        percent_of_2_stdev = 0.66
        last_stdev_value = self.standard_deviation_data[str(last_day)]
        stdev_variation = last_stdev_value * 2 * percent_of_2_stdev
        stdev_threshold_price = last_sma_value + stdev_variation

        # Compare last close price to the SMA
        if last_close_price > stdev_threshold_price:
            self.is_close_nearer_2_stdev = True
        else:
            self.is_close_nearer_2_stdev = False
        
        log_print(f"INFO: Is last close nearing or above 2 standard deviation? {self.is_close_nearer_2_stdev}",
            "DEBUG", False)

        self.save_local_data()
        return
    
    # Determine a Price History Score
    def determine_price_history_score(self):
        '''
        Description...

        Args:
            ...

        Raises:
            None.

        Returns:
            ...
        '''
        # Metrics weightings
        price_history_trend_weighting = 1
        price_check_sma_weighting = 2
        price_check_stdev_weighting = 2
        total_num_of_options = 5

        if self.is_trend_positive == True:
            price_history_trend = 1
        else:
            price_history_trend = 0
        if self.is_close_greater_than_sma == True:
            price_check_sma = 1
        else:
            price_check_sma = 0
        if self.is_close_nearer_2_stdev == True:
            price_check_stdev = 1
        else:
            price_check_stdev = 0

        self.price_history_score = (
            (
                (price_history_trend * price_history_trend_weighting) +
                (price_check_sma * price_check_sma_weighting) +
                (price_check_stdev * price_check_stdev_weighting)
            ) / total_num_of_options
        )

        log_print(f"Price History Score is {self.price_history_score}",
            "DEBUG", False)

        self.save_local_data()
        return

    ###########################################################################
    # SAVE LOCAL DATA & LOAD LOCAL DATA LOGIC
    ###########################################################################
    def save_local_data(self):
        '''
        Saves data to local filesystem under a directory
            data/price_history_by_symbol/[symbol].json. Data saved is from the
            object data:
                data {
                    price_history_data = {}
                    current_price = 0.00
                    sma_data = {}
                    standard_deviation_data = {}
                }
                analysis {
                    close_trend_days = [1, 3, 9]
                    close_trend_data = []
                    close_trend_average = 0.00
                    is_trend_positive = True
                    is_close_greater_than_sma = True
                    is_close_nearer_2_stdev = True
                    price_history_score = 0.00
                }

        Args:
            None.

        Raises:
            None.

        Returns:
            None. Saves data in file named
                data/price_history_by_symbol/[symbol].json.
                The json structure will include two primary segments: data &
                analysis. Each segment will include several elements.

        '''
        save_path = self.config_save_path.strip(f'/{self.symbol}.json')
        # Check if directory exists.
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        # Structure data.
        data = {
            "data": {
                "price_history_data": self.price_history_data,
                "current_price": self.current_price,
                "sma_data": self.sma_data,
                "standard_deviation_data": self.standard_deviation_data
            },
            "analysis": {
                "close_trend_days": self.close_trend_days,
                "close_trend_data": self.close_trend_data,
                "close_trend_average": self.close_trend_average,
                "is_trend_positive": self.is_trend_positive,
                "is_close_greater_than_sma": self.is_close_greater_than_sma,
                "is_close_nearer_2_stdev": self.is_close_nearer_2_stdev,
                "price_history_score": self.price_history_score
            }
        }
        # Save data.
        with open(self.config_save_path, 'w') as outfile:
            json.dump(data, outfile, sort_keys=True,
                      indent=4, separators=(',', ': '))
            log_print("INFO: Price History data saved.", "INFO", False)
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
            self.price_history_data = data['data']['price_history_data']
            self.current_price = data['data']['current_price']
            self.sma_data = data['data']['sma_data']
            self.standard_deviation_data = data['data']['standard_deviation_data']
            self.close_trend_days = data['analysis']['close_trend_days']
            self.close_trend_data = data['analysis']['close_trend_data']
            self.close_trend_average = data['analysis']['close_trend_average']
            self.is_trend_positive = data['analysis']['is_trend_positive']
            self.is_close_greater_than_sma = data['analysis']['is_close_greater_than_sma']
            self.is_close_nearer_2_stdev = data['analysis']['is_close_nearer_2_stdev']
            self.price_history_score = data['analysis']['price_history_score']
            log_print("INFO: Price History data loaded.", "INFO", False)
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

        # Acquire data
        if local_data_arg is not False or web_data_arg is True:
            self.get_price_history_data()
        else:
            self.price_history_data = self.load_local_data()
        
        # Transform and perform calculations on data
        self.get_simple_moving_average_data()
        self.get_standard_deviation_data()

        # Run analytics
        self.check_price_history_trends()
        self.price_check_sma()
        self.price_check_stdev()
        self.determine_price_history_score()

        return


if __name__ == "__main__":
    symbol = "DFS"
    sh = PriceHistory(symbol)
    sh.run(source_web=True)
