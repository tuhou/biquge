# -*- coding:utf-8 -*-
"""
author:tuhou
time:2022/11/3 13:59 
思路：
"""
from pymongo import MongoClient


def get_db():
    # uname = 'root'
    # passwd = 'password'
    host = '127.0.0.1'
    port = 27017
    book_db = 'biquge'
    mc = MongoClient(host, port)
    db = mc[book_db]
    # db.authenticate(uname, passwd)
    return db


def run():
    pass


if __name__ == '__main__':
    run()