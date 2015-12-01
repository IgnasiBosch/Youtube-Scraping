#!/usr/bin/env python

import time
import sys
import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from humbledb import Document, Mongo, Embed


class VideoSource(Document):
    config_database = 'VideoScraper'
    config_collection = 'videos'

    title = 'title'
    url = 'url'
    ref = 'ref'
    source = Embed('source_key')

    @staticmethod
    def is_valid(video):
        black_list = ['[Deleted Video]', '[Private Video]']
        return video.title not in black_list


# class Source(Document):
#     config_database = 'VideoScraper'
#     config_collection = 'sources'
#
#     title = 'title'
#     url = 'url'
#     type = 'type'


def init_driver():
    driver = webdriver.Firefox()
    driver.wait = WebDriverWait(driver, 5)

    return driver


def lookup_from_list(driver, url, type):
    driver.get(url)
    while load_more_content():
        pass

    html = driver.page_source
    bs = BeautifulSoup(html, "html.parser")

    items = bs.find_all("a", {"class": "yt-uix-tile-link"})

    with Mongo:
        # source = Source.find_one({Source.url: url})
        #
        # if source is None:
        #     source = Source()
        #     source.title = bs.title.get_text().strip()
        #     source.url = url
        #     source.type = type
        #     Source.insert(source)

        for item in items:
            ref = get_video_ref_from_url(item['href'])
            video = VideoSource.find_one({VideoSource.ref: ref})
            if video is None:
                video = VideoSource()
                video.title = item.get_text().strip()
                video.url = "https://youtube.com" + item['href']
                video.ref = ref
                # video.source = source
                VideoSource.insert(video)

            print(video.title + " - " + video.url)


def lookup_from_playlist(driver, url):
    driver.get(url + "/playlists")
    while load_more_content():
        pass

    html = driver.page_source
    bs = BeautifulSoup(html, "html.parser")

    rows = bs.select("div.yt-lockup-content a.yt-uix-sessionlink.spf-link")

    for row in rows:
        url = "https://youtube.com" + row['href']
        lookup_from_list(driver, url, "playlist")
        # lookup_from_list(driver, url + "/videos?view=0&sort=dd&flow=list&live_view=500", "list")


def load_more_content():
    try:
        button = driver.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "load-more-button")))

        time.sleep(3)
        button.click()

        return True
    except TimeoutException:
        return False


def get_video_ref_from_url(url):
    return urlparse.parse_qs(urlparse.urlsplit(url).query)['v'][0]

if __name__ == "__main__":
    driver = init_driver()
    url = sys.argv[1]
    try:
       lookup_from_playlist(driver, "https://www.youtube.com/user/MIT")
       # lookup_from_list(driver, url + "/videos?view=0&sort=dd&flow=list&live_view=500", "list")
    finally:
       driver.quit()
