# GhostScraper
An asset scraper for ghost blogs

## Usage

gh_scraper.py [options] [ghost-blog url]

### Options
 - `-d [dir]` or `--directory=[dir]` to specify data directory location. This is the location where the assets will be saved after downloading. It can be either a fullpath or relative path to where the script is being called. The path must not end with a `/`.

 - `-u [ua string]` or `--user-agent=[ua string]` is the user agent string that will be included in the headers for the HTTP GET requests used to pull down assets

 - `-t [tag]` or `--tag=[tag]` specifies the HTML element tag that identifies the asset to fetch

 - `-a [attr]` or `--attribute=[attr]` specifies the attribute of the HTML element tag that identifies the source location for the asset to download

## Dependencies

- [Python3](https://www.python.org)
    - [BeautifulSoup 4](https://www.crummy.com/software/BeautifulSoup/)
    - [lxml](https://lxml.de)
