import pymongo
import pytz
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
tzinfo = pytz.timezone('Asia/Shanghai')


class MongoDB(object):

    """
    mongoDB相关操作封装
    """

    __slots__ = '__dbLink'

    def __init__(self, db_name, table_name):

        """
        :param db_name: 连接的mongoDB函数库名
        :param table_name: 连接的库的表名
        """

        server_ip = 'localhost'
        server_port = 27017
        user_name = ""
        user_password = ""

        conn = pymongo.MongoClient(host=server_ip, port=server_port, tz_aware=True, tzinfo=tzinfo)
        whois_db = conn[db_name]
        # whois_db.authenticate(user_name, user_password)
        col_name = whois_db[table_name]
        self.__dbLink = col_name

    def get_link(self):

        """
        :return: 连接上的mongo库状态
        """
        return self.__dbLink

    def get_download(self, command=None, show=None):

        """
        :param command: 执行查询的单命令
        :param show: 显示限制查询命令
        :return: 返回结果列表
        """

        if command is None:
            command = {}
        if show:
            result = self.__dbLink.find(command, show).limit(1000000)
        else:
            result = self.__dbLink.find(command).limit(1000000)
        pi = []
        for i in result:
            pi.append(i)

        return pi

    def roll_find(self, lists, field, show=None):

        """
        :param lists: 轮询查询的列表
        :param field: 需要查询的字段
        :param show: 显示限制查询命令
        :return: 返回结果列表
        """

        pi = []
        if show:
            for i in lists:
                result = self.__dbLink.find({field: i}, show).limit(10000)
                for q in result:
                    pi.append(q)
        else:
            for i in lists:
                result = self.__dbLink.find({field: i}).limit(10000)
                for q in result:
                    pi.append(q)

        return pi

    def whois_coll_thread_pool_flint(self, type_a, find_df, max_workers=100):
        result_back = []

        def find_whois(llink, type_c, key_limit_c, whois_server_list):
            projection = {
                "r_domainname": 1,
                "r_whoisserver_list": 1,
            }
            result = pd.DataFrame(llink.find({type_c: key_limit_c}, projection))
            domain = []
            for ii in range(0, len(result)):
                for q in result.loc[ii, 'r_whoisserver_list']:
                    if q in whois_server_list:
                        if result.loc[ii, 'r_domainname'] not in domain:
                            domain.append(result.loc[ii, 'r_domainname'])
                            break
            return domain

        def result_add(future_result):
            res = future_result.result()
            for i in res:
                if i not in result_back:
                    result_back.append(i)

        thread_pool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="whois_find")
        for i in range(0, len(find_df)):
            key_limit = {
                "$gte": find_df.loc[i, 'start_time'],
                "$lte": find_df.loc[i, 'end_time']
            }
            future = thread_pool.submit(find_whois, self.__dbLink, type_a, key_limit, find_df.loc[i, 'whois_list'])
            future.add_done_callback(result_add)
        thread_pool.shutdown(wait=True)
        return result_back
