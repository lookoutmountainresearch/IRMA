##############################################################################
#    IMPORTS
##############################################################################
import os
import sys
import json
import pandas as pd
from datetime import datetime

print(sys.argv)

# Check for filename in command line.
if len(sys.argv) < 2:
    exit()

# Check if the file exists.
current_path = os.getcwd()
print(current_path)
file_exist = os.path.exists(f"{current_path}/{sys.argv[1]}") 
print(file_exist)

today = datetime.now().strftime("%Y-%m-%d")
print(today)

# Read file into dictionary
suggestions_data = []
if file_exist:
    with open(sys.argv[1]) as f:
        data = json.load(f)
symbols_list = data.keys()
for symbol in symbols_list:
    symbol_data = []
    # Company Info
    print(symbol)
    print(data[symbol]["Company"])
    company = data[symbol]["Company"]
    print(data[symbol]["profile_data"]["Industry"])
    industry = data[symbol]["profile_data"]["Industry"]
    # Analysis Data
    print(data[symbol]["Earnings Date"])
    earnings_date = data[symbol]["Earnings Date"]
    print(data[symbol]["Reported EPS"])
    reported_eps = data[symbol]["Reported EPS"]
    print(data[symbol]["EPS Estimate"])
    eps_estimate = data[symbol]["EPS Estimate"]
    print(data[symbol]["price_history_score"])
    price_history_score = data[symbol]["price_history_score"]
    print(data[symbol]["Surprise(%)"])
    earnings_surprise = data[symbol]["Surprise(%)"]
    # Links
    print(data[symbol]["profile_data"]["Yahoo Chart URL"])
    yahoo_chart_url = data[symbol]["profile_data"]["Yahoo Chart URL"]
    print(data[symbol]["profile_data"]["Yahoo Options URL"])
    yahoo_options_url = data[symbol]["profile_data"]["Yahoo Options URL"]
    print(data[symbol]["profile_data"]["Yahoo Summary URL"])
    yahoo_summary_url = data[symbol]["profile_data"]["Yahoo Summary URL"]
    symbol_data = [
        symbol,
        company,
        industry,
        earnings_date,
        reported_eps,
        eps_estimate,
        price_history_score,
        earnings_surprise,
        yahoo_chart_url,
        yahoo_options_url,
        yahoo_summary_url,
        today
    ]
    suggestions_data.append(symbol_data)    

# Create the pandas DataFrame
df = pd.DataFrame(suggestions_data, columns = ['Symbol', 
                                               'Company',
                                               'Industry',
                                               'Earnings Date',
                                               'Reported EPS',
                                               'EPS Estimate',
                                               'Price History Score',
                                               'Earnings Surprise',
                                               'Yahoo Chart URL',
                                               'Yahoo Options URL',
                                               'Yahoo Summary URL',
                                               'Date Stamp'])
#df = pd.DataFrame(data, columns = ['Name', 'Age'])

# print the data.  
print(df)

df.to_csv(sys.argv[1].replace("json", "csv"))


