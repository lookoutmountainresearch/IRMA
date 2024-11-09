import logging
from requests_html import HTMLSession
session = HTMLSession()
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime

###############################################################################
# ENABLE LOGGING
###############################################################################
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)-8s %(message)s",
    filename="moneypress.log",
    filemode="a"
)
logger = logging.getLogger(__name__)


###############################################################################
# OPTIONS CLASS TO GET A LIST OF OPTIONABLE STOCK SYMBOLS
###############################################################################
class EarningsCalendar():
    """
    Retrieves earnings data for a specified number of days in the past, 
    starting from the current date. This can be configured using the 
    `config_earnings_days_in_past` attribute, which is set to 15 days by default.

    Attributes:
        config_earnings_days_in_past (int): Number of days in the past to retrieve earnings data.
        earnings_calendar_data (dict): Stores earnings data for various companies.
        total_records (int): Total number of records in `earnings_calendar_data`.

    Example:
        ec = EarningsCalendar()
        ec.run()
    """
    def __init__(self):
        """Initializes EarningsCalendar with default settings for 
        retrieving earnings data."""
        # CONFIGURATION
        self.config_earnings_days_in_past = 15
        # DATA
        self.earnings_calendar_data = {}
        # ANALYSIS METRICS
        self.total_records = len(self.earnings_calendar_data)
        return

    ###############################################################################
    # SCRAPE & VALIDATE DATA FUNCTION(S)
    ###############################################################################

    def convert_to_float(self, value):
        """
        Converts a string representation of a number to a float, handling 
        cases where the string may start with a '+' or '-' symbol.

        Args:
            value (str): The string value to convert to float.

        Returns:
            float: The converted float value.

        Example:
            >>> convert_to_float("+74.75")
            74.75
        """
        if value == "-":
            converted_value = value
        elif value[0] == "+":
            converted_value = float(value.replace("+",""))
        elif value[0] == "-":
            converted_value = 0 - float(value.replace("-",""))
        else:
            converted_value = float(value)
        return converted_value

    def calc_days_since_earnings(self, earnings_date):
        """
        Calculates the number of days since a given earnings date.

        Args:
            earnings_date (str): The date of earnings in 'YYYY-MM-DD' format.

        Returns:
            int: The number of days since the given `earnings_date`.
        """
        first_date = datetime.strptime(earnings_date, '%Y-%m-%d')
        last_date = datetime.today()
        delta = last_date - first_date
        return delta.days
        
    def calc_earnings_score(self, earnings_surprise, earnings_date):
        """
        Calculates a score based on the earnings surprise value and 
        the number of days since the earnings date.

        Args:
            earnings_surprise (float): The earnings surprise percentage.
            earnings_date (str): The date of earnings in 'YYYY-MM-DD' format.

        Returns:
            float: The computed earnings score.
        """
        if earnings_surprise == '-':
            earnings_surprise_score = 0.0
        elif earnings_surprise >= 10.0 and earnings_surprise < 20.0:
            earnings_surprise_score = 75.0
        elif earnings_surprise >= 20.0:
            earnings_surprise_score = 100.0
        else:
            earnings_surprise_score = 0.0
        
        num_of_days = self.calc_days_since_earnings(earnings_date)
        
        if num_of_days < 5.0:
            earnings_date_score = 100.0
        elif num_of_days > 5.0 and num_of_days <= 10.0:
            earnings_date_score = 75.0
        else:
            earnings_date_score = 50.0
        
        earnings_score = (
            earnings_surprise_score +
            earnings_date_score
        ) / 2.0

        return earnings_score

    def scrape_earnings_calendar_stocks(self, earnings_date):
        """
        Retrieves earnings data for all companies on a specific date 
        from Yahoo Finance, handling multiple pages if necessary.

        Args:
            earnings_date (str): The date for which to retrieve earnings data.

        Returns:
            None
        """
        offset = 0
        url = f'https://finance.yahoo.com/calendar/earnings?day={earnings_date}&offset={offset}&size=100'
        
        #"https://finance.yahoo.com/calendar/earnings?from=2024-11-03&to=2024-11-09&day=2024-11-07"
        #"https://finance.yahoo.com/calendar/earnings?from=2024-11-03&to=2024-11-09&day=2024-11-07&offset=100&size=100"
        
        webresults = session.get(url, timeout=2.0)
        # webresults.html.render()

        # Check if there are any earnings listed.
        no_earnings_xpath = '//*[@id="fin-cal-table"]/div[2]/div'
        no_earnings_results = webresults.html.xpath(no_earnings_xpath, first=True)
        try:
            if no_earnings_results.text == "We couldn't find any results.":
                earnings_exist = False
            else:
                earnings_exist = True
        except Exception as e:
            logger.critical(e)
            earnings_exist = False

        # Get table headings as keys in dictionary
        if earnings_exist is True:
            headings_xpath = '//*[@id="cal-res-table"]/div[1]/table/thead/tr'
            headings_results = webresults.html.xpath(headings_xpath, first=True)
            headings_soup = BeautifulSoup(headings_results.html, "lxml")
            headings_cells = headings_soup.find_all('th')
            headings = []
            for heading in headings_cells:
                headings.append(heading.text)
            headings.append('Earnings Date')

        # Pagation logic to determine the numbers of cycles
        if earnings_exist is True:
            number_of_records_xpath = '//*[@id="fin-cal-table"]/h3/span[2]/span'
            number_of_records_results = webresults.html.xpath(number_of_records_xpath, first=True)
            number_of_records = number_of_records_results.text.split(" ")[2]
            number_of_cycles = int(int(number_of_records)/100) + 1
            print(f"NUMBER OF RECORDS: {number_of_records}")
            print(f"NUMBER OF CYCLES: {number_of_cycles}")

        # Loop through pages & table data.
        if earnings_exist is True:
            cycle = 1
            while cycle <= number_of_cycles:
                if offset != 0:
                    url = f'https://finance.yahoo.com/calendar/earnings?from=2021-05-02&to=2021-05-08&day={earnings_date}&offset={offset}&size=100'
                    webresults = session.get(url)
                xpath = '//*[@id="cal-res-table"]/div[1]/table/tbody'
                try:
                    table_html = webresults.html.xpath(xpath, first=True)
                    table_soup = BeautifulSoup(table_html.html, "lxml")
                except Exception as e:
                    logging.critical(e)
                table_rows = table_soup.find_all("tr")
                for row in table_rows:
                    cells = row.find_all('td')
                    # Data validation before updating class data to ensure valid data isn't overwritten 
                    if cells[0].text in self.earnings_calendar_data:
                        logging.warning(f"{cells[0].text} exists, {self.earnings_calendar_data[cells[0].text]} data overwritten {cells[1].text} {cells[2].text} {cells[3].text} {cells[4].text} {cells[5].text}")
                    # If so, maintain duplicates counter for count validation
                    self.earnings_calendar_data[cells[0].text] = {
                        headings[1]: cells[1].text,
                        headings[2]: cells[2].text,
                        headings[3]: cells[3].text,
                        headings[4]: self.convert_to_float(cells[4].text),
                        headings[5]: self.convert_to_float(cells[5].text),
                        headings[6]: self.convert_to_float(cells[6].text),
                        headings[7]: earnings_date,
                        "days_since_earnings": self.calc_days_since_earnings(earnings_date),
                        "earnings_score": self.calc_earnings_score(
                            self.convert_to_float(cells[5].text),
                            earnings_date)
                    }
                cycle += 1
                offset += 100
        return

    def get_list_of_days(self, number_of_days):
        """
        Generates a list of dates starting from today, extending back by 
        the specified number of days.

        Args:
            number_of_days (int): The number of past days to include in the list.

        Returns:
            list of str: A list of date strings in 'YYYY-MM-DD' format.
        """
        import datetime
        list_of_days = []
        start_day = datetime.datetime.now()
        list_of_days.append(start_day.strftime("%Y-%m-%d"))
        i = 1
        while i != number_of_days:
            calc_hours = i * 24
            day_for_list = start_day - datetime.timedelta(hours=calc_hours)
            list_of_days.append(day_for_list.strftime("%Y-%m-%d"))
            i += 1
        print(list_of_days)
        return list_of_days

    def get_earnings_calendar_stocks(self):
        """
        Retrieves earnings data for a range of dates based on the 
        `config_earnings_days_in_past` setting. Data is saved in the 
        `earnings_calendar_data` attribute.

        Returns:
            None
        """
        date_list = self.get_list_of_days(self.config_earnings_days_in_past)
        for d in date_list:
            print(d)
            self.scrape_earnings_calendar_stocks(d)

        # Auto-save web data to local file
        self.save_local_data(self.earnings_calendar_data)
        return

    ###############################################################################
    # SAVE LOCAL DATA & LOAD LOCAL DATA LOGIC
    ###############################################################################

    def save_local_data(self, data):
        """
        Saves the earnings data as a JSON file named 'earnings_calendar.json' 
        in the 'data' directory. Existing files are overwritten.

        Args:
            data (dict): The earnings data to save.

        Returns:
            None
        """
        # Check if directory exists.
        if not os.path.exists('data'):
            os.makedirs('data')
        # Save data.
        with open('data/earnings_calendar.json', 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))
            print("Earnings Calendar data saved.")
        return

    def load_local_data(self):
        """
        Loads earnings data from a local JSON file named 
        'earnings_calendar.json' in the 'data' directory.

        Returns:
            dict: The loaded earnings data.
        """
        
        with open('data/earnings_calendar.json') as json_file:
            data = json.load(json_file)
            self.earnings_calendar_data = data
            print("Earnings Calendar data loaded.")
        return data

    ###############################################################################
    # SAVE CLOUD DATA & LOAD CLOUD DATA
    ###############################################################################

    def save_cloud_data(self):
        '''
        #TODO: Add feature to save data to cloud storage

        Saves earnings calendar data in json format to a file in cloud storage
        called earnings_calendar.json in a directory named data. Provide data in a
        Python dictionary format. Save_cloud_data will automatically be performed
        after get_earnings_calendar_stocks(). Existing files will be automatically
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

        Loads earnings calendar data from file in cloud storage called
        earnings_calendar.json. Returns data in a Python dictionary format.

        Args:
            None.

        Raises:
            CRITICAL: Logs critical message if file doesn't exist.
            
        Returns:
            data (dict): returns the option data in the
                data/earnings_calendar.json file.
        '''
        
        return


    ###########################################################################
    # RUN COMMAND
    ###########################################################################

    def run(self, **kwargs):
        """
        Populates earnings data by fetching it from either a web source or 
        a local file, based on the provided keyword arguments.

        Args:
            **kwargs: Optional arguments:
                - source_web (bool): Set to True to fetch data from the web.
                - source_local (bool): Set to True to load data from a local file.

        Returns:
            None
        
        Upcoming Features:
            #TODO: Query data to determine number of surprises.
            #TODO: Create list sorted from largest to smallest surprises.
            #TODO: Create history of earnings for a given symbol.
        """
        # Set Python kwargs to variable
        logger.debug(kwargs)
        web_data_arg = kwargs.get("source_web", False)
        local_data_arg = kwargs.get("source_local", False)

        # Use argument to determine source of data
        if web_data_arg is True:
            self.get_earnings_calendar_stocks()
        elif local_data_arg is True:
            # Check if local file exists
            if os.path.exists('data/earnings_calendar.json'):
                # Load options data
                self.earnings_calendar_data = self.load_local_data()
            else:
                # No local source file exists, scrape data from the web
                logger.warning("File data/options.json does not exist, sourcing from web.")
                self.get_earnings_calendar_stocks()
        else:
            # If no source is specified, scrape data from the web
            self.get_earnings_calendar_stocks()
        return


if __name__ == "__main__":
    ec = EarningsCalendar()
    # ec.config_earnings_days_in_past = 2 # Test override of default.
    
    ec.run()
    #ec.scrape_earnings_calendar_stocks('2021-05-03')
    
    print(ec.earnings_calendar_data)
    #ec.load_local_data()
    print(len(ec.earnings_calendar_data))
    #ec.save_local_data(ec.earnings_calendar_data)
    print(ec.earnings_calendar_data["AMBA"])
    