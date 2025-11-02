# -*- coding: utf-8 -*-

# This code shows an example of text translation from English to Simplified-Chinese.
# This code runs on Python 2.7.x and Python 3.x.
# You may install `requests` to run this code: pip install requests
# Please refer to `https://api.fanyi.baidu.com/doc/21` for complete api document
import json
import time

import requests
import random
from hashlib import md5


# Generate salt and sign
def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()


def baidu_trans(query):
    # query = 'Hello World! This is 1st paragraph. This is 2nd paragraph.'

    # Set your own appid/appkey.
    appid = '20200512000450035'
    appkey = '2CZmCvIx6GgatEdBCVZU'

    # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
    from_lang = 'en'
    to_lang = 'zh'

    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path

    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

    # Send request
    dst = ''
    try:
        while True:
            try:
                r = requests.post(url, params=payload, headers=headers)
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
                if 'bad handshake' in str(e) or '10054' in str(e):
                    continue  
                else:
                    raise Exception(e)
            break
        # time.sleep(5)
        result = json.loads(r.text)


        for trans in result.get('trans_result', {}):
            dst += trans.get('dst', '')
    except requests.exceptions.ProxyError as e:
        print(f'Error: HTTPConnectionPool. {e}')
        raise

    return dst


if __name__ == "__main__":
    _query = 'Hello World! This is 1st paragraph.\nThis is 2nd paragraph.'
    _res = baidu_trans(_query)
    print(_res)
    pass
