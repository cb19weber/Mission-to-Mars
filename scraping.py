#!/usr/bin/env python
# coding: utf-8

# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
# Import Pandas and datetime
import pandas as pd
import datetime as dt

def scrape_all():
    # Initialize Splinter to use Chrome
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)
    news_title, news_paragraph = mars_news(browser)
    hemisphere_image_urls = hemispheres(browser)
    
    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title, 
        "news_paragraph": news_paragraph, 
        "featured_image": featured_image(browser), 
        "facts": mars_facts(), 
        "last_modified": dt.datetime.now(),
        "hemispheres": hemisphere_image_urls
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None
    
    return news_title, news_p

def featured_image(browser):
    # Scrape Mars Images
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None
    
    # Use the base URL to create an absolute URL
    img_url = f'{url}/{img_url_rel}'

    return img_url

def mars_facts():
    # Scrape Mars Facts Table
    try:
        # Use 'read_html' to scrape fact DataFrame and export to html
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)
    
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

def hemispheres(browser):
    # 1. Use browser to visit the URL - had to update link to ensure function performed correctly
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    hemi_soup = soup(html, 'html.parser')
    hemi_raw_html = hemi_soup.find_all('div', class_='item')
    for temp_soup in hemi_raw_html:
        hemispheres = {}
        title = temp_soup.find('h3').get_text()
        browser.find_by_tag('h3').click()
        temp_html = browser.html
        temp_full_soup = soup(temp_html, 'html.parser')
        # hemispheres = browser.links.find_by_text('Sample')
        hemispheres = {'title': title,
                    'img_url': temp_full_soup.find('div', class_='downloads').find('a').get('href')}
        hemisphere_image_urls.append(hemispheres)
        browser.back()

    # 4. Return the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as a script, print scraped data
    print(scrape_all())