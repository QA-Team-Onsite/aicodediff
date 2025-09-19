#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: gaobo
@Project: py-codediff
@file: read_report_view.py
@Date: 2025/2/18 9:51
@Description: 
"""
from datetime import timedelta

from model.save_read_report import ReportModel
def read_report(report_id):
    sql_report = ReportModel().report_query_model(report_id=report_id)
    report = {"code": 200, "data": {}}

    # 假设 sql_report 是包含元组的列表
    for i in sql_report:

        # 如果 i[2] 不存在，初始化它为一个字典
        if i[2] not in report["data"]:
            report["data"][i[2]] = {}
        method_name = "\n\n" + i[3]
        # 如果 i[3] 不存在，初始化它为一个空列表
        if i[3] not in report["data"][i[2]]:
            report["data"][i[2]][method_name] = []

        # 向 i[3] 对应的列表中追加 i[4] 和 i[5]
        report["data"][i[2]][method_name].extend([i[4], i[5]])

    print(report)

    return report

def report_time(report_id):
    sql_report = ReportModel().report_time_model(report_id=report_id)
    print(sql_report)
    report_timediff, report_time_num = sql_report[0]
    print("report_timediff",report_timediff)
    print(type(report_timediff))
    total_seconds = int(report_timediff.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
    report = {"code": 200, "data": {"report_timediff":time_str,"report_time_num":report_time_num}}
    print(report)
    return report