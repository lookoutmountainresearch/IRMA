

import logging
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from datetime import datetime

###############################################################################
# ENABLE LOGGING
###############################################################################
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)-8s %(message)s",
    filename="moneypress_earningscalendar.log",
    filemode="a"
)
logger = logging.getLogger(__name__)


###############################################################################
# CREATE HTML SESSION
###############################################################################
html_session = HTMLSession()


class OptionsChain():
    """
    A class to retrieve and parse option chain data from Yahoo Finance.

    This class scrapes options data for a given stock symbol, including call 
    and put options for available expiration dates, using Yahoo Finance's 
    options page. It also retrieves the current price for the specified symbol.
    """
    def __init__(self, symbol):
        """
        Initializes the OptionsChain object.

        Args:
            symbol (str): The stock symbol (ticker) to retrieve options data for.

        Attributes:
            options_chains (list): List of available expiration dates in seconds.
            url_base (str): Base URL for the options chain.
            url_chain (str): URL template for the options chain with a specific date.
            option_chain_call_data (dict): Dictionary to store call options data.
            option_chain_put_data (dict): Dictionary to store put options data.
            current_price (float): The current price of the stock.
        """
        self.symbol = symbol
        self.options_chains = []
        self.url_base = f"https://finance.yahoo.com/quote/{self.symbol}/options?p={self.symbol}"
        self.url_chain = f"https://finance.yahoo.com/quote/{self.symbol}/options?p={self.symbol}&date=<<date>>"
        self.option_chain_call_data = {}
        self.option_chain_put_data = {}
        self.current_price = -1
    
    def convert_date_to_seconds(self, ex_date_str):
        """
        Converts a given expiration date to seconds from the Unix epoch.

        Args:
            ex_date_str (str): Expiration date in 'Month Day, Year' format.

        Returns:
            int: The number of seconds from 1/1/1970 to the expiration date.

        Logs:
            Logs the computed seconds between the Unix epoch and the expiration date.
        """
        start_date_str = '1970-01-01'
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        ex_date = datetime.strptime(ex_date_str, '%B %d, %Y')
        difference = (ex_date - start_date)
        date_in_seconds = int(difference.total_seconds())
        logger.info(f'Calcuated seconds between "{start_date_str}" and "{ex_date_str}" to be {date_in_seconds} .')
        return date_in_seconds

    def get_option_chain_list(self, webpage_html):
        """
        Extracts a list of available expiration dates from the options page HTML.

        Args:
            webpage_html (HTML): HTML content of the options page.

        Returns:
            None

        Logs:
            Logs whether option chains were successfully retrieved or an error if not.
        """
        option_chain_list_xpath = '//*[@id="Col1-1-OptionContracts-Proxy"]/section/div/div[1]/select'
        try:
            option_chain_list_html = webpage_html.html.xpath(option_chain_list_xpath, first=True)
            option_chain_list_soup = BeautifulSoup(option_chain_list_html.html, "lxml")
            option_chain_list = option_chain_list_soup.find_all("option")
            for option_chain in option_chain_list:
                self.options_chains.append(self.convert_date_to_seconds(option_chain.text))
        except Exception as e:
            logger.error(e)
        # Data validation
        if len(self.options_chains) <= 0:
            logger.error("No option chains were returned.")
        else:
            logger.debug(f"Option Chains has been set to {self.options_chains}.")
        return

    def scrape_option_chain_data(self, **kwargs):
        """
        Fetches HTML data from Yahoo Finance for a given options expiration date.

        Args:
            **kwargs (optional): Optional date argument in seconds from the Unix epoch.

        Returns:
            HTML: HTML content of the options page for the provided or default expiration date.

        Logs:
            Logs the URL used to fetch the data, including whether a specific date was provided.
        """
        # Iterating over the Python kwargs dictionary
        result = ""
        logger.info(kwargs)
        date_value = kwargs.get("date", "null")
        for arg in kwargs:
            result += arg
            # print(f"{result}={date_value}")
            result = ""
        
        if date_value == "null":
            logger.info(f"""Getting option data 
                with base URL: {self.url_base}. 
                No option date was provided. """)
            webpage_results = html_session.get(self.url_base)
        else:
            url_chain = self.url_chain.replace("<<date>>", str(date_value))
            logger.info(f"""Getting option data 
                with chain URL: {url_chain}. 
                Date {date_value} was provided. """)
            webpage_results = html_session.get(url_chain)
        return webpage_results

    def get_current_price(self, webpage_html):
        """
        Retrieves the current stock price from the Yahoo Finance options page HTML.

        Args:
            webpage_html (HTML): HTML content of the options page.

        Returns:
            None

        Logs:
            Logs the current price retrieved or an error if the price could not be found.
        """
        try:
            current_price_xpath = '//*[@id="quote-header-info"]/div[3]/div[1]/div/span[1]'
            self.current_price = webpage_html.html.xpath(current_price_xpath, first=True).text
            logger.debug(f"Current price has been set to {self.current_price}.")
        except Exception as e:
            logger.error(e)
        # Data validation

        return

    def get_option_chain_data(self, webpage_html):
        """
        Extracts and saves the call and put options data from the options page HTML.

        Args:
            webpage_html (HTML): HTML content of the options page.

        Returns:
            None

        Logs:
            Logs the options data headings, tables, and entries, including errors if tables are missing.
        """
        # Get Ex Date for options and convert to seconds from 1/1/1970
        try:
            ex_date_xpath = '//*[@id="Col1-1-OptionContracts-Proxy"]/section/section[1]/div[1]/span[3]'
            ex_date = webpage_html.html.xpath(ex_date_xpath, first=True).text
            ex_date_seconds = self.convert_date_to_seconds(ex_date)
        except Exception as e:
            logger.error(e)
            return
        
        ###############################################################################
        # CALLS
        ###############################################################################
        
        # Find calls table data headings
        calls_headings_xpath = '//*[@id="Col1-1-OptionContracts-Proxy"]/section/section[1]/div[2]/div/table/thead'
        try:
            calls_headings_html = webpage_html.html.xpath(calls_headings_xpath, first=True)
            headings_soup = BeautifulSoup(calls_headings_html.html, "lxml")
            headings = []
            headings_html = headings_soup.find_all("th")
            for heading in headings_html:
                headings.append(heading.text.strip("*"))
            logger.debug(headings)
            calls_table_exist = True
        except Exception as e:
            calls_table_exist = False
            logger.warning(f"Calls table does not exist - {e}")
        
        # Get calls table data
        if calls_table_exist is not False:
            calls_table_xpath = '//*[@id="Col1-1-OptionContracts-Proxy"]/section/section[1]/div[2]/div/table/tbody'
            calls_table_html = webpage_html.html.xpath(calls_table_xpath, first=True)
            calls_table_soup = BeautifulSoup(calls_table_html.html, "lxml")
            data = []
            rows_html = calls_table_soup.find_all("tr")
            for row in rows_html:
                cells_html = row.find_all("td")
                row_data = []
                for cell in cells_html:
                    row_data.append(cell.text)
                data.append(row_data)
                logger.debug(row_data)
            logger.debug(data)
        
        # Save to object
        if calls_table_exist is not False:
            self.option_chain_call_data[ex_date_seconds] = {}
            for entry in data:
                print(entry)
                self.option_chain_call_data[ex_date_seconds][entry[0]] = {}
                self.option_chain_call_data[ex_date_seconds][entry[0]] = {
                    headings[0]: entry[0],
                    headings[1]: entry[1],
                    headings[2]: entry[2],
                    headings[3]: entry[3],
                    headings[4]: entry[4],
                    headings[5]: entry[5],
                    headings[6]: entry[6],
                    headings[7]: entry[7],
                    headings[8]: entry[8],
                    headings[9]: entry[9],
                    headings[10]: entry[10]
                }
        
        ###############################################################################
        # PUTS
        ###############################################################################

        # Find puts table data headings
        puts_headings_xpath = '//*[@id="Col1-1-OptionContracts-Proxy"]/section/section[2]/div[2]/div/table/thead'
        try:
            puts_headings_html = webpage_html.html.xpath(puts_headings_xpath, first=True)
            puts_headings_soup = BeautifulSoup(puts_headings_html.html, "lxml")
            puts_headings = []
            puts_headings_html = puts_headings_soup.find_all("th")
            for heading in puts_headings_html:
                puts_headings.append(heading.text.strip("*"))
            logger.debug(puts_headings)
            puts_table_exist = True
        except Exception as e:
            puts_table_exist = False
            logger.warning(f"Puts table does not exist - {e}")
        
        # Get calls table data
        if puts_table_exist is not False:
            puts_table_xpath = '//*[@id="Col1-1-OptionContracts-Proxy"]/section/section[2]/div[2]/div/table/tbody'
            puts_table_html = webpage_html.html.xpath(puts_table_xpath, first=True)
            puts_table_soup = BeautifulSoup(puts_table_html.html, "lxml")
            data = []
            rows_html = puts_table_soup.find_all("tr")
            for row in rows_html:
                cells_html = row.find_all("td")
                row_data = []
                for cell in cells_html:
                    row_data.append(cell.text)
                data.append(row_data)
                logger.debug(row_data)
            logger.debug(data)
        
        # Save to object
        if puts_table_exist is not False:
            self.option_chain_put_data[ex_date_seconds] = {}
            for entry in data:
                print(entry)
                self.option_chain_put_data[ex_date_seconds][entry[0]] = {}
                self.option_chain_put_data[ex_date_seconds][entry[0]] = {
                    headings[0]: entry[0],
                    headings[1]: entry[1],
                    headings[2]: entry[2],
                    headings[3]: entry[3],
                    headings[4]: entry[4],
                    headings[5]: entry[5],
                    headings[6]: entry[6],
                    headings[7]: entry[7],
                    headings[8]: entry[8],
                    headings[9]: entry[9],
                    headings[10]: entry[10]
                }

        return

    def run(self):
        """
        Main function to initialize scraping and data collection for the specified symbol.

        Retrieves the initial HTML, gets current price and options chains, 
        and then iterates over available expiration dates to collect data for each.

        Returns:
            None
        """
        
        # Initial scrape to set key data & get list of option chains
        webpage_results = self.scrape_option_chain_data()
        self.get_current_price(webpage_results)
        self.get_option_chain_list(webpage_results)
        # Scrape data for each option chain
        self.get_option_chain_data(webpage_results)
        option_chain_seq = 1
        while option_chain_seq < len(self.options_chains):
            print(self.options_chains[option_chain_seq])
            webpage_results = self.scrape_option_chain_data(date=self.options_chains[option_chain_seq])
            self.get_option_chain_data(webpage_results)
            option_chain_seq = option_chain_seq + 1


        return
