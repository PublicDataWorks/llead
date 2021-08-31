from datetime import datetime
from dateutil.parser import parse

from django.conf import settings
from django.test import TestCase

from unittest.mock import patch, Mock, MagicMock
from scrapy.http import XmlResponse, Request

from news_articles.constants import TAG_STYLE_MAPPINGS, NEWS_ARTICLE_CLOUD_SPACES
from news_articles.factories import CrawledPostFactory
from news_articles.spiders import ScrapyRssSpider
from officers.factories import OfficerFactory
from utils.constants import FILE_TYPES


class ScrapyRssSpiderTestCase(TestCase):
    @patch('news_articles.spiders.base_scrapy_rss.GoogleCloudService')
    def setUp(self, mock_gcloud_service):
        self.spider = ScrapyRssSpider()

    def test_parse_guid(self):
        self.spider.guid_pre = 'https://thelensnola.org/?p='
        assert self.spider.parse_guid('https://thelensnola.org/?p=566338') == '566338'

    def test_contains_keywork(self):
        assert self.spider.contains_keyword('officer NOPD')
        assert not self.spider.contains_keyword('lorem if sum')

    def test_get_crawled_post_guid(self):
        CrawledPostFactory(source_name='thelens')
        self.spider.name = 'thelens'
        self.spider.guid_limit = 100
        self.spider.get_crawled_post_guid()
        assert self.spider.post_guids

    @patch('scrapy.Request')
    def test_start_request(self, mock_request):
        mock_request_object = Mock()
        mock_request.return_value = mock_request_object
        self.spider.urls = ['http://example.com']
        next(self.spider.start_requests())
        next(self.spider.start_requests())
        mock_request.assert_called_with(url='http://example.com', callback=self.spider.parse_rss)

    @patch('scrapy.Request')
    @patch('news_articles.spiders.ScrapyRssSpider.parse_item')
    def test_parse_rss(self, mock_parse_item, mock_request):
        mock_request_object = Mock()
        mock_request.return_value = mock_request_object
        mock_parse_object = [{
            'title': 'Article Title',
            'description': 'Lorem if sum',
            'link': 'http://example.com',
            'guid': 'GUID-GUID',
            'author': 'Writer',
            'published_date': 'Fri, 20 Aug 2021 19:08:47 +0000',
        }]
        mock_parse_item.return_value = mock_parse_object

        next(self.spider.parse_rss(XmlResponse(
            url='http://example.com',
            request=Request(url='http://example.com'),
            body=str.encode('This is testing content!')
        )))

        date = parse(mock_parse_object[0]['published_date'])

        mock_request.assert_called_with(
            url='http://example.com',
            callback=self.spider.parse_article,
            meta={
                'link': 'http://example.com',
                'guid': 'GUID-GUID',
                'title': 'Article Title',
                'author': 'Writer',
                'published_date': date.date(),
            }
        )

    @patch('news_articles.spiders.base_scrapy_rss.BeautifulSoup')
    def test_parse_section(self, mock_beautiful_soup):
        mock_name = Mock()
        mock_name.name = 'h1'
        mock_current_tag = Mock(return_value=[mock_name])
        mock_get_text = Mock(return_value='Test text')
        mock_beautiful_soup_instance = Mock(
            currentTag=mock_current_tag,
            get_text=mock_get_text
        )
        mock_beautiful_soup.return_value = mock_beautiful_soup_instance

        parsed_section = self.spider.parse_section('<h1></h1>')

        assert parsed_section == {
            'style': TAG_STYLE_MAPPINGS.get('h1'),
            'content': 'Test text'
        }

    @patch('news_articles.spiders.base_scrapy_rss.BeautifulSoup')
    def test_unparse_section(self, mock_beautiful_soup):
        mock_name = Mock()
        mock_name.name = 'aside'
        mock_current_tag = Mock(return_value=[mock_name])
        mock_get_text = Mock(return_value='Test text')
        mock_beautiful_soup_instance = Mock(
            currentTag=mock_current_tag,
            get_text=mock_get_text
        )
        mock_beautiful_soup.return_value = mock_beautiful_soup_instance

        parsed_section = self.spider.parse_section('<aside></aside>')

        assert parsed_section is None

    @patch('news_articles.spiders.base_scrapy_rss.BeautifulSoup')
    def test_parse_invalid_section(self, mock_beautiful_soup):
        mock_name = Mock()
        mock_name.name = 'footer'
        mock_current_tag = Mock(return_value=[mock_name])
        mock_get_text = Mock(return_value='Test text')
        mock_beautiful_soup_instance = Mock(
            currentTag=mock_current_tag,
            get_text=mock_get_text
        )
        mock_beautiful_soup.return_value = mock_beautiful_soup_instance

        parsed_section = self.spider.parse_section('<h1></h1>')

        assert parsed_section == {
            'style': 'BodyText',
            'content': 'Test text'
        }

    def test_parse_paragraphs(self):
        def mock_parse_section_side_effect(paragraph):
            return paragraph
        self.spider.parse_section = MagicMock(side_effect=mock_parse_section_side_effect)

        parsed_paragraphs = self.spider.parse_paragraphs(['paragraph 1', 'paragraph 2', None])

        assert parsed_paragraphs == ['paragraph 1', 'paragraph 2']

    def test_get_officer_data(self):
        officer1a = OfficerFactory(first_name='first_name1', last_name='last_name1')
        officer1b = OfficerFactory(first_name='first_name1', last_name='last_name1')
        officer2 = OfficerFactory(first_name='first_name2', last_name='last_name2')

        officers_data = self.spider.get_officer_data()
        expected_result = {
            'first_name1 last_name1': [officer1a.id, officer1b.id],
            'first_name2 last_name2': [officer2.id]
        }

        assert officers_data == expected_result

    def test_parse_item(self):
        with self.assertRaises(NotImplementedError):
            self.spider.parse_item('response')

    def test_parse_article(self):
        with self.assertRaises(NotImplementedError):
            self.spider.parse_article('response')

    def test_get_upload_pdf_location(self):
        date = datetime.now().date()
        location = self.spider.get_upload_pdf_location(date, 'id')
        file_name = f'{date.strftime("%Y-%m-%d")}_{self.spider.name}_id.pdf'
        assert location == f'{NEWS_ARTICLE_CLOUD_SPACES}/{self.spider.name}/{file_name}'

    def test_upload_file_to_gcloud(self):
        mock_upload_file_from_string = Mock()
        self.spider.gcloud.upload_file_from_string = mock_upload_file_from_string

        result = self.spider.upload_file_to_gcloud('buffer', 'file_location', 'pdf')
        self.spider.gcloud.upload_file_from_string.assert_called_with(
            'file_location',
            'buffer',
            'pdf'
        )
        assert result == f"{settings.GC_PATH}file_location"

    @patch('news_articles.spiders.base_scrapy_rss.logger.error')
    def test_upload_file_to_gcloud_raise_exception(self, mock_logger_error):
        mock_logger_error.return_value = 'error'
        error = ValueError()
        mock_upload_file_from_string = Mock(side_effect=error)
        self.spider.gcloud.upload_file_from_string = mock_upload_file_from_string

        result = self.spider.upload_file_to_gcloud('buffer', 'file_location', 'pdf')
        mock_logger_error.assert_called_with(error)
        assert result is None

    @patch('news_articles.spiders.base_scrapy_rss.generate_from_blob')
    def test_generate_preview_image(self, mock_generate_from_blob):
        mock_generate_from_blob.return_value = 'image_buffer'
        self.spider.upload_file_to_gcloud = Mock(return_value='url')

        result = self.spider.generate_preview_image('pdf_buffer', 'location')

        mock_generate_from_blob.assert_called_with('pdf_buffer')
        self.spider.upload_file_to_gcloud.assert_called_with('image_buffer', 'location', FILE_TYPES['IMG'])
        assert result == 'url'

    @patch('news_articles.spiders.base_scrapy_rss.generate_from_blob')
    def test_not_generating_preview_image(self, mock_generate_from_blob):
        mock_generate_from_blob.return_value = None
        self.spider.upload_file_to_gcloud = Mock(return_value='url')

        self.spider.generate_preview_image('pdf_buffer', 'location')

        mock_generate_from_blob.assert_called_with('pdf_buffer')
        self.spider.upload_file_to_gcloud.assert_not_called()
