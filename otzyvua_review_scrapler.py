from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import time
import math


def init_driver(headless=True, adblock=True):
    """
    A utility function that launches Google Chrome running Selenium. It does 3 things: downloads the driver on first
    launch, installs an ad blocker, and starts the browser in headless mode. Advertising closes the area of clickable
    elements and interferes with scrolling through the page.

    :param headless: If true, runs in headless mode. It is more eficcient, but sometimes scraping fails in headless mode
    :param adblock: If true, installs and uses uBlock origin
    :return: Selenium webdriver
    """
    if headless:
        # TODO: Throw ValueError, when both set to True, because it's impossible to have adblock in non-headless mode
        adblock = False

    driver_installer = ChromeDriverManager(log_level=0, print_first_line=False)
    service = Service(driver_installer.install())
    options = Options()
    options.headless = headless
    if adblock:
        options.add_extension('selenium_supplementary/ublock_1_39_2_0.crx')
    return webdriver.Chrome(service=service, options=options)


def reviews(urls):
    """
    Iterates over the urls of review pages and yields reviews. To do this, launches Selenium via init_driver

    :param urls: List, each item of which is a URL to review, that should be scraped
    :return: Generator, yielding reviews from each URL
    """
    with init_driver() as driver:
        for url in urls:
            driver.get(url)
            try:
                yield driver.find_element(By.CSS_SELECTOR, "div#comments_container span.comment.description").text
            except Exception:
                pass


def review_urls_from_feed():
    """
    Uses scrape_feed method

    :return: Generator of links to review pages from an endless feed of all reviews at otzyvua.net
    """
    return scrape_feed("div#container div.otzyv_box_float a.user-review")


def clinic_urls_from_feed():
    """
    Uses scrape_feed method

    :return: Generator of links to clinic pages from an endless feed of all reviews at otzyvua.net
    """
    return scrape_feed("div#container div.otzyv_box_float h2 a")


def review_urls_from_clinic_page(clinic_url, reviews_per_page=30):
    with init_driver(adblock=False) as driver:
        driver.get(clinic_url)
        n_reviews = int(driver.find_element(
            By.XPATH, '//div[@class="btn-group"][.//span[@class="inav-title"][text()="Відгуки"]]//div/span'
        ).text)
        n_pages = math.ceil(n_reviews / reviews_per_page)

        for page_idx in range(1, n_pages + 1):
            driver.get(clinic_url + f"?page={page_idx}")
            review_elems = driver.find_elements(By.CSS_SELECTOR, ".commentbox h2 a")
            for elem in review_elems:
                yield elem.get_attribute('href')


def scrape_feed(css_selector, n_batches=20, scroll_pause_time=6):
    """
    Launches Chrome using the init_driver, opens the endless feed page and tries
    to load `n_batches more' times, scrolling to the very bottom. After each
    scrolling, wait `scroll_pause_time' seconds.

    Optimal default values for `n_batches' and `scroll_pause_time' are handpicked. If values are decreased, then
    the feed will not be loaded completely, and if increased, the feed will exhaust and code will be running idle
    without loading anything.

    :param css_selector: Valid CSS selector
    :param n_batches: How many scroll events to send
    :param scroll_pause_time: How long to wait before sending next scroll event
    :return: Generator, yielding all texts inside HTML tags with given selector
    """
    with init_driver(headless=False) as driver:
        driver.get("https://www.otzyvua.net/uk/meditsina/kliniki/")

        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(n_batches):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        link_elems = driver.find_elements(By.CSS_SELECTOR, css_selector)
        for elem in link_elems:
            yield elem.get_attribute('href')
