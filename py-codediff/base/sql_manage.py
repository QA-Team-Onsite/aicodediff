#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: gaobo
@Project: py-codediff
@file: sql_manage.py
@Date: 2025/2/17 19:45
@Description: 
"""
import pymysql
from pymysql.err import MySQLError
from base.enum import Enum

class DatabaseManager:
        def __init__(self):
            # self.host = "localhost"
            # self.port = 3306
            # self.user = "root"
            # self.password = "root"
            # self.database = "ui_auto"
            self.host = Enum.host
            self.port = 3306
            self.user = Enum.user
            self.password = Enum.password
            self.database = Enum.database
            self.connection = self._create_connection()



        def _create_connection(self):
            """创建数据库连接"""
            try:
                return pymysql.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    port=self.port
                )
            except MySQLError as e:
                print(f"连接错误: {e}")
                return None

        def execute_sql(self, query, params=None, fetch=True):
            """执行 SQL 查询或更新"""
            if not self.connection:
                print("未连接到数据库")
                return None

            cursor = self.connection.cursor()
            try:
                if isinstance(params, list):  # 检查是否为列表，执行批量插入
                    cursor.executemany(query, params)
                else:
                    cursor.execute(query, params)
                if fetch:

                    res=cursor.fetchall()
                    print("查询结果:", res)
                    return res  # 获取结果
                else:
                    self.connection.commit()  # 提交更改
                    return cursor.lastrowid
            except MySQLError as e:
                print(f"执行错误: {e}")


        def close_connection(self):
            """关闭数据库连接"""
            if self.connection:
                self.connection.close()

