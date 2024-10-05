import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# URL of the news page
url = "https://newsroom.calgary.ca/?h=1&t=Police"

month_mapping = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

# Send a GET request to the URL
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract all news articles
articles = soup.find_all('a', class_='td_headlines')  # Check the correct class in the HTML

# Filter articles from the last month
one_month_ago = datetime.now() - timedelta(days=30)
for article in articles:

    months = soup.find_all('div', class_="pp_date_month")

    for month in months:
        if month.getText() in month_mapping:
            release_month = month_mapping[month.getText()]

            if ((datetime.now().month - 2) % 12 or 12 ) <= release_month <= datetime.now().month:

                article_url = article['href']
                response = requests.get(article_url)
                news_soup = BeautifulSoup(response.content, 'html.parser')

                print(article_url)

                article_body = soup.find_all('div', class_="pp-overflow-hidden pp-min-width-5")  # Check the correct class in the HTML

                print(article_body)






    title = article.text.strip()
    date_text = article.find_next('meta', {'name': 'date'})  # Find the date text (check HTML for correct tag)

    print(date_text)

    article_date = datetime.strptime(date_text, '%B %d, %Y')  # Modify format as per the date on site

    # Print article details if it was published in the last month
    if article_date >= one_month_ago:
        link = article.find('a')['href']
        print(f"Title: {title}")
        print(f"Date: {article_date.strftime('%Y-%m-%d')}")
        print(f"Link: {link}")
        print("------")
