import datetime
import json

import mock

from models.paste import Paste
from simple_tor_crawler import SimpleTorCrawler

DATA_FIXTURES_FOLDER = './data_fixtures'
SOURCE = 'stronghold_paste'


def get_html_data_fixture(file_name):
    with open(f'{DATA_FIXTURES_FOLDER}/{file_name}.html') as f:
        return f.read()


def get_config_data_fixture():
    with open(f'{DATA_FIXTURES_FOLDER}/{SOURCE}.json') as f:
        return json.load(f)


@mock.patch('simple_tor_crawler.SimpleCrawler.get_page_source',
            side_effect=[
                get_html_data_fixture('stronghold_paste_all'),
                get_html_data_fixture('stronghold_paste_paste')
            ])
@mock.patch('simple_tor_crawler.SimpleCrawler.get_source_config',
            return_value=get_config_data_fixture())
def test_get_new_pastes(get_source_config_mock, get_mock):
    expected_result = Paste({'title': 'Codex tasks.xml',
                             'date': datetime.datetime(2018, 1, 23, 0, 2, 58),
                             'content': 'Hourly Cleanup',
                             'author': ''})
    crawler = SimpleTorCrawler()
    crawler.date_cursor = datetime.datetime(2015, 3, 3, 2, 3, 4)
    res = next(crawler.get_new_pastes())
    assert res
    assert res.data
    assert res.data.extra == expected_result.extra


@mock.patch('simple_tor_crawler.SimpleCrawler.get_page_source',
            side_effect=[
                get_html_data_fixture('stronghold_paste_all'),
                get_html_data_fixture('stronghold_paste_paste')
            ])
@mock.patch('simple_tor_crawler.SimpleCrawler.get_source_config',
            return_value=get_config_data_fixture())
def test_get_new_pastes_old_paste(get_source_config_mock, get_mock):
    crawler = SimpleTorCrawler()
    crawler.date_cursor = datetime.datetime(2018, 1, 25, 2, 3, 4)
    res = crawler.get_new_pastes()
    assert len(list(res)) == 0
