# coding=utf-8

import time
import random
import wb_client
import process_weibo_page
import process_weibo_share_and_comment


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
        print(page_info)

        cool_down -= 1
        pass

    pass


if __name__ == '__main__':
    req_all_forward_info('http://weibo.com/2769186257/CcvBnyQbL')
    pass
