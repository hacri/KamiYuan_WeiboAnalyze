# coding=utf-8

import time
import random
import wb_client
import process_weibo_page
import process_weibo_share_and_comment
import db_conn


def req_all_forward_info(weibo_url):
    """
    获取某条微博的全部转发记录
    :param weibo_url:
    :return:
    """
    wb_page_html = wb_client.get_client().get(weibo_url).text
    (mid, content) = process_weibo_page.get_id_and_content(wb_page_html)

    # 获取第一页转发的原始数据
    get_json = process_weibo_share_and_comment.req_forward_info(mid)
    # 处理第一页
    page_info = process_weibo_share_and_comment.get_forward_list_info_from_json(get_json)
    print(page_info)

    # 最大mid
    max_mid = page_info['max_mid']
    # 总页数
    page = page_info['total_page']

    # 冷却计数，到达这个次数后会长时间等待一次
    cool_down_reset = 10

    cool_down = cool_down_reset
    # 循环获取转发信息（一次一页）
    for i in range(1, page + 1):
        if cool_down <= 0:
            # 随机等10-60s
            time_wait = random.uniform(10, 60)
            cool_down = cool_down_reset
        else:
            # 随机等1-5秒
            time_wait = random.uniform(1, 5)
        print(time_wait)
        time.sleep(time_wait)

        # 获取一页转发信息的原始数据
        get_json = process_weibo_share_and_comment.req_forward_info(mid, i, max_mid)
        # 处理原始数据
        page_info = process_weibo_share_and_comment.get_forward_list_info_from_json(get_json)

        for j in page_info['item']:
            user_info = j['user']

            if user_info['yellow_v']:
                user_info['yellow_v'] = 1
            else:
                user_info['yellow_v'] = 0

            if user_info['blue_v']:
                user_info['blue_v'] = 1
            else:
                user_info['blue_v'] = 0

            if user_info['daren']:
                user_info['daren'] = 1
            else:
                user_info['daren'] = 0

            if j['forward_from'] is None:
                j['forward_from'] = ''

            # 插入数据库（用户信息）
            db_conn.my_conn.cursor().execute('''
            INSERT `user_info` (`user_id`, `user_name`, `is_member`, `is_blue_v`, `is_yellow_v`, `is_daren`)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE `user_name` = `user_name`
            ''', (user_info['id'], user_info['name'], user_info['member'], user_info['blue_v'], user_info['yellow_v'],
                  user_info['daren']))

            # 插入数据库（转发信息）
            db_conn.my_conn.cursor().execute('''
            INSERT `forward_info` (`mid`, `user_id`, `wb_content`, `wb_content_main`, `like_count`, `forward_count`,
                `forward_from`, `date`, `origin_mid`)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE `user_id` = `user_id`
            ''', (j['mid'], user_info['id'], j['wb_content'], j['wb_content_main'], j['like'], j['forward'],
                  j['forward_from'], j['date'], mid))

            pass

        print(page_info)

        cool_down -= 1
        pass

    pass


if __name__ == '__main__':
    # 后面写微博的网址
    req_all_forward_info('http://weibo.com/1977460817/Cdmu9gcE2')
    pass
