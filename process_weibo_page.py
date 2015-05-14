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


def find_pub_date_from_html(raw_html):
    soup = BeautifulSoup(raw_html)
    date_items = soup.select('.WB_feed_profile a.S_txt2')
    for i in date_items:
        if i['date']:
            return int(int(i['date']) / 1000)
    return None
    pass


def get_user_info(raw_html):
    soup = BeautifulSoup(raw_html)
    pf_item = soup.select('.pf_wrap')
    for i in pf_item:
        user_info = {
            'id': 0,
            'name': '',
            'member': False,
            'yellow_v': False,
            'daren': False,
            'blue_v': False,
        }

        username_item = i.select('.username')
        if len(username_item) == 0:
            return None
        user_info['name'] = username_item[0].text

        photo_src = i.find('img', class_='photo')['src']
        result = re.match('http://tp\d.sinaimg.cn/(\d+)/\d+/\d+/1', photo_src)
        if result:
            user_info['id'] = result.group(1)
        else:
            return None

        for j in i.select('a'):
            if 'title' in j.attrs and j['title'] == '微博会员':
                for k in j.find('em')['class']:
                    re_match = re.match('icon_member(\d*)', k)
                    if re_match:
                        user_info['member'] = int(re_match.group(1))
                    pass
                pass
            else:
                sub_i = j.find('em')
                if sub_i is None:
                    continue

                if 'icon_approve' in sub_i['class']:
                    # 黄v认证
                    user_info['yellow_v'] = True
                elif 'icon_club' in sub_i['class']:
                    # 微博达人
                    user_info['daren'] = True
                elif 'icon_approve_co' in sub_i['class']:
                    # 蓝v认证
                    user_info['blue_v'] = True

                pass
            pass
        return user_info
        pass
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
    pub_date = None
    user_info = None

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

            if pub_date is None:
                pub_date = find_pub_date_from_html(html_json['html'])

            if user_info is None:
                user_info = get_user_info(html_json['html'])

            if mid is not None \
                    and content is not None \
                    and pub_date is not None \
                    and user_info is not None:
                return mid, content, pub_date, user_info
            pass
        pass
    return None, None, None, None
    pass


if __name__ == '__main__':
    # html = codecs.open('weibo_page.html', 'r', encoding='utf-8')
    # print(get_id_and_content(html))
    import wb_client

    thehtml = wb_client.get_client().get('http://weibo.com/2656274875/Cc36UmeSo').text
    print(get_id_and_content(thehtml))
    pass
