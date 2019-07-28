'''youdao translate for free as in beer

limited to maximum of 50 chars
'''
import logging
from pathlib import Path
from time import sleep
from random import random

import hashlib
import requests_cache
# from jmespath import search

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

HOME_FOLDER = Path.home()
__FILE__ = globals().get('__file__') or 'test'
CACHE_NAME = (Path(HOME_FOLDER) / (Path(__FILE__)).stem).as_posix()
EXPIRE_AFTER = 3600

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) '\
     'AppleWebKit/537.36 (KHTML, like Gecko) '\
     'Chrome/67.0.3396.99 Safari/537.36'
HEADERS = {
    'User-Agent': USER_AGENT,
    'Host': 'fanyi.youdao.com',
    'Origin': 'http://fanyi.youdao.com',
    'Referer': 'http://fanyi.youdao.com/',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',  # pylint: disable=duplicate-key
}

COOKIES = {  # pylint: disable=duplicate-key
    'OUTFOX_SEARCH_USER_ID': '-445605139@10.168.8.63',  # valid
    'OUTFOX_SEARCH_USER_ID': '-2022895048@10.168.8.76;',  # valid
    "OUTFOX_SEARCH_USER_ID": "1660767496@10.168.8.63",  # valid

    "OUTFOX_SEARCH_USER_ID": "833225052@10.169.0.83",  # from devtools

        # 'JSESSIONID': 'aaaS-VdjFju2I-Vb2FZAw',
        # 'OUTFOX_SEARCH_USER_ID_NCOO': '1386887341.1391568',
        # '___rl__test__cookies': salt,
    }

# fetch a new one if this one no longer works
# e.g. fanyijs = request.get('http://shared.ydstatic.com/fanyi/newweb/v1.0.19/scripts/newweb/fanyi.min.js').text
# APID = re.search(r'md5\("fanyideskweb"\+e\+i\+"(.*?)"', fanyijs).groups()[0]
# 'n%A-rKaT5fb[Gy?;N5@Tj'
# assert len(APID) == 21

APID = 'n%A-rKaT5fb[Gy?;N5@Tj'  # plan-B
APID = '97_3(jkMYg@T[KZQmqjTK'

URL = 'http://fanyi.youdao.com/translate_o?'\
    'smartresult=dict&smartresult=rule'

ERRORCODE = {
    '0': "正常",
    '20': "要翻译的文本过长(>400)",
    '30': "无法进行有效的翻译",
    '40': "不支持的语言类型",
    '50': "无效的key",
    '60': "无词典结果，仅在获取词典结果生效",
    }


def make_throttle_hook(timeout=0.67, exempt=1000):
    """
    Returns a response hook function which sleeps for `timeout` seconds if
    response is not cached

    the first exempt calls exempted from throttling
    """

    try:
        timeout = float(timeout)
    except Exception as _:
        timeout = .67

    try:
        exempt = int(exempt)
    except Exception as _:
        exempt = 100

    def hook(response, *args, **kwargs):  # pylint: disable=unused-argument
        if not getattr(response, 'from_cache', False):
            timeout_ = timeout + random() - 0.5
            timeout_ = max(0, timeout_)

            try:
                hook.flag
            except AttributeError:
                hook.flag = -1
            finally:
                hook.flag += 1
                quo, _ = divmod(hook.flag, exempt)
            # quo is 0 only for the first exempt calls

            LOGGER.debug('avg delay: %s, sleeping %s s, flag: %s', timeout, timeout_, bool(quo))

            # will not sleep (timeout_ * bool(quo)=0) for the first exempt calls
            sleep(timeout_ * bool(quo))

        return response
    return hook


SESS = requests_cache.CachedSession(
    cache_name=CACHE_NAME,
    expire_after=EXPIRE_AFTER,
    allowable_methods=('GET', 'POST'),
)

SESS.hooks = {'response': make_throttle_hook()}

def youdao_tr(  # pylint: disable=too-many-locals
        text,
        from_lang='auto',
        to_lang='auto',
        timeout=(55, 66),
    ):
    '''
    youdao translate
    '''
    text = text.strip()
    if not text:
        youdao_tr.text = 'Nothing to do'
        youdao_tr.json = {"msg": "Nothing to do"}
        return ''

    salt = str(len(text))
    sign = hashlib.md5(('fanyideskweb' + text \
    + salt + APID).encode('utf-8')).hexdigest()

    data = {
        'i': text,
        'from': from_lang,
        'to': to_lang,
        'smartresult': ['dict', 'rule', 'ugc'],
        'client': 'fanyideskweb',
        'salt': salt,
        'sign': sign,
        'doctype': 'json',
        'version': '2.1',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_REALTIME',
        'typoResult': 'false',
    }

    try:
        resp = SESS.post(
            URL,
            data=data,
            headers=HEADERS,
            cookies=COOKIES,
            timeout=timeout,
        )
        resp.raise_for_status()
    except Exception as exc:  # pragma: no cover
        LOGGER.error(exc)
        resp = str(exc)
        youdao_tr.text = str(exc)
        youdao_tr.json = {'error': str(exc)}
        return str(exc)

    try:
        youdao_tr.text = resp.text
        jdata = resp.json()
    except Exception as exc:  # pragma: no cover
        LOGGER.error(exc)
        youdao_tr.text = str(exc)
        youdao_tr.json = {'error': str(exc)}

    tr_res = jdata.get('translateResult')

    if not str(jdata): # pragma: no cover
        return str(jdata)

    try:
        res = tr_res[0][0].get('tgt')
        # res = search('[][].tgt', tr_res)
    except Exception as exc:  # pragma: no cover
        LOGGER.error(exc)
        res = str(exc)
    return ''.join(res)


def test_empty():
    '''test space'''
    text = ' '
    assert youdao_tr(text) == ''


def test_1():
    '''test 1: test 123'''
    text = 'test 123'
    assert youdao_tr(text) == '测试123'


def test_de():
    '''test de'''
    text = 'Dies ist ein Test'
    assert youdao_tr(text) == '这是测试'


def test_fr():
    '''test fr'''
    text = 'c\'est bon'
    assert '好' in youdao_tr(text)

def test_random():
    ''' test random'''
    from sys import maxsize
    from random import randint

    text = 'test ' + str(randint(0, maxsize))
    assert youdao_tr(text)[:2] in ['测试', '实验']


def pressure_test():
    '''pressure tests'''
    from sys import maxsize
    from random import randint
    from tqdm import trange

    for _ in trange(50):
        text = 'test ' + str(randint(0, maxsize))
        assert youdao_tr(text)[:2] in ['测试', ]


def main():  # pragma: no cover
    '''main'''
    import sys

    if len(sys.argv) < 2:
        print('Supply some English or Chinese text.')
        sys.exit(1)

    print(youdao_tr(' '.join(sys.argv[1: ])))

if __name__ == '__main__':  # pragma: no cover
    main()
