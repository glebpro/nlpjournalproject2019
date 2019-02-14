#
#   Download utterances from TED talks centered around terms listed in
#   tcse_terms.txt. Will output `<timestamp> <utterance>` lines to `tcse_data/<term>.txt`
#   Timestamps assigned to random notes in equal distribution between 3 months.
#
#   Usage: python download_tcse_data.py
#   Output: ./tcse_data/[term].txt
#
#   @author Gleb Promokhov gleb.promokhov@gmail.com
#

import requests
import os
import sys
import json
import time
import random
import datetime

HEADERS = {
    'Origin': 'https://yohasebe.com',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Referer': 'https://yohasebe.com/tcse/',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    'DNT': '1',
}
BASE_URL = 'https://yohasebe.com/tcse'
ROOT_PATH = sys.path[0]

START_DATE = datetime.datetime(2019, 1, 30)
END_DATE = datetime.datetime(2019, 3, 30)

# build output path
OUTPUT_PATH = ROOT_PATH+'/tcse_data'
if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

# get intput terms
INPUT_TERMS = open(ROOT_PATH+'/tcse_terms.txt', 'r').readlines()
INPUT_TERMS = [i.strip() for i in INPUT_TERMS]

def getRandomTime():
    return str(random.random() * (END_DATE - START_DATE) + START_DATE)

def executeQuery(term):

    data = {
      'text': term,
      'offset': '0',
      'total': '0',
      'if_talk': 'f',
      'advanced': 't',
      'allow_en_only': 't',
      'target': 'sentence',
      'search': 'en',
      'lang_id': '0'
    }

    response = requests.post(BASE_URL+'/execute', headers=HEADERS, data=data)

    return response.text

def download_tcse_terms():

    for term in INPUT_TERMS:
        with open(OUTPUT_PATH + '/' + term + '.txt', 'w') as outfile:

            # execute query
            response = json.loads(executeQuery(term))

            # get out utterances
            data = response['targets']
            data = [i['en'] for i in data]

            # write random time and sentence down
            for sentence in data:
                outfile.write(getRandomTime() + ' ' + sentence + '\n')

            # don't overload TCSE website
            time.sleep(2)

download_tcse_terms()

















#
