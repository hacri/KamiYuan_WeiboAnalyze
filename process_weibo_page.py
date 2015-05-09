# coding=utf-8

from bs4 import BeautifulSoup
import re
import json
import process_weibo_share_and_comment
import codecs


def find_id_from_html(raw_html):
    """
    从html中获取mid
    :param raw_html:
    :return:
    """
    soup = BeautifulSoup(raw_html)
    id_item = soup.select('.WB_feed_profile .WB_cardwrap')
    for i in id_item:
        if i['mid']:
            return i['mid']
    return None
    pass


def find_content_from_html(raw_html):
    """
    从html中获取weibo内容
    :param raw_html:
    :return:
    """
    soup = BeautifulSoup(raw_html)
    text_items = soup.select('.WB_text')
    for i in text_items:
        return process_weibo_share_and_comment.filter_weibo_content(i)
    return None
    pass


def get_id_and_content(raw_html):
    """
    从html中获取id和内容
    :param raw_html:
    :return:
    """
    soup = BeautifulSoup(raw_html)

    mid = None
    content = None

    for i in soup.find_all('script'):
        js_str = i.get_text()
        if re.match('^FM\.view\(', js_str):
            js_str = re.sub('^FM\.view\(', '', js_str)
            js_str = re.sub('\)[;]?$', '', js_str)
            if js_str is '':
                continue

            html_json = json.loads(js_str)

            if 'html' not in html_json:
                continue

            if mid is None:
                mid = find_id_from_html(html_json['html'])

            if content is None:
                content = find_content_from_html(html_json['html'])

            if mid is not None and content is not None:
                return mid, content
            pass
        pass
    return None, None
    pass


if __name__ == '__main__':
    # html = codecs.open('weibo_page.html', 'r', encoding='utf-8')
    # print(get_id_and_content(html))
    import wb_client

    thehtml = wb_client.get_client().get('http://weibo.com/2656274875/Cc36UmeSo').text
    print(get_id_and_content(thehtml))
    pass
