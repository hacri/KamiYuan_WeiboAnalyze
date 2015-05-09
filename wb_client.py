# coding=utf-8

import requests
import requests.cookies

wb_client = None


def init_client():
    global wb_client
    cookie_file = open('cookie.txt', 'r')
    cookie_str_arr = []
    for i in cookie_file:
        cookie_str_arr.append(i.strip())
    cookie_file.close()

    cookie_str = ''.join(cookie_str_arr)
    cookie_arr = cookie_str.split('; ')

    cookie_dict = {}
    for i in cookie_arr:
        tmp = i.split('=')
        if len(tmp) >= 2:
            cookie_dict[tmp[0]] = tmp[1]

    # 伪造成浏览器
    wb_client = requests.session()
    wb_client.cookies = requests.cookies.cookiejar_from_dict(cookie_dict)
    wb_client.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0'
    wb_client.headers['X-Requested-With'] = 'XMLHttpRequest'

    pass


def get_client():
    """
    :rtype: requests.Session
    """
    global wb_client
    if wb_client is None:
        init_client()
        pass
    return wb_client
    pass

