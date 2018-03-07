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

        file_list = self._search_regex(
            r'fileList\s*=\s*JSON\.parse\(\'([^\']+)\'\)', webpage, 'file list', fatal=False)
        if file_list is not None:
            try:
                file_list = self._parse_json(file_list, video_id)
            except Exception:
                file_list = None

        file_list_pseudo = self._search_regex(
            r'fileListPseudo\s*=\s*JSON\.parse\(\'([^\']+)\'\)', webpage, 'file list pseudo', fatal=False)
        if file_list_pseudo is not None:
            try:
                file_list_pseudo = self._parse_json(file_list_pseudo, video_id)
            except Exception:
                file_list_pseudo = None

        if file_list_pseudo is not None:
            file_list = file_list_pseudo

        if file_list is None:
            raise ExtractorError('There is no file list json info')

        for i, item in enumerate(file_list[0]):
            label = item.get('label')
            if not label:
                label = str(i)
            else:
                label = label[:-1]

            formats.append(dict(
                protocol='https',
                format_id=label,
                height=int(label),
                vcodec='h264',
                acodec='aac',
                ext='mp4',
                url=item['file']
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
