import functions_framework
import logging
import json
from ss_yahoo_finance import GetGainers

##############################################################################
# IMPORT CUSTOM MODULES
##############################################################################
import ss_yahoo_finance as y

gainers = y.GetGainers()

@functions_framework.http
def get_gainers(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    
        Run local using the following: 
        functions-framework --target=get_gainers
        
        Testing using the following: 
        curl --header "Content-Type: application/json"   --request POST   --data '{"name":"Matt","password":"xyz"}'   http://localhost:8080
    """
    print(request)
    
    # Create instance from class
    gainers = GetGainers()
    # Load data from Yahoo
    gainers.load_from_yahoo()
    # Print data to validate it was loaded correctly
    print(gainers.get_gainers_data())
    # Save the data
    gainers.save_data_local()
    # Get the symbols from data set
    print(gainers.get_symbols())
    
    return gainers.get_symbols()



if __name__ == "__main__":
    pass