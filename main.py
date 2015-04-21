# coding=utf-8

import time
import random
import wb_client
import process_weibo_page
import process_weibo_share_and_comment
import db_conn


def req_all_forward_info(weibo_url):
    wb_page_html = wb_client.get_client().get(weibo_url).text
    (mid, content) = process_weibo_page.get_id_and_content(wb_page_html)

    get_json = process_weibo_share_and_comment.req_forward_info(mid)
    page_info = process_weibo_share_and_comment.get_forward_list_info_from_json(get_json)
    print(page_info)

    max_mid = page_info['max_mid']
    page = page_info['total_page']

    cool_down = 10
    for i in range(1, page + 1):
        if cool_down <= 0:
            time_wait = random.uniform(10, 60)
            cool_down = 10
        else:
            time_wait = random.uniform(1, 5)
        print(time_wait)
        time.sleep(time_wait)

        get_json = process_weibo_share_and_comment.req_forward_info(mid, i, max_mid)
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

            db_conn.my_conn.cursor().execute('''
            INSERT `user_info` (`user_id`, `user_name`, `is_member`, `is_blue_v`, `is_yellow_v`, `is_daren`)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE `user_name` = `user_name`
            ''', (user_info['id'], user_info['name'], user_info['member'], user_info['blue_v'], user_info['yellow_v'],
                  user_info['daren']))

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
    req_all_forward_info('http://weibo.com/1977460817/Cdmu9gcE2')
    pass
