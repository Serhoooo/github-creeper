# github-creeper

A simple crawler for GitHub repositories, issues, and wikis.

## Usage with virtual environment

### Prerequisites

- Python 3
- pip
- venv

### Configuring the virtual environment

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

### Run the crawler

Configure the crawler by editing the workspace/[config.json](workspace/config.json) file. The configuration file should
be a JSON file with the following
structure:

```json
{
  "keywords": [
    "Python",
    "GO"
  ],
  "proxies": [
    "your_proxy:port",
    "your_proxy:port"
  ],
  "type": "Repositories"
}
```

Results will be saved in the workspace folder --> [results.json](workspace/results.json) after each run.

To run the crawler, execute the following command:

```bash
python launcher.py
```

### Run the tests

To run all the tests, execute this command:

```bash
pytest
```

To see a coverage report, execute this command:

```bash
pytest  --cov-report term --cov .
```

