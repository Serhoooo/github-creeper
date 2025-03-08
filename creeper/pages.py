import logging
from urllib.parse import urljoin

from lxml.etree import HTML
import requests

logger = logging.getLogger(__name__)


class AbstractGitHubPage:
    BASE_URL = 'https://github.com/'

    def __init__(self, path: str, params: dict = None):
        self.path: str = path
        self.params: dict = params or {}
        self.is_fetched: bool = False
        self.page_content: str = ''
        self.parse_results: list or dict = []

    @property
    def url(self):
        return urljoin(self.BASE_URL, self.path)

    def fetch(self, session: requests.Session):
        response = session.get(self.url, params=self.params)

        if not response.ok:
            logger.error(f'Failed to fetch {self.url}')
            self.is_fetched = False
            return

        self.is_fetched = True
        self.page_content = response.text

    def parse(self):
        if not self.is_fetched:
            raise ValueError('Page content is not fetched')

        if not self.page_content:
            raise ValueError('Page content is empty')

        return self._parse()

    def _parse(self):
        raise NotImplementedError


class GitHubSearchPage(AbstractGitHubPage):
    SEARCH_RESULT_XPATH = '//*[contains(@class, "search-title")]'

    def _parse(self):
        self.parse_results = []

        for result in HTML(self.page_content).xpath(self.SEARCH_RESULT_XPATH):
            a_elements = result.xpath('.//a')
            if not a_elements:
                continue
            self.parse_results.append({'url': a_elements[0].get('href')})

    @property
    def absolute_urls(self):
        return [{'url': urljoin(self.BASE_URL, result['url'])} for result in self.parse_results]


class GitHubRepositoryPage(AbstractGitHubPage):
    AUTHOR_XPATH = 'string(//a[@rel="author"])'
    LANGUAGE_STATS_XPATH = '//li[@class="d-inline"]'

    def _parse(self):
        tree = HTML(self.page_content)
        self.parse_results = {
            'author': tree.xpath(self.AUTHOR_XPATH).strip(),
            'language_stats': self.get_language_stats(tree),
        }

    @classmethod
    def get_language_stats(cls, tree: HTML):
        language_stats = {}

        for li_element in tree.xpath(cls.LANGUAGE_STATS_XPATH):
            a_elements = li_element.xpath('.//a')

            if not a_elements:
                continue

            a_element = a_elements[0]

            try:
                name_span, value_span = a_element.xpath('.//span')
            except ValueError:
                continue

            name = name_span.text.strip()
            value = value_span.text.strip().replace('%', '')

            try:
                value = float(value)
            except ValueError:
                value = None

            language_stats[name] = value

        return language_stats
