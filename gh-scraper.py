import sys
import getopt
import requests
import urllib.request
from bs4 import BeautifulSoup
import os

sitemap = 'sitemap.xml'
UA = 'Mozilla/5.0'
dataDir = './data'
assetMap = {}

def fetchMaps(url):
    print('Fetching sitemaps from ' + url)
    resp = requests.get(url)
    if(resp.status_code == 200):
        siteSoup = BeautifulSoup(resp.text,'xml')
        maps = siteSoup.findAll('sitemap')
        if len(maps) > 0:
            return maps
        else:
            return []


def fetchLocations(mp):
    ml = mp.find('loc')
    print('Fetching locations from ' + ml.string)
    mLData = requests.get(ml.string)
    if(mLData.status_code == 200):
        mLXML = BeautifulSoup(mLData.text,'xml')
        mLURLs = mLXML.findAll('url')
    if len(mLURLs) > 0:
        return mLURLs
    else:
        return []


def fetchAsset(locElem, type):
    locURL = locElem.find('loc')
    print('Fetching assets from ' + locURL.string)
    locURLData = requests.get(locURL.string)
    if(locURLData.status_code == 200):
        locHTML = BeautifulSoup(locURLData.text, 'html.parser')
        locElems = locHTML.findAll(str(type))
    if len(locElems) > 0:
        for e in locElems:
            aU = e['src']
            assetURL = aU
            if aU[0] == '/':
                url = locURL.string[:-1]
                uri = url.split('//')
                proto = uri[0]
                base = (uri[1].split('/'))[0]
                assetURL = proto + '//' + base + aU
            if not assetURL in assetMap:  
                print('Downloading asset: ' + assetURL)
                req = urllib.request.Request(assetURL, headers={'User-Agent': UA})
                assetLocation = urllib.request.urlopen(req)
                assetData = assetLocation.read()
                assetFPath = dataDir + '/' + (locURL.string[:-1].split('/')).pop() + '/' + (aU.split('/')).pop()
                print('Writing to ' + assetFPath)
                os.makedirs(os.path.dirname(assetFPath), exist_ok=True)
                with open(assetFPath, "wb") as f:
                    f.write(assetData)
                    f.close()
                    assetMap[assetURL] = assetFPath
            else:
                print('Skipping previously downloaded asset ' + assetURL)

def main():
    try:
        opts, args = getopt.getopt(sys.argv,'d:u:a:',['directory=','user-agent=','asset='])
        if len(args) <= 1:
            raise Exception('Invalid arguments')
    except:
        print('Usage: gh-scraper.py [opts] url')

    try:
        url = args.pop()
        siteMapURL = url + '/' + sitemap
        maps = fetchMaps(siteMapURL)
        print('Found ' + str(len(maps)) + ' sitemaps')
        for m in maps:
            locs = fetchLocations(m)
            print('Found ' + str(len(locs)) + ' locations to lookup in map ' + m.find('loc').string)
            for l in locs:
                try:
                    fetchAsset(l,'img')
                except Exception as err:
                    print(err)
                    print('Skipping fetch attempt due to error')
                    continue

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
