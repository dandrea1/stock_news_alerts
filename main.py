import requests
import os
from twilio.rest import Client


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

# Stock API information
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API_KEY = os.environ['STOCK_KEY']
CLOSING_STOCK_PRICES = []

# News API information
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.environ['NEWS_KEY']
NUMBER_ARTICLES = 3
NEWS_ARTICLES = {}

# Twilio API Information
ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_TRIAL_PHONE = "+XXXXXX"


# Get Previous Two Days Stock Closing Prices
def get_closing_prices():
    stock_parameters = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": STOCK,
        "apikey": STOCK_API_KEY,
    }
    stock_response = requests.get(url=STOCK_ENDPOINT, params=stock_parameters)
    stock_response.raise_for_status()
    stock_data = stock_response.json()['Time Series (Daily)']

    last_two_days = {k: stock_data[k] for k in list(stock_data)[:2]}
    for key, value in last_two_days.items():
        CLOSING_STOCK_PRICES.append(float(value['4. close']))


# Call News API to get top 3 news articles title and description for desired Company and save into dictionary
def get_news_articles():
    news_parameters = {
        "q": COMPANY_NAME,
        "from": CLOSING_STOCK_PRICES[0],
        "sortBy": "popularity",
        "pageSize": NUMBER_ARTICLES,
        "apiKey": NEWS_API_KEY
    }
    response = requests.get(url=NEWS_ENDPOINT, params=news_parameters)
    data = response.json()
    for num in range(NUMBER_ARTICLES):
        NEWS_ARTICLES[data["articles"][num]['title']] = data["articles"][num]['description']


# Get the closing prices, and if percent difference is greater than 5%, send text message to user with 3 relevant
# articles for that company.
get_closing_prices()

# Calculate percent difference in closing stock price for previous two days
difference = CLOSING_STOCK_PRICES[1] - CLOSING_STOCK_PRICES[0]
up_down = "None"

if difference > 0:
    up_down = "👆"
else:
    up_down = "👇"


percent_difference = round((difference / CLOSING_STOCK_PRICES[0]) * 100, 2)

if abs(percent_difference) >= 5:

    # Get relevant new articles & format for text message using list comprehension
    get_news_articles()

    articles_titles_to_text = [key for (key, value) in NEWS_ARTICLES.items()]
    articles_descriptions_to_text = [value for (key, value) in NEWS_ARTICLES.items()]

    # Text articles to user
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    for _ in range(len(articles_titles_to_text)):
        message = client.messages \
            .create(
            body=f"{STOCK}: {up_down}{percent_difference}%\nHeadline: {articles_titles_to_text[_]}"
                 f"\nBrief: {articles_descriptions_to_text[_]}",
            from_=TWILIO_TRIAL_PHONE,
            to='+XXXXXXXX'
        )
else:
    print("Stock price change in normal range")
