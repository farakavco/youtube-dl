# coding: utf-8
from __future__ import unicode_literals

from lutino.utils import re

from bs4 import BeautifulSoup
from youtube_dl.extractor.common import InfoExtractor
from youtube_dl.utils import ExtractorError


class AparatIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?aparat\.com/(?:v/|video/video/embed/videohash/)(?P<id>[a-zA-Z0-9]+)'

    _TEST = {
        'url': 'http://www.aparat.com/v/wP8On',
        'md5': '131aca2e14fe7c4dcb3c4877ba300c89',
        'info_dict': {
            'id': 'wP8On',
            'ext': 'mp4',
            'title': 'تیم گلکسی 11 - زومیت',
            'age_limit': 0,
        },
        # 'skip': 'Extremely unreliable',
    }

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage = self._download_webpage(url, video_id)
        html_elements = BeautifulSoup(webpage, 'html.parser')

        formats = []

        video_files = self._search_regex(
            r'options\s*=\s*JSON\.parse\(\'([^\']+)\'\)', webpage, 'video files', fatal=False)
        if video_files is not None:
            try:
                video_files = self._parse_json(video_files, video_id)
            except Exception:
                video_files = None

        if video_files is None:
            self._downloader.params['logger'].error(
                url,
                extra={
                    'web_page_source': webpage,
                })
            raise ExtractorError('There is no file list json info')

        for index, item in enumerate(video_files['plugins']['sabaPlayerPlugin']['multiSRC'][0]):
            label = item.get('label')
            if not label:
                label = str(index)
            else:
                label = label[:-1]

            formats.append(dict(
                protocol='https',
                format_id=label,
                height=int(label),
                vcodec='h264',
                acodec='aac',
                ext='mp4',
                url=item['src']
            ))

        title = html_elements.find('meta', {'property': 'og:title'})['content']
        description = html_elements.find('meta', {'property': 'og:description'})['content']
        thumbnail = html_elements.find('meta', {'property': 'og:image'})['content']
        tag_element = html_elements.find('ul', {'class': 'vone__tags'})
        tags = [t['title'] for t in tag_element.findAll('a', {'class': 'video_one_tag_link'})]
        category_element = html_elements.find('a', {'class': 'vone__cats'})['href']
        category_slug = re.search(r'aparat.com/([\w\-_]+)/?', category_element).group(1)

        return {
            'id': video_id,
            'title': title,
            'description': description,
            'ext': 'mp4',
            'thumbnail': thumbnail,
            'formats': formats,
            'tags': tags,
            'categories': [category_slug],
            'age_limit': self._family_friendly_search(webpage),
        }

    def _family_friendly_search(self, html):
        return 0
