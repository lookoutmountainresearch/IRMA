
import logging
from datetime import datetime
import json
import os
from pprint import pprint
from requests_html import HTMLSession
#from google.cloud import storage

session = HTMLSession()

###############################################################################
# ACCOUNT INTEGRATION
###############################################################################
"""
Build page on LMR to remind me how to do this...

https://www.educative.io/answers/how-to-upload-a-file-to-google-cloud-storage-on-python-3

"""

###############################################################################
# ENABLE LOGGING
###############################################################################
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)-8s %(message)s",
    filename="ss_yahoo_finance.log",
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
# CLASSES
###############################################################################

class GetGainers():
    """
    A class to get all Top Gainers from Yahoo Finance website for the day
    that the script is ran.

    Args:
        None.

    Raises:
        None.

    Returns:
        GetGainers instance.
    """
    def __init__(self):
        offset = 0
        self.y_finance_gainers_url = f"https://finance.yahoo.com/gainers/?offset={offset}&count=100"
        self.gainers_data = {}
        self.total_gainers_count = -1
        self.headers = []
        return

    def load_from_yahoo(self):
        webpage_html = session.get(self.y_finance_gainers_url)
        log_print(f"Getting option data from {self.y_finance_gainers_url}", "INFO", False)
        
        # Get table from Gainers page.
        gainers_xpath = '//*[@id="scr-res-table"]/div[1]/table'
        gainers_rows = webpage_html.html.xpath(gainers_xpath, first=True).find('tr')
        
        # Get the table headers to use a keys in the JSON.
        gainers_headers = webpage_html.html.xpath(gainers_xpath, first=True).find('th')
        for column_header in gainers_headers:
            header_text = column_header.text.replace(" (", " ").replace(")", "").replace("%","percent").replace("52 Week","year").replace(" ","_").lower()
            self.headers.append(header_text)
        print(f"Found {len(self.headers)} headers in table and they are {self.headers}.")

        s = 0
        for row in gainers_rows:
            gainers_data_row = row.find('td')
            if len(gainers_data_row) != 0:
                self.gainers_data[gainers_data_row[s].text] = {}
                self.gainers_data[gainers_data_row[s].text][self.headers[s+1]] = gainers_data_row[s+1].text
                self.gainers_data[gainers_data_row[s].text][self.headers[s+2]] = gainers_data_row[s+2].text
                self.gainers_data[gainers_data_row[s].text][self.headers[s+3]] = gainers_data_row[s+3].text
                self.gainers_data[gainers_data_row[s].text][self.headers[s+4]] = gainers_data_row[s+4].text
                self.gainers_data[gainers_data_row[s].text][self.headers[s+5]] = gainers_data_row[s+5].text
                self.gainers_data[gainers_data_row[s].text][self.headers[s+6]] = gainers_data_row[s+6].text
                self.gainers_data[gainers_data_row[s].text][self.headers[s+7]] = gainers_data_row[s+7].text
                self.gainers_data[gainers_data_row[s].text][self.headers[s+8]] = gainers_data_row[s+8].text
        log_print(f"Scrape returned {len(self.gainers_data)} records.", "DEBUG", False)
        self.total_gainers_count = len(self.gainers_data)
        return

    def get_gainers_data(self):
        """
        Returns the gainers data from the class. If data is not present, 
        the method with run load_from_yahoo().

        Args:
            None.

        Raises:
            None.

        Returns:
            Gainers data from Yahoo Finance.
        """
        if self.total_gainers_count < 0:
            self.load_from_yahoo()
        else:
            data = self.gainers_data
        return data
    
    def get_symbols(self):
        """
        Returns...

        Args:
            None.

        Raises:
            None.

        Returns:
            Gainers data...
        """
        if self.total_gainers_count < 0:
            self.load_from_yahoo()
        else:
            symbols = []
            data_dict_keys = self.gainers_data.keys()
            for key in data_dict_keys:
                symbols.append(key)
        return symbols
    
    ##########################################################################
    # FILE HANDLING FUNCTIONS
    ##########################################################################

    def load_data_from_local(self, filename):
        return

    def load_data_from_cloud(self, filename):
        return

    def save_data_local(self):
        # Open a file in write mode
        with open("get-gainers.json", "w") as f:
            # Convert the dictionary to a JSON string
            json_string = json.dumps(self.gainers_data)
            # Write the JSON string to the file
            f.write(json_string)
        # Close the file
        f.close()
        return

    def save_data_to_cloud(self, bucket_name, source_file_path, destination_blob_name, credentials_file):
        # Initialize the Google Cloud Storage client with the credentials
        storage_client = storage.Client.from_service_account_json(credentials_file)
        # Get the target bucket
        bucket = storage_client.bucket(bucket_name)
        # Upload the file to the bucket
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_path)
        print(f"File {source_file_path} uploaded to gs://{bucket_name}/{destination_blob_name}")



###############################################################################
# TEST and VALIDATE CLASS AND FUNCTIONS ARE WORKING.
###############################################################################
if __name__ == "__main__":
    # Create instance from class
    gainers = GetGainers()
    # Load data from Yahoo
    gainers.load_from_yahoo()
    # Print data to validate it was loaded correctly
    pprint(gainers.get_gainers_data())
    # Save the data
    gainers.save_data_local()
    # Get the symbols from data set
    print(gainers.get_symbols())
    # Replace the following variables with your specific values
    '''
    BUCKET_NAME = "your-bucket-name"
    SOURCE_FILE_PATH = "path/to/your/local/file.txt"
    DESTINATION_BLOB_NAME = "uploaded-file.txt"
    CREDENTIALS_FILE = "path/to/your/credentials.json"
    gainers.save_data_to_cloud(BUCKET_NAME, SOURCE_FILE_PATH, DESTINATION_BLOB_NAME, CREDENTIALS_FILE)
    '''  






