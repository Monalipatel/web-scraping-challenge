from bs4 import BeautifulSoup
from splinter import Browser
import pandas as pd
import re, time

def scrape():

    # Set Executable Path & Initialize Chrome Browser
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    # NASA Mars News
    # Scrape the NASA Mars News Site and collect the latest News Title and Paragraph Text. Assign the text to variables that you can reference later.
    news_title,news_p = mars_news(browser)
    data = {
        'news_title': news_title,
        'news_p': news_p,
        'featured_image': featured_image(browser),
        'weather': twitter_weather(browser),
        'facts': mars_facts(),
        'hemisphere': hemisphere_image_urls(browser)
    }
    return data 

def mars_news(browser):
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=0.5)

    html = browser.html
    news_soup = BeautifulSoup(html, "html.parser")

    try:
        slide_element = news_soup.select_one("ul.item_list li.slide")
        latest_news_title = slide_element.find("div", class_="content_title").get_text()
        
        news_paragraph = slide_element.find("div", class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None
    
    return latest_news_title, news_paragraph


def featured_image(browser):
    # Visit the NASA JPL (Jet Propulsion Laboratory) Site
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)

    full_image_button = browser.find_by_id("full_image")
    full_image_button.click()

    # Find "More Info" Button and Click It
    browser.is_element_present_by_text("more info", wait_time=1)
    more_info_element = browser.find_link_by_partial_text("more info")
    more_info_element.click()

    # Parse Results HTML with BeautifulSoup
    html = browser.html
    image_soup = BeautifulSoup(html, "html.parser")

    try:
        img_url = image_soup.select_one("figure.lede a img").get("src")
    except AttributeError:
        return None
    
    # Use Base URL to Create Absolute URL
    img_url = f"https://www.jpl.nasa.gov{img_url}"

    return img_url

def twitter_weather(browser):
    #Mars Weather
    
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)
    time.sleep(5)
    html = browser.html
    weather_soup = BeautifulSoup(html, "html.parser")
    # Find a Tweet with the data-name `Mars Weather`
    mars_weather_tweet = weather_soup.find("div",attrs={"class": "tweet", "data-name": "Mars Weather"})
    # Search Within Tweet for <p> Tag Containing Tweet Text
    try:
        mars_weather = mars_weather_tweet.find("p", "tweet-text").get_text()

    except AttributeError:
        pattern = re.compile(r'sol')
        mars_weather = weather_soup.find('span', text=pattern).text

    return mars_weather


#Mars Facts
def mars_facts():

    try:
        df = pd.read_html("https://space-facts.com/mars/")[0]
    except BaseException:
        return None
    df.columns=["Description", "Value"]
    df.set_index("Description", inplace=True)

    return df.to_html(classes="table table-striped")


#Mars Hemispheres
def hemisphere_image_urls(browser):

    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)
    
    hemisphere_image_urls = []

    # Get a List of All the Hemispheres
    links = browser.find_by_css("a.product-item h3")
    for item in range(len(links)):
        hemisphere = {}

    # Find Element on Each Loop to Avoid a Stale Element Exception
        browser.find_by_css("a.product-item h3")[item].click()

        sample_element = browser.find_link_by_text("Sample").first
        hemisphere["img_url"] = sample_element["href"]
        
        # Get Hemisphere Title
        hemisphere["title"] = browser.find_by_css("h2.title").text
        
        # Append Hemisphere Object to List
        hemisphere_image_urls.append(hemisphere)
        
        # Navigate Backwards
        browser.back()
    return hemisphere_image_urls


if __name__ == "__main__":
    print(scrape())
