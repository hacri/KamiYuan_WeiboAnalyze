# coding=utf-8

import re
import wb_client
import time

client = wb_client.get_client()
result = client.get('http://weibo.com/aj/v6/mblog/info/big', params={
    'ajwvr': 6,
    'id': 3828611973026681,
    '__rnd': int(time.time() * 1000)
})
print(result.text)
print(wb_client)
