import datetime
import json
import time

import requests
import six
from apscheduler.schedulers.background import BackgroundScheduler
from lxml import html

from dal.tinydbdal import TinyDBDal
from models.paste import Paste

DEFAULT_DATE_CURSOR = datetime.datetime.utcnow() - datetime.timedelta(days=14)

SOURCE = 'stronghold_paste'
CONFIGS_FOLDER = './configs'
CONFIG_PATH = f'{CONFIGS_FOLDER}/{SOURCE}.json'

PROXIES = {
    'http': 'http://localhost:8118',
    'https': 'http://localhost:8118'
}

JOB_INTERVAL_HOURS = 4


class SimpleTorCrawler:
    def __init__(self):
        self.dal = TinyDBDal()
        self.config = self.get_source_config()
        self.config_item = self.config and self.config.get('item')
        self.config_paging_url = self.config \
            and self.config.get('paging') \
            and self.config.get('paging').get('url')
        self.date_format = self.config_item \
            and self.config_item.pop('date_format')
        self.date_cursor = self._get_date_cursor()
        self.splitter = self.config_item and self.config_item.pop('splitter')
        self.paste_url_selector = self.config_item \
            and self.config_item.pop('paste_url')
        self.date_selector = self.config_item and self.config_item.pop('date')

    @staticmethod
    def get_page_source(url):
        return requests.get(url, proxies=PROXIES).content

    def _get_date_cursor(self):
        last_crawl_date = self.dal.get_last_crawl_date()
        return last_crawl_date or DEFAULT_DATE_CURSOR

    def _format_date(self, date):
        if not date:
            return datetime.datetime.utcnow()

        return datetime.datetime.strptime(date, self.date_format)

    def _is_new_paste(self, date):
        return date > self.date_cursor

    def _store_paste(self, obj):
        self.dal.insert_new_paste(obj.data.extra)

    def _finish_crawl(self):
        self.dal.update_last_crawl_date(datetime.datetime.utcnow())

    def get_source_config(self):
        return json.load(open(CONFIG_PATH))

    def get_new_pastes(self):
        paging = True
        page_url = self.config['url']

        while True:
            page = self.get_page_source(page_url)
            tree = html.fromstring(page)
            items = tree.xpath(self.splitter)
            page_url = self.config_paging_url \
                and tree.xpath(self.config_paging_url)
            # handle pastes from current page
            for item in items:
                paste_date = self._format_date(
                    item.xpath(self.date_selector).strip())
                if self._is_new_paste(paste_date):
                    paste_url = item.xpath(self.paste_url_selector)
                    if not paste_url:
                        continue
                    page = self.get_page_source(paste_url and paste_url[0])
                    tree = html.fromstring(page)
                    raw_paste = \
                        {param: ''.join(tree.xpath(
                            self.config_item[param])).strip()
                         for param in self.config_item}
                    raw_paste['date'] = str(paste_date)
                    paste = Paste()
                    yield paste.load(raw_paste)
                else:
                    paging = False
                    break

            if not paging or not page_url:
                break

            # get the first paging url
            page_url = page_url[0]

    def crawl(self):
        print('=============================')
        print(f'start crawl {SOURCE}')
        for paste in self.get_new_pastes():
            self._store_paste(paste)
        print('finish current job')
        print(f'next run in {JOB_INTERVAL_HOURS} hours')
        print('=============================')
        self._finish_crawl()


if __name__ == "__main__":
    c = SimpleTorCrawler()
    c.crawl()

    running = True
    sched = BackgroundScheduler()
    sched.add_job(c.crawl, 'interval', hours=JOB_INTERVAL_HOURS)
    sched.start()
    try:
        while running:
            time.sleep(1)
            for s in sorted(six.iteritems(sched._jobstores)):
                jobs = s[1].get_all_jobs()
                if jobs == []:
                    running = False
                    print('closing')

    except Exception:
        print('The program has been interrupted. closing')
        sched.shutdown()
