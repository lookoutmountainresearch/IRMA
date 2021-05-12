
import logging
from requests_html import HTMLSession
from bs4 import BeautifulSoup
session = HTMLSession()
from datetime import datetime
import json
import os

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
# OPTIONS CLASS TO GET A LIST OF OPTIONABLE STOCK SYMBOLS
###############################################################################
class Options():
    '''
    Options class is for interacting with the options data. This class 
    acquires, formats, saves, & loads the options data.

    Attributes:
        total_weekly_options (int): This is where we store the total number
            of weekly options.
    
    Example:
        opt = Options()
        opt.run()
        print(opt.total_weekly_options)  # Returns the count of weekly options
    '''

    def __init__(self):
        self.options_data = {}
        self.total_weekly_options = 0
        return
    
    def __dir__(self):
        dir = ['run',
            'scrape_weekly_options_list', 
            'save_local_data', 
            'load_local_data', 
            'save_cloud_data', 
            'load_cloud_data', 
            'is_valid_weekly_option',
            'validate_weekly_options']
        return dir


    ###############################################################################
    # SCRAPE & VALIDATE DATA FUNCTION(S)
    ###############################################################################
    def scrape_weekly_options_list(self):
        '''
        Connects to data source and gathers the options list in a json format 
        and stores in the options_data class variable.

        Args:
            None.
        
        Raises:
            None.

        Returns:
            None.
        '''
        cboe_url = 'https://www.cboe.com/us/options/symboldir/weeklys_options/'
        web_content = session.get(cboe_url)
        logger.info(f"Getting option data from {cboe_url}")
        options_rows = web_content.html.find('table', first=True).find('tr')
        self.total_weekly_options = len(options_rows)
        options_data_row_list = []
        options_data_list = {}
        for row in options_rows:
            # options_data_content = BeautifulSoup(row.html, "lxml")
            options_data_row = row.find('td')
            if len(options_data_row) != 0:
                for data in options_data_row:
                    options_data_row_list.append(data.text)
                logger.debug(f"{options_data_row_list} found on the web.")
                options_data_list[options_data_row_list[1]] = {"company name": options_data_row_list[0]}
                options_data_row_list = []
        self.options_data = options_data_list
        logger.info(f"Scrape returned {len(self.options_data)} records.")
        self.total_weekly_options = len(self.options_data)
        
        # Save data to a file
        self.save_local_data(self.options_data)
        return
    

    ###############################################################################
    # SAVE LOCAL DATA & LOAD LOCAL DATA LOGIC
    ###############################################################################
    def save_local_data(self, data):
        '''
        Saves option data in json format to a local file called options.json in a
        directory named data. Provide data in a Python dictionary format. 
        Save_local_data will automatically be performed after 
        scrape_weekly_options_list(). Existing files will be automatically
        overwritten.

        Args:
            data (dict): dictionary to be saved as json.
        Raises:

        Returns:
            None.
        '''
        # Check if directory exists.
        if not os.path.exists('data'):
            os.makedirs('data')
        # Save data.
        with open('data/options.json', 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))
            logger.info("Options data saved to local data directory.")
        return
    
    def load_local_data(self):
        '''
        Loads option data from a local file called options.json in a
        directory named data. Returns data in a Python dictionary format.

        Args:
            None.

        Raises:
            CRITICAL: Logs critical message if file doesn't exist.

        Returns:
            data (dict): returns the option data in the data/options.json file.
        '''
        data_file_path = 'data/options.json'
        data = {}
        if os.path.exists(data_file_path):
            with open(data_file_path) as json_file:
                data = json.load(json_file)
                logger.debug(data)
                self.options_data = data
                self.total_weekly_options = len(self.options_data)
                logger.info("Options data loaded from local data directory.")
        else:
            logger.critical(f"{data_file_path} doesn't exist.")
        return data

    
    ###############################################################################
    # SAVE CLOUD DATA & LOAD CLOUD DATA
    ###############################################################################
    def save_cloud_data(self):
        '''
        #TODO: Add feature to save data to cloud storage

        Saves option data in json format to a file in cloud storage called
        options.json in a directory named data. Provide data in a Python
        dictionary format. Save_cloud_data will automatically be performed after 
        scrape_weekly_options_list(). Existing files will be automatically
        overwritten.

        Args:
            data (dict): dictionary to be saved as json.
        Raises:

        Returns:
            None.
        '''

        return
    
    def load_cloud_data(self):
        '''
        #TODO: Add feature to load data from cloud storage

        Loads option data from file in cloud storage called options.json.
        Returns data in a Python dictionary format.

        Args:
            None.

        Raises:
            CRITICAL: Logs critical message if file doesn't exist.
            
        Returns:
            data (dict): returns the option data in the data/options.json file.
        '''
        
        return


    ###############################################################################
    # SERVICE FUNCTIONS
    ###############################################################################
    def is_valid_weekly_option(self, symbol):
        '''
        Service to validate if a stock has weekly options given the symbol.

        Args:
            symbol (str): Stock symbol.

        Raises:
            None.

        Returns:
            valid_weekly_options: True or False
        '''
        # If total_weekly_options, less than or equal to 0 try to load local
        if len(self.options_data) == 0 and os.path.exists('data/options.json'):
            self.load_local_data()

        # Check if symbol exists, return True or False
        valid_weekly_options = False
        # Check if symbol is in options_data list
        valid_weekly_options = symbol in self.options_data
        return valid_weekly_options
    
    def validate_weekly_options(self, symbols_dictionary):
        '''
        Service to validate a list of stocks that have weekly options.

        Args:
            symbol (dict): Stock symbol list in the follow format:
                {
                "AA": {
                    "company name": "ALCOA CORP COM",
                ...
                }

        Raises:
            None.

        Returns:
            valid_weekly_options_dictionary: Dictionary of valid weekly
                options.
        '''
        valid_weekly_options_dictionary = {}
        for symbol in symbols_dictionary:
            # Use is_valid_weekly_option to check symbol.
            valid_symbol_check = self.is_valid_weekly_option(symbol)
            # If valid, add to new dictionary.
            if valid_symbol_check is True:
                valid_weekly_options_dictionary[symbol] = symbols_dictionary[symbol]
        return valid_weekly_options_dictionary


    ###########################################################################
    # RUN COMMAND
    ###########################################################################
    def run(self, **kwargs):
        '''
        Populates the weekly options list. If no source is specified, data 
        will be sourced from web.
        
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

        # Use argument to determine source of data
        if web_data_arg is True:
            self.scrape_weekly_options_list()
        elif local_data_arg is True:
            # Check if local file exists
            if os.path.exists('data/options.json'):
                # Load options data
                self.options_data = self.load_local_data()
            else:
                # No local source file exists, scrape data from the web
                logger.warning("File data/options.json does not exist, sourcing from web.")
                self.scrape_weekly_options_list()
        else:
            # If no source is specified, scrape data from the web
            self.scrape_weekly_options_list()
        return


###############################################################################
# SCRIPT IF RUNNING AS __MAIN__
###############################################################################
if __name__ == "__main__":
    opt = Options()
    print("Getting options data...")
    logger.info("Getting options data...")
    opt.run(source_local=False)
    
    print(f"Check for total number of records retuned: {opt.total_weekly_options}")
    
    symbol = "MSFT"
    print(f"Check if symbol {symbol} exists: {opt.is_valid_weekly_option(symbol)}")
    print("Options data process complete.")
    logger.info("Options data process complete.")