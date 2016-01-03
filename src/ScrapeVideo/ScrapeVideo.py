from humbledb import Document, Embed
from bs4 import BeautifulSoup
import urlparse
import requests
requests.packages.urllib3.disable_warnings()


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


def lookup_from_list(url):
    link_more_delector = 'button.load-more-button'
    link_more_attribute_selector = 'data-uix-load-more-href'

    res = requests.get(url)
    html = res.text
    bs = BeautifulSoup(html, "html.parser")
    link_more = bs.select_one(link_more_delector)[link_more_attribute_selector]
    domain = get_domain_name(url)
    res = load_more_content(domain + link_more)

    while res['link_more']:
        html = html + res['content']
        res = load_more_content(res['link_more'])
    html = html + res['content']

    bs = BeautifulSoup(html, "html.parser")

    items = bs.find_all("a", {"class": "yt-uix-tile-link"})

    for item in items:
        ref = get_video_ref_from_url(item['href'])
        video = VideoSource()
        video.title = item.get_text().strip()
        video.url = get_domain_name(url) + item['href']
        video.ref = ref
        yield video


def get_video_ref_from_url(url):
    try:
        return urlparse.parse_qs(urlparse.urlsplit(url).query)['v'][0]
    except KeyError:
        print "ERROR" + url


def get_videos(url):
    return lookup_from_list(url + "/videos")


def get_domain_name(url):
    return urlparse.urlunparse(urlparse.urlparse(url)[:2] + ("",) * 4)


def load_more_content(url):
    req = requests.get(url)
    res = req.json()

    if res['load_more_widget_html']:
        bs = BeautifulSoup(res['load_more_widget_html'], "html.parser")
        link_more = get_domain_name(url) + bs.select_one('button.load-more-button')['data-uix-load-more-href']
    else:
        link_more = False

    return {'link_more': link_more, 'content': res['content_html']}
