from src.ScrapeSource import ScrapeSource
from src.ScrapeVideo import ScrapeVideo
from humbledb import Mongo


url = 'https://www.youtube.com/user/PyDataTV'
Source = ScrapeSource.Source
Video = ScrapeVideo.VideoSource
source = ScrapeSource.build_source(url)
# source = ScrapeSource.build_source('https://www.youtube.com/channel/UC3EDu_qaY65TCo1UgcdY7Qg')

with Mongo:
    _source = Source.find_one({Source.type: source.type, Source.slug: source.slug})
    if _source is not None:
        _source.name = source.name
        _source.url = source.url
        _source.logo = source.logo
        source = _source

    Source.save(source)

    for video in ScrapeVideo.get_videos(source.url):
        _video = Video.find_one({Video.ref: video.ref})
        if _video is not None:
            _video.title = video.title
            _video.url = video.url
            video = _video

        video.source = source
        Video.save(video)
        print(video)



