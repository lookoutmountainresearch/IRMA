# IMPORTS

###############################################################################
# OPEN AI CONFIGURATION
###############################################################################
# Account: matt.hess@lookoutmountainresearch.com
ORGANIZATION_KEY = 'org-Y8Ln1gFyZLpSz75Dqppc0bwD'
# Project: Stock Market Sentiment
PROJECT_KEY = 'proj_y79FDnsWgQvsVRYiwwL4KsLt'

'''
from openai import OpenAI

client = OpenAI(
  organization='org-Y8Ln1gFyZLpSz75Dqppc0bwD',
  project='$PROJECT_ID',
)

from openai import OpenAI

client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
'''


class Sentiment():
    """
    
    """
    def __init__(self, symbol):
        """
        
        """
        self.symbol = symbol
        self.xpath_lib = {
            "url": "",
            "elements": {

            }
        }
        self.news_articles = {}
        return

    def get_news_articles(self):
        """
        
        """
        return

    def save_news_articles(self):
        """
        Saves the news articles to a local folder.
        """
        return
    
    def load_news_articles(self):
        """
        
        """
        return

    def determine_sentiment(self):
        """
        
        """
        return

    def correlation_to_spy(self):
        """
        
        """
        return



###############################################################################
# SCRIPT IF RUNNING AS __MAIN__
###############################################################################
if __name__ == "__main__":
    SYMBOL = "MSFT"
    sent = Sentiment(SYMBOL)
