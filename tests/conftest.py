from pathlib import Path
import pytest

from creeper.pages import GitHubSearchPage, GitHubRepositoryPage


@pytest.fixture
def repository_html():
    return get_dummy_html('repo_page.html')


@pytest.fixture
def search_results_html():
    return get_dummy_html('search_page.html')


def get_dummy_html(file_name: str) -> str:
    path = Path(__file__).parent / 'dummy_html'

    with open(path / file_name, 'r') as f:
        html_content = f.read()

    return html_content


class MockGitHubSearchPage(GitHubSearchPage):

    def fetch(self, session):
        pass


class MockGitHubRepositoryPage(GitHubRepositoryPage):

    def fetch(self, session):
        pass


@pytest.fixture
def mock_github_search_page():
    return MockGitHubSearchPage(path='')


@pytest.fixture
def mock_github_repository_page():
    return MockGitHubRepositoryPage(path='')
