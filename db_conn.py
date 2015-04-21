# coding=utf-8

import pymysql
import pymysql.cursors

my_conn = pymysql.connect(
    host='localhost',
    user='root',
    passwd='',
    db='weibo_analyze',
    charset='utf8',
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)
