#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: gaobo
@Project: aicodediff
@file: fe_view.py
@Date: 2025/4/29 16:13
@Description:
"""
import os
import re
import requests
from model.save_read_report import ReportModel
from base.enum import Enum


def fe(diff_output_path,base_path,port,model,num_ctx,report_id):
        # 用于存储文件路径和变动方法名
        modified_methods_by_file = {}
        # 当前文件路径
        current_file = None
        ollama_count = 0

    # 读取本地保存的 git diff 文件diff_output.txt
        with open(diff_output_path, "r", encoding='utf-8', errors='ignore') as file:
            current_method_num = 0
            # 遍历git diff文件将文件内容分类存储到modified_methods_by_file字典中
            for line in file:
                # 检查是否是文件路径的变更行
                if line.startswith("--- a/") or line.startswith("+++ b/"):
                    current_file = line.split()[1]  # 获取文件路径
                    if current_file.startswith(('a', 'b')):
                        current_file = current_file[1:]
                    modified_methods_by_file[current_file] = []
                    current_method_num = 0
                    continue
                if line.startswith("@@"):
                    current_method_num += 1
                    current_method = f"code_{current_method_num}"
                    modified_methods_by_file[current_file].append({current_method: ""})
                    # 将当前代码行添加到该方法的代码字符串中
                    modified_methods_by_file[current_file][current_method_num-1][current_method] += line.strip() + "\n"
                    continue
                if line.startswith("diff --git") or line.startswith("index") or line.startswith("deleted file") or line.startswith("---") or line.startswith("+++"):
                    continue
                else:
                    if line.startswith('-'):
                        continue
                    else:
                        modified_methods_by_file[current_file][current_method_num-1][current_method] += line.strip() + "\n"  # 将当前代码行添加到该方法的代码字符串中
        print("modified_methods_by_file:::", modified_methods_by_file)
        # 遍历modified_methods_by_file字典,获取大模型结果,存库
        if modified_methods_by_file:
            for file_path, values in modified_methods_by_file.items():
                # 提取后缀名
                print("文件后缀名file_extension:::", file_path)
                file_extension = os.path.splitext(file_path)[1].lstrip('.') if os.path.splitext(file_path)[1] else ""
                print("文件后缀名file_extension:::", file_extension)
                for value in values:
                    for method_name, method_code in value.items():  # 正确解包字典中的唯一键值对
                        if "+0,0" in method_code:
                            continue
                        print("大模型传参:::", {"code": method_code, "model": model, "num_ctx": num_ctx, "fbend": 1, "stype": file_extension})
                        ollama_response = requests.post(f"http://{Enum.host}:{port}/ollama/generate", json={"code": method_code, "model": model, "num_ctx": num_ctx, "fbend": 1, "stype": file_extension})
                        ollama_count += 1
                        print("接口调用次数ollama_count:::", ollama_count)
                        ollama_json = ollama_response.json()
                        print("增量方法大模型结果ollama_json:::", ollama_json)
                        ollama_content = ollama_json["content"]
                        # 插入数据库
                        ReportModel().report_save_model(report_id=report_id, file_path=file_path, method_name=method_name,
                                                        modelresult=method_code, sourcecode=ollama_content,
                                                        sourcecode_stack=method_code)
                        print("数据插入成功")
            response_fin = {"code": 200, "data": modified_methods_by_file, "msg": "操作成功"}
            return response_fin
        else:
            response_fin = {"code": 200, "data": {}, "msg": "当前分支与基线分支代码不存在差异"}
            return response_fin
