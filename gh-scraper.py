#!/usr/bin/python3

import sys
import getopt
import requests
import urllib.request
from bs4 import BeautifulSoup
import os

_property = {}

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
    global _property
    UA = _property['UA']
    attr = _property['attr']
    dataDir = _property['dataDir']
    assetMap = _property['assetMap']
    assetMap = _property['assetMap']

    locURL = locElem.find('loc')
    print('Fetching assets from ' + locURL.string)
    locURLData = requests.get(locURL.string)
    if(locURLData.status_code == 200):
        locHTML = BeautifulSoup(locURLData.text, 'html.parser')
        locElems = locHTML.findAll(str(type))
    if len(locElems) > 0:
        for e in locElems:
            aU = e[attr]
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

def printUsage(exit_code):
    print('Usage: gh-scraper.py [opts] url')
    sys.exit(exit_code)


def main(argv):
    global _property

    _property['sitemap'] = 'sitemap.xml'
    _property['dataDir'] = './data'
    _property['UA'] = 'Mozilla/5.0'
    _property['tag'] = 'img'
    _property['attr'] = 'src'
    _property['assetMap'] = {}

    try:
        opts, args = getopt.getopt(argv,'hd:u:t:a:',['help','directory=','user-agent=','tag=','attribute='])
        if len(args) < 1:
            raise Exception('Invalid arguments')
        else:
            print(opts)
            for opt, arg in opts:
                if opt == '-h':
                    printUsage(2)
                elif opt in ('-d','--directory'):
                    _property['dataDir'] = arg
                elif opt in ('-u','--user-agent'):
                    _property['UA'] = arg
                elif opt in ('-t','--tag'):
                    _property['tag'] = arg
                elif opt in ('-a','--attribute'):
                    _property['attr'] = arg
    except getopt.GetoptError as ge:
        print(ge.msg)
        print('Argument: '+ge.opt)
        printUsage(2)
    except:
        printUsage(2)

    try:
        url = args.pop()
        siteMapURL = url + '/' + _property['sitemap']
        maps = fetchMaps(siteMapURL)
        print('Found ' + str(len(maps)) + ' sitemaps')
        for m in maps:
            locs = fetchLocations(m)
            print('Found ' + str(len(locs)) + ' locations to lookup in map ' + m.find('loc').string)
            for l in locs:
                try:
                    fetchAsset(l, _property['tag'])
                except Exception as err:
                    print(err)
                    print('Skipping fetch attempt due to error.')
                    continue
        print('Fetch completed. Exiting.')
        sys.exit(0)

    except Exception as e:
        print(e)
        sys.exit(-1)

if __name__ == "__main__":
    main(sys.argv[1:])
