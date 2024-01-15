
import logging
# from bs4 import BeautifulSoup
import os
import json
# import pyppdf.patch_pyppeteer
from requests_html import HTMLSession
from pprint import pprint
from datetime import datetime

###############################################################################
# ENABLE LOGGING
###############################################################################
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)-8s %(message)s",
    filename="moneypress.log",
    filemode="a"
)
logger = logging.getLogger(__name__)


###############################################################################
# STOCKS CLASS TO GET SUMMARY & PROFILE INFO BY STOCK SYMBOL
###############################################################################
class CompanyProfile():
    '''
    This class gets information about the company behind the stock symbol. This
    will help with reporting and classifying companies from ETFs.

    Arguments:
        symbol (str):

    Example:
        cp = CompanyProfile("GE")
        cp.run()
        print(cp.profile_data["sector"]) # Prints Industrials

    '''

    def __init__(self, symbol):
        self.symbol = symbol
        self.profile_data = {}
        print(self.symbol)
        return

    def scrape_profile_info(self):
        '''
        Function to scrape data from stock summary.

        Args:
            None

        Raises:
            Errors if xpath does not exist.

        Returns:
            Adds data elements to the profile_data attribute
        '''
        session = HTMLSession()
        url = f'https://finance.yahoo.com/quote/{self.symbol}/profile?p={self.symbol}'
        r = session.get(url)
        # r.html.render()

        data_elements = {
            "Stock Type": {
                'xpath': '//*[@id="Col1-0-Profile-Proxy"]/section/div[2]/div[1]/div/div[6]/span[2]'
            },
            "Company": {
                "Description": {
                    'xpath': '//*[@id="Col1-0-Profile-Proxy"]/section/section[2]/p'
                },
                "Sector": {
                    'xpath': '//*[@id="Col1-0-Profile-Proxy"]/section/div[1]/div/div/p[2]/span[2]'
                },
                "Industry": {
                    'xpath': '//*[@id="Col1-0-Profile-Proxy"]/section/div[1]/div/div/p[2]/span[4]'
                },
                "Website": {
                    'xpath': '//*[@id="Col1-0-Profile-Proxy"]/section/div[1]/div/div/p[1]/a[2]'
                }
            },
            "ETF": {
                "Description": {
                    'xpath': '//*[@id="Col2-2-QuoteModule-Proxy"]/div/div/h3/span'
                },
                "Category": {
                    'xpath': '//*[@id="Col1-0-Profile-Proxy"]/section/div[2]/div[1]/div/div[1]/span[2]'
                },
                "Fund Family": {
                    'xpath': '//*[@id="Col1-0-Profile-Proxy"]/section/div[2]/div[1]/div/div[2]/span[2]'
                }
            }
        }

        # Determine if stock symbol is a company or an ETF-Fields are different
        self.profile_data['Symbol'] = self.symbol
        if len(r.html.xpath(data_elements['Stock Type']['xpath'])) == 0:
            stock_type = "Company"
        else:
            stock_type = r.html.xpath(
                data_elements['Stock Type']['xpath'])[0].text

        if stock_type == "Company":
            self.profile_data['Stock Type'] = stock_type
            try:
                self.profile_data['Description'] = r.html.xpath(
                    data_elements['Company']['Description']['xpath'])[0].text
            except Exception as e:
                print(f"Description - {e}")
                self.profile_data['Description'] = ''
            try:
                self.profile_data['Sector'] = r.html.xpath(
                    data_elements['Company']['Sector']['xpath'])[0].text
            except Exception as e:
                print(f"Sector - {e}")
                self.profile_data['Sector'] = ''
            try:
                self.profile_data['Industry'] = r.html.xpath(
                    data_elements['Company']['Industry']['xpath'])[0].text
            except Exception as e:
                print(f"Industry - {e}")
                self.profile_data['Industry'] = ''
            try:
                self.profile_data['Website'] = r.html.xpath(
                    data_elements['Company']['Website']['xpath'])[0].text
            except Exception as e:
                print(f"Website - {e}")
                self.profile_data['Website'] = ''
        else:
            self.profile_data['Stock Type'] = stock_type
            try:
                self.profile_data['Description'] = r.html.xpath(
                    data_elements['ETF']['Description']['xpath'])[0].text
            except Exception as e:
                self.profile_data['Description'] = ""
                print(f"ERROR: {e}")
            self.profile_data['Category'] = r.html.xpath(
                data_elements['ETF']['Category']['xpath'])[0].text
            self.profile_data['Fund Family'] = r.html.xpath(
                data_elements['ETF']['Fund Family']['xpath'])[0].text
        self.save_local_data(self.profile_data)
        return

    def scrape_summary_info(self):
        session = HTMLSession()
        url = f'https://finance.yahoo.com/quote/{self.symbol}?p={self.symbol}'
        r = session.get(url)
        r.html.render

        data_elements = {
            "Company": {
                "Year Range": {
                    'xpath': '//*[@id="quote-summary"]/div[1]/table/tbody/tr[6]/td[2]'
                },
                "Average Volume": {
                    'xpath': '//*[@id="quote-summary"]/div[1]/table/tbody/tr[8]/td[2]'
                },
                "Market Cap": {
                    'xpath': '//*[@id="quote-summary"]/div[2]/table/tbody/tr[1]/td[2]'
                },
                "PE Ratio": {
                    'xpath': '//*[@id="quote-summary"]/div[2]/table/tbody/tr[3]/td[2]'
                },
                "EPS": {
                    'xpath': '//*[@id="quote-summary"]/div[2]/table/tbody/tr[4]/td[2]'
                },
                "Next Earnings Date": {
                    'xpath': '//*[@id="quote-summary"]/div[2]/table/tbody/tr[5]/td[2]'
                },
                "Forward Dividend": {
                    'xpath': '//*[@id="quote-summary"]/div[2]/table/tbody/tr[6]/td[2]'
                },
                "Dividend Ex-Date": {
                    'xpath': '//*[@id="quote-summary"]/div[2]/table/tbody/tr[7]/td[2]'
                }
            },
            "ETF": {
                "Year Range": {
                    'xpath': '//*[@id="quote-summary"]/div[1]/table/tbody/tr[6]/td[2]'
                },
                "Average Volume": {
                    'xpath': '//*[@id="quote-summary"]/div[1]/table/tbody/tr[8]/td[2]'
                },
                "Net Assets": {
                    'xpath': '//*[@id="quote-summary"]/div[2]/table/tbody/tr[1]/td[2]'
                },
                "PE Ratio": {
                    'xpath': '//*[@id="quote-summary"]/div[2]/table/tbody/tr[3]/td[2]'
                },
                "Yield": {
                    'xpath': '//*[@id="quote-summary"]/div[2]/table/tbody/tr[4]/td[2]'
                },
                "Expense Ratio": {
                    'xpath': '//*[@id="quote-summary"]/div[2]/table/tbody/tr[7]/td[2]'
                },
            }
        }
        # Determine if stock symbol is a company or an ETF-Fields are different
        if "Stock Type" in self.profile_data:
            stock_type = self.profile_data["Stock Type"]
        else:
            self.scrape_profile_info()
        # Set profile data based on stock_type
        self.profile_data['Last Updated'] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M")
        self.profile_data['Yahoo Summary URL'] = f"https://finance.yahoo.com/quote/{self.symbol}?p={self.symbol}"
        self.profile_data['Yahoo Chart URL'] = f"https://finance.yahoo.com/quote/{self.symbol}/chart?p={self.symbol}"
        self.profile_data['Yahoo Options URL'] = f"https://finance.yahoo.com/quote/{self.symbol}/options?p={self.symbol}"
        if stock_type == "Company":
            self.profile_data['Year Range'] = r.html.xpath(
                data_elements['Company']['Year Range']['xpath'],
                first=True).text
            self.profile_data['Average Volume'] = r.html.xpath(
                data_elements['Company']['Average Volume']['xpath'],
                first=True).text
            self.profile_data['Market Cap'] = r.html.xpath(
                data_elements['Company']['Market Cap']['xpath'],
                first=True).text
            self.profile_data['PE Ratio'] = r.html.xpath(
                data_elements['Company']['PE Ratio']['xpath'],
                first=True).text
            self.profile_data['EPS'] = r.html.xpath(
                data_elements['Company']['EPS']['xpath'],
                first=True).text
            self.profile_data['Next Earnings Date'] = r.html.xpath(
                data_elements['Company']['Next Earnings Date']['xpath'],
                first=True).text
            self.profile_data['Forward Dividend'] = r.html.xpath(
                data_elements['Company']['Forward Dividend']['xpath'],
                first=True).text
            self.profile_data['Dividend Ex-Date'] = r.html.xpath(
                data_elements['Company']['Dividend Ex-Date']['xpath'],
                first=True).text
        else:
            self.profile_data['Year Range'] = r.html.xpath(
                data_elements['ETF']['Year Range']['xpath'],
                first=True).text
            self.profile_data['Average Volume'] = r.html.xpath(
                data_elements['ETF']['Average Volume']['xpath'],
                first=True).text
            self.profile_data['Net Assets'] = r.html.xpath(
                data_elements['ETF']['Net Assets']['xpath'],
                first=True).text
            self.profile_data['PE Ratio'] = r.html.xpath(
                data_elements['ETF']['PE Ratio']['xpath'],
                first=True).text
            self.profile_data['Yield'] = r.html.xpath(
                data_elements['ETF']['Yield']['xpath'],
                first=True).text
            self.profile_data['Expense Ratio'] = r.html.xpath(
                data_elements['ETF']['Expense Ratio']['xpath'],
                first=True).text
        self.save_local_data(self.profile_data)
        return

    def get_summary_profile_web_info(self):
        # Check if file exists
        if os.path.exists(f'data/by_symbol/{self.symbol}.json'):
            self.load_local_data()
        # Check Last Updated timestamp, greater than 7 days load from scrape
        if 'Last Updated' in self.profile_data:
            timestamp = datetime.strptime(self.profile_data['Last Updated'], "%Y-%m-%d %H:%M")
            today = datetime.now()
            days_delta = today - timestamp
            if days_delta.days > 6:
                self.scrape_profile_info()
                self.scrape_summary_info()
        else:
            self.scrape_profile_info()
            self.scrape_summary_info()
        # Update profile_data with symbol
        return

    ###########################################################################
    # SAVE LOCAL DATA & LOAD LOCAL DATA LOGIC
    ###########################################################################
    def save_local_data(self, data):
        '''
        Saves data to local filesystem under the data directory.

        Args:
            data (dict): Dictionary data to be saved as json in file

        Raises:
            None.

        Returns:
            None. Saves data in file named [symbol].json.
        '''
        # Check if directory exists.
        if not os.path.exists('data/by_symbol/'):
            os.makedirs('data/by_symbol/')
        # Save data.
        with open(f'data/by_symbol/{self.symbol}.json', 'w') as outfile:
            json.dump(
                    data, outfile,
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': '))
            print(f"{self.symbol} profile data saved.")
        return

    def load_local_data(self):
        '''
        Loads profile data from a local file called [symbol].json in a
        directory named data/by_symbol. Returns data in a Python
        dictionary format.

        Args:
            None.

        Raises:
            CRITICAL: Logs critical message if file doesn't exist.

        Returns:
            data (dict): updates data in profile_data attribute the profile
                data in the data/by_symbol/[symbol].json file.
        '''
        local_profile_path = f'data/by_symbol/{self.symbol}.json'
        if os.path.exists(local_profile_path):
            with open(local_profile_path) as json_file:
                data = json.load(json_file)
                logger.debug(data)
                self.profile_data = data
            logger.info(f"{self.symbol} profile data loaded from local data directory.")
            print(f"{self.symbol} profile data loaded from local data directory.")
        else:
            logger.critical(f"{local_profile_path} doesn't exist.")
        return

    ###########################################################################
    # SAVE CLOUD DATA & LOAD CLOUD DATA
    ###########################################################################
    def save_cloud_data(self):
        return

    def load_cloud_data(self):
        return

    ###########################################################################
    # RUN COMMAND
    ###########################################################################
    def run(self, **kwargs):
        '''
        Populates profile information about either a company or ETF. If no
        source is specified, data will be sourced from web.

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
        logger.debug(kwargs)
        web_data_arg = kwargs.get("source_web", False)
        local_data_arg = kwargs.get("source_local", False)

        # If source local, check if file exists, & then check file timestamp
        if local_data_arg is True:
            # load data from local file
            self.load_local_data()
            # check profile timestamp or if profile_data empty, load from web
            if len(self.profile_data) == 0:
                self.get_summary_profile_web_info()
        elif web_data_arg is True:
            # Scrape data from web
            self.get_summary_profile_web_info()
        else:
            # Scrape data from web
            self.get_summary_profile_web_info()
        return


###############################################################################
# SCRIPT IF RUNNING AS __MAIN__
###############################################################################
if __name__ == "__main__":
    symbol = "AMBA"
    stock = CompanyProfile(symbol)
    stock.run(source_local=False)
    pprint(stock.profile_data)
    symbol = "ULTA"
    stock = CompanyProfile(symbol)
    stock.run(source_local=False)
    pprint(stock.profile_data)
    symbol = "TXT"
    stock = CompanyProfile(symbol)
    stock.run(source_local=False)
    pprint(stock.profile_data)
    symbol = "SPY"
    stock = CompanyProfile(symbol)
    stock.run(source_local=False)
    pprint(stock.profile_data)
    symbol = "ARKK"
    stock = CompanyProfile(symbol)
    stock.run(source_local=False)
    pprint(stock.profile_data)
    symbol = "BTF"
    stock = CompanyProfile(symbol)
    stock.run(source_local=False)
    pprint(stock.profile_data)
    
