from humbledb import Document
import urllib
from bs4 import BeautifulSoup
import re


class Source(Document):
    config_database = 'VideoScraper'
    config_collection = 'sources'

    name = 'name'
    url = 'url'
    type = 'type'
    logo = 'logo'
    slug = 'slug'


def build_source(url):
    v = validate_url(url)
    if not v:
        return False

    name_selector = 'a.branded-page-header-title-link'
    logo_selector = 'img.channel-header-profile-image'

    url = v.group(0)
    source = Source()
    source.url = url
    source.type = v.group(1)
    source.slug = v.group(2)

    data = urllib.urlopen(url)
    soup = BeautifulSoup(data, "html.parser")

    name_element = soup.select_one(name_selector)
    source.name = name_element.text
    logo_element = soup.select_one(logo_selector)
    source.logo = logo_element['src']

    return source


def validate_url(url):
    valid_source_url = re.compile(r"https?://(?:www.)?youtube.(?:\w+)/(user|channel)/(\w+)")
    if valid_source_url.match(url):
        return valid_source_url.match(url)
    else:
        return False
