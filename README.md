# Easyxss

A simple threading based tool to find reflection in parameters of multiple URLS for cross site scripting identification.

## Requirements

```
▶ requests
▶ corlorama
▶ argparse
▶ urlparse
▶ time
▶ slackclient
▶ urllib3
```

## Usage

Basic usage:

```
▶ python3 easyxss.py -f urls.txt -o output.txt

```

Output to Slack:

```
▶ python3 easyxss.py -f urls.txt -t YOUR_SLACK_TOKEN -o output.txt
```

Options:

```
▶ usage: easyxss.py [-h] -f LIST [-t SLACKTOKEN] -o OUTPUT

Identify Reflection in parameters

optional arguments:
  -h, --help            show this help message and exit
  -f LIST, --list LIST  List of urls with parameters
  -t SLACKTOKEN, --slacktoken SLACKTOKEN
                        Slack Token
  -o OUTPUT, --output OUTPUT
                        Output file
```

## Demo

[![asciicast](https://asciinema.org/a/rBhTSSt5scYVLD0G8dqjTFwCC.svg)](https://asciinema.org/a/rBhTSSt5scYVLD0G8dqjTFwCC)
