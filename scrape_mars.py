from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import time
from splinter import Browser
import re


def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=True)


def scrape_info(url):
    browser = init_browser()

    browser.visit(url)

    time.sleep(1)
    # Scrape without splinter
    # html = requests.get("https://mars.nasa.gov/news/").text
    # soup = bs.BeautifulSoup(html, 'html.parser')

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "lxml")

    browser.quit()
    return soup


def scrape_nasa_news():
    url = "https://mars.nasa.gov/news/"
    soup = scrape_info(url)
    news_title = soup.find("div", class_="content_title").text.strip()
    news_p = soup.find("div", class_="article_teaser_body").text.strip()
    return news_title, news_p


def scrape_nasa_spaceimages():
    browser = init_browser()
    browser.visit("https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars")
    time.sleep(1)
    # Click's the link to produce a larger version of the featured image
    browser.click_link_by_partial_text("FULL IMAGE")
    time.sleep(1)
    soup = bs(browser.html, "lxml")
    # finds the relative path to the image, and converts it to a full image path
    img_url = (
        "https://www.jpl.nasa.gov/spaceimages/"
        + soup.find("img", class_="fancybox-image")["src"].split("/", 2)[-1]
    )
    browser.quit()
    return img_url


def scrape_twitter():
    url = "https://twitter.com/marswxreport?lang=en"
    soup = scrape_info(url)
    # regular expression pattern to pass to soup's find
    pattern = re.compile(r"InSight sol")
    # find text in the html hat contains the starting message for the weather tweet
    last_tweet = soup.find_all(text=pattern)[0].replace("\n", " ")
    return last_tweet


def scrape_table():
    html = requests.get("https://space-facts.com/mars/").content
    # the second table has mars's facts
    df = pd.read_html(html)[1]
    df = df.rename(columns={0: "Property", 1: "Value"})
    return df.to_html(index=False, classes=["table", "table-hover"], border=0)


def scrape_hemisphere():
    html = requests.get("https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    ).content
    soup = bs(html, "lxml")
    items = soup.find_all("div", class_="item")
    urls = ["https://astrogeology.usgs.gov" + item.find('a')['href'] for item in items]
    # urls = ["https://web.archive.org" + item.find("a")["href"] for item in items]
    hemisphere_image_urls = []
    for path in urls:
        soup_hemisphere = bs(requests.get(path).content, "lxml")
        title = soup_hemisphere.find("h2", class_="title").text
        img_url = soup_hemisphere.find("div", class_="downloads").find("a")["href"]
        hemisphere_image_urls.append({"title": title, "img_url": img_url})
    return hemisphere_image_urls


def scrape():
    print("scraping nasa news")
    news_title, news_p = scrape_nasa_news()
    print("scraping space images")
    featured_img_url = scrape_nasa_spaceimages()
    print("scraping twitter")
    last_tweet = scrape_twitter()
    print("scraping facts table")
    facts_df = scrape_table()
    print("scraping mars hemi sphere info")
    hemisphere_img_urls = scrape_hemisphere()
    results = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_img_url": featured_img_url,
        "last_tweet": last_tweet,
        "facts_df": facts_df,
        "hemisphere_img_urls": hemisphere_img_urls,
    }
    return results
