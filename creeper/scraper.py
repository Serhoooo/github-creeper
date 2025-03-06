from concurrent.futures import ThreadPoolExecutor
import random
import requests

from creeper.pages import GitHubSearchPage, GitHubRepositoryPage, AbstractGitHubPage


class Scraper:
    SEARCH_TYPES = ['repositories', 'issues', 'wikis']

    def __init__(self, keywords: list, search_type: str, proxies: list):
        self.keywords = keywords
        self.search_type = search_type
        self.proxies = proxies
        self.session = requests.Session()
        self.setup_session()

    @property
    def is_repository_search(self) -> bool:
        return self.search_type == 'repositories'

    def setup_session(self):
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
        })
        if self.proxies:
            proxy = random.choice(self.proxies)
            self.session.proxies.update(
                {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}',
                }
            )

    def run(self) -> list:
        search_page = self.get_search_page()
        search_page.fetch(self.session)
        search_page.parse()

        if not search_page.is_fetched:
            raise ValueError('Failed to fetch search page')

        if not self.is_repository_search:
            return search_page.absolute_urls

        results = []

        for page in self.fetch_pages([GitHubRepositoryPage(item['url']) for item in search_page.parse_results]):

            if not page.is_fetched:
                results.append({'url': page.url, 'error': 'Failed to fetch page'})
                continue

            results.append(
                {
                    'url': page.url,
                    'extra': page.parse_results,
                }
            )

        return results

    def get_search_page(self) -> GitHubSearchPage:
        if self.search_type not in self.SEARCH_TYPES:
            raise ValueError(f'Unsupported search type: {self.search_type}')

        return GitHubSearchPage(
            path='search',
            params={
                'q': ' OR '.join(self.keywords),
                'type': self.search_type,
            }
        )

    def fetch_pages(self, pages: [AbstractGitHubPage]) -> iter:
        with ThreadPoolExecutor(max_workers=10) as executor:
            return executor.map(self.page_fetcher, pages)

    def page_fetcher(self, page: GitHubRepositoryPage) -> GitHubRepositoryPage:
        page.fetch(self.session)
        page.parse()
        return page
