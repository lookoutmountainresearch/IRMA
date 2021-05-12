

# From options.py
"""
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
"""


"""
    def load_options_list_to_firestore(self, data_as_json):
        '''Loads data into Firestore database.
        Data formated as json (ex: SYMBOL: {company name: NAME})
        '''
        options_data = {}
        last_update_date = datetime.utcnow()
        # Formats data in json data with active flag and timestamp
        for symbol in data_as_json:
            options_data[symbol] = {"active": True,
                                    "company name": data_as_json[symbol]['company name'],
                                    "last updated": last_update_date}
        print(options_data)

        # Resets active flag to False in Firestore database

        # Use a service account
        cred = credentials.Certificate('LMR_Research_Portal-ac53fd4f6ff3.json')
        firebase_admin.initialize_app(cred)
        
        db = firestore.client()

        options_master_data = db.collection(u'IRMA').document(u'Master Data').collection(u'Options')
        docs = options_master_data.stream()

        
        options_data_update = {}
        for doc in docs:
            print(f'{doc.id} => {doc.to_dict()}')
            options_data_update['active'] = False
            db_conn = db.collection(u'IRMA').document(u'Master Data').collection(u'Options').document(doc.id)
            db_conn.set(options_data_update, merge=True)
        print(options_data_update)

        # Loads new data into Firestore
        for symbol in options_data:
            options_data_update['active'] = True
            options_data_update['company name'] = options_data[symbol]['company name']
            options_data_update['last updated'] = options_data[symbol]['last updated']
            db_conn = db.collection(u'IRMA').document(u'Master Data').collection(u'Options').document(symbol)
            db_conn.set(options_data_update, merge=True)
        
        # Update totals in Firestore
        total_options_data = {
            'weekly options count': self.total_weekly_options,
            'last updated': last_update_date}
        db_conn = db.collection(u'IRMA').document(u'Master Data')
        db_conn.set(total_options_data, merge=True)
        return
    """

# opt.load_options_list_to_firestore(opt.options_data)
    #opt.save_local_data(opt.options_data)



# From main.py
'''
if __name__ == "__main__":
    with open('config.json') as f:
        config = json.load(f)

    # Get symbol from command argument
    config["Symbol"] = get_symbol()

    # Get Profile info
    config["Profile"]["url"] = config["Profile"]["url"].replace("{symbol}",
        config["Symbol"])
    config["Profile"]["elements"] = get_web_content(config["Profile"]["url"],
        config["Profile"]["elements"])
    
    # Get Summary info
    config["Summary"]["url"] = config["Summary"]["url"].replace("{symbol}",
        config["Symbol"])
    config["Summary"]["elements"] = get_web_content(config["Summary"]["url"],
        config["Summary"]["elements"])

    # Get Price History data to determine the standard deviation
    config["Price History"]["url"] = config["Price History"]["url"].replace("{symbol}",
        config["Symbol"])
    config["Price History"]["elements"] = get_web_content(config["Price History"]["url"],
        config["Price History"]["elements"])

    for items in config["Price History"]["elements"]['table']['value']:
        print(items)

    data_list = config["Price History"]["elements"]['table']['value'].split("\n")
    # print(data_list)

    data = {
        data_list[0]: [],
        data_list[1]: [],
        data_list[2]: [],
        data_list[3]: [],
        data_list[4]: [],
        data_list[5]: [],
        data_list[6]: []
    }
    ''''''
    i = 7
    data_date = []
    data_open = []
    data_high = []
    data_low = []
    data_close = []
    data_adj_close = []
    data_volume = []
    
    while i < len(data_list):
        try:
            data_date.append(data_list[i])
            data_open.append(data_list[i + 1])
            data_high.append(data_list[i + 2])
            data_low.append(data_list[i + 3])
            data_close.append(data_list[i + 4])
            data_adj_close.append(data_list[i + 5])
            data_volume.append(data_list[i + 6])
        except Exception as e:
            print(e)
        i += 7

    data = {
        data_list[0]: [data_date],
        data_list[1]: [data_open],
        data_list[2]: [data_high],
        data_list[3]: [data_low],
        data_list[4]: [data_close],
        data_list[5]: [data_adj_close],
        data_list[6]: [data_volume]
    }
    print(data)
    # df = pd.DataFrame(data)
    # print(df)
    ''''''
    # Get Option Chain data
    config["Option Chain"]["url"] = config["Option Chain"]["url"].replace("{symbol}",
        config["Symbol"])
    config["Option Chain"]["elements"] = get_web_content(config["Option Chain"]["url"],
        config["Option Chain"]["elements"])
    # pprint(config)



    # Analyze Money Press trade
    pass
'''


# From options when updating documentation
    ''' 
    
        run(source_web as boolean OPTIONAL | source_local as boolean OPTIONAL)
        scrape_weekly_options_list()
        save_local_data(data as json)
        load_local_data()
        is_valid_weekly_option(symbol as string)
        validate_weekly_options(symbols as dictionary)
        total_weekly_options
    '''


    # From stock.py

def get_stock_info(self):
    # Get list of symbols

    # Use a service account
    cred = credentials.Certificate('LMR_Research_Portal-ac53fd4f6ff3.json')
    firebase_admin.initialize_app(cred)
    
    db = firestore.client()

    options_master_data = db.collection(u'IRMA').document(u'Master Data').collection(u'Options')
    docs = options_master_data.stream()

    stock_data_update = {}
    for doc in docs:
        print(f'{doc.id} => {doc.to_dict()}')
        meta = doc.to_dict()
        stock_data_update = {doc.id: {}}
        print(stock_data_update)
        print(meta)
        stock_data_update[doc.id] = {"active": True,
                                "company name": meta['company name'],
                                "last updated": meta['last updated']}
        
    print(stock_data_update)

    # Get info from Profile page & determine ETF or company
    '''
    https://finance.yahoo.com/quote/FUTU/profile?p=FUTU
    https://finance.yahoo.com/quote/FUTU?p=FUTU
    https://finance.yahoo.com/quote/FUTU/analysis?p=FUTU
    https://finance.yahoo.com/quote/FUTU/key-statistics?p=FUTU

    https://finance.yahoo.com/quote/SPY/profile?p=SPY --check first to determine ETF
    https://finance.yahoo.com/quote/SPY?p=SPY 
    https://finance.yahoo.com/quote/SPY/analysis?p=SPY --not for ETFs
    https://finance.yahoo.com/quote/SPY/key-statistics?p=SPY --not for ETFs
    '''
    # Get info from Summary page
    # Get info from analysis (companies only)
    # Get info from statistics (companies only)
    
    return
