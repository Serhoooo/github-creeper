import json
import logging
from pathlib import Path

from creeper.scraper import Scraper

logger = logging.getLogger(__name__)


def run_scraper():
    config_path = Path(__file__).parent / 'workspace' / 'config.json'
    results_path = Path(__file__).parent / 'workspace' / 'results.json'

    with open(config_path, 'r') as f:
        config = json.load(f)

    try:
        keywords = config['keywords']
        search_type = config['type'].lower()
        proxies = config['proxies']
    except KeyError:
        logger.error('Invalid config file')
        exit()

    scraper = Scraper(keywords=keywords, search_type=search_type, proxies=proxies)
    results = scraper.run()

    with open(results_path, 'w') as f:
        f.write(json.dumps(results, indent=4))


if __name__ == '__main__':
    run_scraper()
