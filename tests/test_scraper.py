from creeper.scraper import Scraper
from creeper.pages import GitHubSearchPage, GitHubRepositoryPage


class TestScraper:

    def test_run_succeed(
            self, mocker,
            search_results_html, repository_html,
            mock_github_search_page, mock_github_repository_page
    ):
        mock_github_search_page.is_fetched = True
        mock_github_search_page.page_content = search_results_html
        mocker.patch(
            'creeper.scraper.Scraper.get_search_page',
            return_value=mock_github_search_page
        )

        scraper = Scraper(keywords=['test'], search_type='issues', proxies=[])
        result = scraper.run()

        assert not scraper.is_repository_search
        assert len(result) == 10
        assert 'TheAlgorithms/Python' in result[0]['url']

        mock_github_repository_page.is_fetched = True
        mock_github_repository_page.page_content = repository_html
        mock_github_repository_page.parse()
        mocker.patch(
            'creeper.scraper.Scraper.fetch_pages',
            return_value=[mock_github_repository_page]
        )

        scraper = Scraper(keywords=['test'], search_type='repositories', proxies=[])
        result = scraper.run()

        assert scraper.is_repository_search
        assert len(result) == 1

        extra_data = result[0]['extra']
        assert extra_data['author'] == 'yusugomori'
        assert extra_data['language_stats']['Go'] == 14.2

    def test_run_failed(
            self, mocker, search_results_html,
            mock_github_search_page, mock_github_repository_page,
    ):
        mock_github_search_page.is_fetched = False
        mocker.patch(
            'creeper.scraper.Scraper.get_search_page',
            return_value=mock_github_search_page
        )

        scraper = Scraper(keywords=['test'], search_type='issues', proxies=[])

        try:
            scraper.run()
        except ValueError as e:
            assert str(e) == 'Page content is not fetched'

        mock_github_search_page.is_fetched = True
        mock_github_search_page.page_content = search_results_html
        mocker.patch(
            'creeper.scraper.Scraper.get_search_page',
            return_value=mock_github_search_page
        )

        mock_github_repository_page.is_fetched = False
        mocker.patch(
            'creeper.scraper.Scraper.fetch_pages',
            return_value=[mock_github_repository_page]
        )

        scraper = Scraper(keywords=['test'], search_type='repositories', proxies=[])
        result = scraper.run()

        assert len(result) == 1
        assert result[0]['error'] == 'Failed to fetch page'

    def test_get_search_page_succeed(self):
        scraper = Scraper(keywords=['test'], search_type='issues', proxies=[])
        search_page = scraper.get_search_page()
        assert isinstance(search_page, GitHubSearchPage)

    def test_get_search_page_failed(self):
        scraper = Scraper(keywords=['test'], search_type='invalid', proxies=[])
        try:
            scraper.get_search_page()
        except ValueError as e:
            assert str(e) == 'Unsupported search type: invalid'

    def test_page_fetcher(self, mock_github_repository_page, search_results_html):
        mock_github_repository_page.is_fetched = True
        mock_github_repository_page.page_content = search_results_html

        scraper = Scraper(keywords=['test'], search_type='issues', proxies=[])
        page = scraper.page_fetcher(mock_github_repository_page)

        assert page is mock_github_repository_page
        assert page.parse_results

    def test_setup_session(self):
        scraper = Scraper(keywords=['test'], search_type='issues', proxies=[])
        assert not scraper.session.proxies

        scraper.proxies = ['fake_proxy']
        scraper.setup_session()
        assert scraper.session.proxies
