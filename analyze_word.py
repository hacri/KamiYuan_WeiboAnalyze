# coding=utf-8

import db_conn
import jieba
import jieba.posseg
import re


def analyze_forwards(origin_mid):
    cur = db_conn.my_conn.cursor()
    cur.execute('''
    SELECT wb_content_main FROM forward_info
    WHERE origin_mid = '%s'
    ''' % origin_mid)

    img_reg = re.compile(r'\[.*\]')
    result = {}
    for i in cur:
        wb_main = i['wb_content_main']
        wb_main = wb_main.strip()
        wb_main = img_reg.sub('', wb_main)
        wb_result = jieba.posseg.cut(wb_main)

        for j in wb_result:
            if j.flag in ('r', 'o', 'p', 'm', 'uj',
                          'x', 'd', 'y', 'a', 'q',
                          'c', 'f', 'vg', 'ad', 'ul',
                          'zg', 'ud', 'l'):
                continue
            word = j.word.strip()
            if len(word) < 2:
                continue

            if word in result:
                result[word] += 1
            else:
                result[word] = 1
            pass
        pass

    for i in result:
        try:
            db_conn.my_conn.cursor().execute("INSERT INTO forward_stat SET origin_mid = %s, word = '%s', count = %d;"
                                             % (origin_mid, i, result[i]))
        except:
            pass


if __name__ == '__main__':
    analyze_forwards(3825463934283470)
