from humbledb import Document, Embed
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import urlparse


class VideoSource(Document):
    config_database = 'VideoScraper'
    config_collection = 'videos'

    title = 'title'
    url = 'url'
    ref = 'ref'
    source = Embed('sources')

    @staticmethod
    def is_valid(video):
        black_list = ['[Deleted Video]', '[Private Video]']
        return video.title not in black_list


def get_videos(url):
    return lookup_from_list(url + "/videos")






def init_driver():
    driver = webdriver.Firefox()
    driver.wait = WebDriverWait(driver, 0)

    return driver




driver = init_driver()


def load_more_content():
    try:
        button = driver.wait.until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "load-more-button")))

        time.sleep(5)
        button.click()

        return True
    except TimeoutException:
        return False


def lookup_from_list(url):
    driver.get(url)
    while load_more_content():
        pass

    html = driver.page_source
    bs = BeautifulSoup(html, "html.parser")

    items = bs.find_all("a", {"class": "yt-uix-tile-link"})

    for item in items:
        ref = get_video_ref_from_url(item['href'])
        video = VideoSource()
        video.title = item.get_text().strip()
        video.url = "https://youtube.com" + item['href']
        video.ref = ref
        yield video


def get_video_ref_from_url(url):
    try:
        return urlparse.parse_qs(urlparse.urlsplit(url).query)['v'][0]
    except KeyError:
        print "ERROR" + url


def lookup_from_playlist(url):
    driver.get(url + "/playlists")
    while load_more_content():
        pass

    html = driver.page_source
    bs = BeautifulSoup(html, "html.parser")

    rows = bs.select("div.yt-lockup-content a.yt-uix-sessionlink.spf-link")

    for row in rows:
        url = "https://youtube.com" + row['href']
        yield lookup_from_list(url, "playlist")
        # lookup_from_list(driver, url + "/videos?view=0&sort=dd&flow=list&live_view=500", "list")

