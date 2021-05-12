
import logging
from requests_html import HTMLSession
session = HTMLSession()
from bs4 import BeautifulSoup
from datetime import datetime
import os

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
# STOCK HISTORY CLASS TO GET A LIST OF STOCK PRICES FOR A SYMBOL
###############################################################################
class StockHistory():
    '''
    
    '''
    def __init__(self, symbol):
        self.symbol = symbol
        self.url = f"https://finance.yahoo.com/quote/{symbol}/history?p={symbol}"
        self.stock_history_data = {}
        self.current_price = -1
        self.sma_20 = 0
        self.sma_40 = 0
        self.sma_60 = 0
        self.sma_80 = 0
        self.average_daily_volume_20 = 0
        return
    
    def convert_date_to_seconds(self, ex_date_str):
        '''
        Provide a valid date and function will convert date to seconds from 
        1/1/1970.
        Requires date as argument.
        '''
        start_date_str = '1970-01-01'
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        ex_date = datetime.strptime(ex_date_str, '%b %d, %Y')
        difference = (ex_date - start_date)
        date_in_seconds = int(difference.total_seconds())
        logger.debug(f'Calcuated seconds between "{start_date_str}" and "{ex_date_str}" to be {date_in_seconds} .')
        return date_in_seconds

    def scrape_stock_history(self):
        '''
        
        '''
        html_session = HTMLSession()
        # Get contents of the page 
        try:
            webpage_results = html_session.get(self.url)

            # Render page results
            #webpage_results.html.render(scrolldown=250)
            
            if webpage_results.status_code == 200:
                logger.info(f"Recieved results from {self.url}")
            else:
                logger.critical(f"Returned status code: {webpage_results.status_code}")
        except Exception as e:
            logger.critical(f"No response from web - {e}")
        return webpage_results

    def get_stock_history_data(self, webpage_html):
        # Find table data headings
        headings_xpath = '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/thead'
        headings_results = webpage_html.html.xpath(headings_xpath, first=True)
        headings_soup = BeautifulSoup(headings_results.html, "lxml")
        headings_html = headings_soup.find_all("th")
        headings = []
        for heading in headings_html:
            headings.append(heading.text.strip("*"))
            # self.stock_history_data[heading.text.strip("*")] = []
        
        # Set table data to variable.
        stock_history_table_xpath = '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody'
        stock_history_table_data = webpage_html.html.xpath(stock_history_table_xpath, first=True)
        stock_history_soup = BeautifulSoup(stock_history_table_data.html, "lxml")
        
        # Find rows in the table
        stock_history_rows = stock_history_soup.find_all("tr")

        # Cycle through each row of the table, validate data, & set to dictionary
        for row in stock_history_rows:
            cells = row.find_all("td")
            if len(cells) == 7:
                self.stock_history_data[self.convert_date_to_seconds(cells[0].text)] = {
                    headings[0]: cells[0].text,
                    headings[1]: float(cells[1].text.replace(",","")),
                    headings[2]: float(cells[2].text.replace(",","")),
                    headings[3]: float(cells[3].text.replace(",","")),
                    headings[4]: float(cells[4].text.replace(",","")),
                    headings[5]: float(cells[5].text.replace(",","")),
                    headings[6]: int(cells[6].text.replace(",",""))
                }
        # Validation
        logger.debug(headings)
        logger.debug(self.stock_history_data)
        # for heading in headings:
            # print(f"Record count for {heading} is {len(self.stock_history_data[heading])}")
        return
    

    ###############################################################################
    # SAVE LOCAL DATA & LOAD LOCAL DATA LOGIC
    ###############################################################################
    def save_local_data(self, data):
        # Check if directory exists.
        if not os.path.exists('data'):
            os.makedirs('data')
        # Save data.
        with open(f'data/{self.symbol}.json', 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))
            print("Earnings Calendar data saved.")
        return
    
    def load_local_data(self):
        with open(f'data/{self.symbol}.json') as json_file:
            data = json.load(json_file)
            self.earnings_calendar_data = data
            print("Earnings Calendar data loaded.")
        return data
    
    def run(self):
        webpage_results = self.scrape_stock_history()
        self.get_stock_history_data(webpage_results)
        return


if __name__ == "__main__":
    symbol = "MSFT"
    sh = StockHistory(symbol)
    sh.run()
    print(sh.stock_history_data)
    print(f"Number of stock history records: {len(sh.stock_history_data)}")
    pass