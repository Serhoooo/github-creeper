import requests
import pytest

from creeper.pages import GitHubSearchPage, GitHubRepositoryPage


class PageTestMixin:

    @pytest.fixture
    def page(self):
        raise NotImplementedError

    def test_fetch_succeed(self, requests_mock, page):
        requests_mock.get(
            page.url,
            text='dummy content',
        )

        page.fetch(session=requests.Session())

        assert page.is_fetched
        assert page.page_content == 'dummy content'

    def test_fetch_failed(self, requests_mock, page):
        requests_mock.get(
            page.url,
            status_code=404,
        )

        page.fetch(session=requests.Session())

        assert not page.is_fetched
        assert not page.page_content

    def test_url(self, page):
        page.path = 'test'
        page.params = {}
        assert page.url == f'{page.BASE_URL}test'

        page.params = {'q': 'test'}
        assert page.url == f'{page.BASE_URL}test?q=test'

    def test_parse_failed(self, page):
        page.is_fetched = False
        try:
            page.parse()
        except ValueError as e:
            assert str(e) == 'Page content is not fetched'

        page.is_fetched = True
        page.page_content = ''
        try:
            page.parse()
        except ValueError as e:
            assert str(e) == 'Page content is empty'


class TestGitHubSearchPage(PageTestMixin):

    @pytest.fixture
    def page(self):
        return GitHubSearchPage(path='search', params={'q': 'test', 'type': 'issues'})

    def test_parse_succeed(self, page, search_results_html):
        page.is_fetched = True
        page.page_content = search_results_html
        page.parse()

        assert page.parse_results
        assert len(page.parse_results) == 10
        assert all('url' in item for item in page.parse_results)


class TestGitHubRepositoryPage(PageTestMixin):

    @pytest.fixture
    def page(self):
        return GitHubRepositoryPage(path='test')

    def test_parse_succeed(self, page, repository_html):
        page.is_fetched = True
        page.page_content = repository_html
        page.parse()

        assert page.parse_results
        assert 'author' in page.parse_results
        assert 'language_stats' in page.parse_results
        assert 'Go' in page.parse_results['language_stats']
        assert page.parse_results['language_stats']['Go'] == 14.2
