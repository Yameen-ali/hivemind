import json
import math

from datetime import datetime

def amount(string):
    return float(string.split(' ')[0])

def parse_time(block_time):
    return datetime.strptime(block_time, '%Y-%m-%dT%H:%M:%S')

def load_json_key(obj, key):
    if not obj[key]:
        return {}
    ret = {}
    try:
        ret = json.loads(obj[key])
    except json.decoder.JSONDecodeError:
        return {}
    return ret

def trunc(string, maxlen):
    if string:
        string = string.strip()
        if len(string) > maxlen:
            string = string[0:(maxlen-3)] + '...'
    return string


def rep_log10(rep):
    def log10(string):
        leading_digits = int(string[0:4])
        log = math.log10(leading_digits) + 0.00000001
        num = len(string) - 1
        return num + (log - int(log))

    rep = str(rep)
    if rep == "0":
        return 25

    sign = -1 if rep[0] == '-' else 1
    if sign < 0:
        rep = rep[1:]

    out = log10(rep)
    out = max(out - 9, 0) * sign  # @ -9, $1 earned is approx magnitude 1
    out = (out * 9) + 25          # 9 points per magnitude. center at 25
    return round(out, 2)


def safe_img_url(url, max_size=1024):
    if url and not isinstance(url, str):
        url = None
    if url:
        url = url.strip()
    if url and len(url) < max_size and url[0:4] == 'http':
        return url
