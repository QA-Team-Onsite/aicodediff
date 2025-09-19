#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: gaobo
@Project: py-codediff
@file: save_read_report.py
@Date: 2025/2/17 19:48
@Description: 
"""
# !/user/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from base.sql_manage import DatabaseManager


class ReportModel:
    def report_query_model(self,report_id):

        report_query = '''SELECT * FROM ai_code_review.code_review_report WHERE report_id = %s ORDER BY id;'''
        params = (report_id,)


        return DatabaseManager().execute_sql(report_query, params)

    def report_save_model(self,report_id,file_path,method_name,modelresult,sourcecode,sourcecode_stack):
        params = (report_id,file_path,method_name,modelresult,sourcecode,sourcecode_stack)
        report_save = '''INSERT INTO ai_code_review.code_review_report (report_id,file_path,method_name,modelresult,sourcecode,sourcecode_stack) 
        VALUES (%s, %s, %s, %s,%s,%s);'''
        return DatabaseManager().execute_sql(report_save, params,fetch=False)

    def report_time_model(self,report_id):
        params = (report_id,)
        print(params)
        max_min_time = '''SELECT SEC_TO_TIME(TIMESTAMPDIFF(SECOND, MIN(created_at), MAX(created_at))) AS time_diff,
       COUNT(*) AS number_report
FROM ai_code_review.code_review_report 
WHERE report_id = %s;
'''
        print(DatabaseManager().execute_sql(max_min_time, params))
        return DatabaseManager().execute_sql(max_min_time, params)

