from django.test import TestCase
from unittest import mock

from apps.animes.models import Episode
from utils.parsers import ParsedTitle, date_and_videos_of_ep, ep_title_parser


class Test_Title_Parsers(TestCase):
    title = 'Foo Bar - 01 VOSTFR'
    expected: ParsedTitle = {
        'name': title,
        'anime': 'Foo Bar',
        'season': 1,
        'number': 1.0,
        'type': Episode.Type.EPISODE,
        'version': 'VOSTFR'
    }

    def test_title_parser(self):
        result = ep_title_parser(self.title)
        self.assertEqual(result, self.expected)

    def test_title_parser_season(self):
        title = 'Foo Bar 2 - 01 VOSTFR'
        expected: ParsedTitle = {
            **self.expected,
            'name': title,
            'season': 2,
        }

        result = ep_title_parser(title)
        self.assertEqual(result, expected)

    def test_title_parser_film(self):
        title = 'Foo Bar - FILM VOSTFR'
        expected: ParsedTitle = {
            **self.expected,
            'name': title,
            'type': Episode.Type.FILM,
            'number': 0.0
        }

        result = ep_title_parser(title)
        self.assertEqual(result, expected)


class Test_date_and_videos_of_ep(TestCase):

    @mock.patch('utils.parsers.get_page', return_value='')
    def test_date_and_videos_of_ep(self, mocked):
        expected = None, []
        result = date_and_videos_of_ep('')
        self.assertEqual(result, expected)
        mocked.assert_called()
