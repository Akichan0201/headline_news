import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://search.kompas.com/search?q=berita+hari+ini"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"}
res = requests.get(url, headers=headers, timeout=10)
html = res.text

html = BeautifulSoup(html, "html.parser")
wrapper = html.find("div", class_="wrap")
articles = wrapper.find_all("div", class_="sectionBox")

news = []
for article in articles:
    links = article.find_all("div", class_="articleItem")
    for i in links:
        link = i.find("a")["href"]
        title = i.find("h2").text
        post = i.find("div", class_="articlePost")
        
        #get the sub-post
        genre = post.find("div", class_="articlePost-subtitle").text
        date = post.find("div", class_="articlePost-date").text

        dict = {
            "Link" : link,
            "Title" : title,
            "Genre" : genre.replace("\n ", ""),
            "Date" : date.replace("\n ", "")
        }

        news.append(dict)

        #normalize whitespace
        for item in news:
            for key in item:
                if isinstance(item[key], str):
                    item[key] = " ".join(item[key].split())
                    

#converting to dataframe
df = pd.DataFrame(news)

# mapping Indo → English month names
month_map = {
    "Januari": "January", "Februari": "February", "Maret": "March",
    "April": "April", "Mei": "May", "Juni": "June",
    "Juli": "July", "Agustus": "August", "September": "September",
    "Oktober": "October", "November": "November", "Desember": "December"
}

# replace Indonesian with English
for indo, eng in month_map.items():
    df["Date"] = df["Date"].str.replace(indo, eng)

# Convert Indonesian month names to datetime
df['Date'] = pd.to_datetime(df['Date'], format='%d %B %Y', dayfirst=True)

# Sort ascending by date
df = df.sort_values(by='Date', ascending=True)

# Reformat date into dd/mm/yy
df['Date'] = df['Date'].dt.strftime('%d/%m/%y')

df.to_excel("Today_News.xlsx", index=False)
print("Data saved to Today_News.xlsx")
