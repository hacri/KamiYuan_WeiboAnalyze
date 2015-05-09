# coding=utf-8
import json

import wb_client
import time
import re
from bs4 import BeautifulSoup


def filter_weibo_content(content):
    """
    处理weibo内容。替换链接和表情
    :param content:
    :return:
    """
    if type(content) == 'str':
        soup = BeautifulSoup(content)
    else:
        soup = content
        pass

    for i in soup.find_all('img'):
        if 'title' in i.attrs:
            i.replace_with(i['title'])
        else:
            i.replace_with('[' + i['src'] + ']')

    for i in soup.find_all('a'):
        if 'extra-data' in i.attrs:
            if i['extra-data'] == 'type=atname':
                i.replace_with(i.text + ' ')
                pass
            elif i['extra-data'] == 'a_topic':
                i.replace_with(i.text)
                pass
            pass
        else:
            i.replace_with(i['href'])
            pass
        pass

    text = re.sub('\n', '', soup.text)
    return re.sub('[\n ]{2,}', ' ', text)
    pass


def get_forward_info_from_item(item_html):
    """
    获取1条转发的信息
    :param item_html:
    :return:
    """
    result = {}

    if type(item_html) is str:
        soup = BeautifulSoup(item_html)
        list_li = soup.find(class_='list_li')
    else:
        list_li = item_html

    result['mid'] = int(list_li['mid'])

    a_list = list_li.select('.WB_text > a')
    if len(a_list) == 0:
        return None

    # 获取转发的人的信息
    forward_user = a_list[0]
    user_info = {
        'name': forward_user.get_text(),
        'id': str(forward_user['usercard']).split('=')[1],
        'yellow_v': False,
        'blue_v': False,
        'daren': False,
        'member': 0
    }

    if len(a_list) > 1:
        # 获取用户额外身份
        for i in a_list[1:]:
            # 微博会员
            if 'title' in i.attrs and i['title'] == '微博会员':
                for j in i.find('i')['class']:
                    re_match = re.match('icon_member(\d*)', j)
                    if re_match:
                        user_info['member'] = int(re_match.group(1))
                pass

            else:
                sub_i = i.find('i')
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

    result['user'] = user_info

    # 获取微博内容
    wb_list = list_li.select('.WB_text span')
    if len(wb_list) == 0:
        return None
    wb_main = wb_list[0]
    result['wb_content'] = filter_weibo_content(wb_main)

    # 获取转发评论
    re_wb_main = re.match('^(.*?)//', result['wb_content'])
    if re_wb_main:
        result['wb_content_main'] = re_wb_main.group(1)
        pass
    else:
        result['wb_content_main'] = result['wb_content']
        pass

    # 获取转发来源
    re_search = re.search('//[ ]*@([^ ]+)', result['wb_content'])
    if re_search:
        result['forward_from'] = re_search.group(1)
    else:
        result['forward_from'] = None
        pass

    # 获取转发日期
    a_list = list_li.select('.WB_from a')
    if len(a_list) == 0 or a_list[0]['node-type'] != 'feed_list_item_date':
        return None
        pass
    result['date'] = int(int(a_list[0]['date']) / 1000)

    # 获取转发数据
    handle_list = list_li.select('.WB_handle .S_txt1')
    result['forward'] = 0
    result['like'] = 0
    for i in handle_list:
        if 'action-type' in i.attrs:
            if i['action-type'] == 'feed_list_forward':
                # 获取转发数
                tmp = i.text.split(' ')
                if len(tmp) == 2:
                    result['forward'] = int(tmp[1])
            elif i['action-type'] == 'forward_like':
                # 获取点赞数
                if i.get_text() != '':
                    result['like'] = int(i.get_text())
                pass
            pass
        pass

    # print(result)
    return result
    pass


def get_forward_list_info_from_json(forward_json):
    """
    获取一组（一页）转发内容
    :param forward_json:
    :return:
    """
    result = {
        'count': forward_json['data']['count'],
        'total_page': forward_json['data']['page']['totalpage'],
        'item': [],
        'max_mid': None
    }

    soup = BeautifulSoup(forward_json['data']['html'])
    max_mid = 0

    # 循环获取每条微博转发内容
    for item in soup.select('.list_li'):
        item_result = get_forward_info_from_item(item)
        if item_result['mid'] > max_mid:
            max_mid = item_result['mid']

        result['item'].append(item_result)
        pass

    result['max_mid'] = max_mid
    # print(result)
    return result
    pass


def req_forward_info(mid, page=None, max_id=None):
    """
    发送http请求获取转发内容
    :param mid:
    :param page:
    :param max_id:
    :return:
    """
    params = {
        'ajwvr': 6,
        'id': mid,
        '__rnd': int(time.time() * 1000) - 10000
    }

    if page is not None:
        params['page'] = page
    if max_id is not None:
        params['max_id'] = max_id

    request_result = wb_client.get_client().get('http://weibo.com/aj/v6/mblog/info/big', params=params)

    return request_result.json()
    pass


if __name__ == '__main__':
    data = get_forward_list_info_from_json(json.loads(r'''

        '''.replace('\n', '').strip()))
    print(json.dumps(data))
