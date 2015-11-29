#!/usr/bin/env python

import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup


def init_driver():
    driver = webdriver.Firefox()
    driver.wait = WebDriverWait(driver, 5)

    return driver


def lookup(driver, url):
    driver.get(url + "/videos?view=0&sort=dd&flow=list&live_view=500")
    while load_more_content():
        pass

    html = driver.page_source
    bs = BeautifulSoup(html, "html.parser")

    h3s = bs.find_all("h3", {"class": "yt-lockup-title "})

    for h3 in h3s:
        print(h3.get_text() + " https://youtube.com" + h3.find("a", href=True)['href'])


def load_more_content():
    try:
        button = driver.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "load-more-button")))

        time.sleep(3)
        button.click()

        return True
    except TimeoutException:
        return False


if __name__ == "__main__":
    driver = init_driver()
    url = sys.argv[1]
    try:
        lookup(driver, url)
    finally:
        driver.quit()