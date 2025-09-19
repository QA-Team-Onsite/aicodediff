#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: gaobo
@Project: aicodediff
@file: get_change_method_view.py
@Date: 2025/1/23 17:13
@Description:
"""
import os
import re
import requests
from model.save_read_report import ReportModel
from view.mark_added_lines_view import mark_added_lines
from view.remove_java_comments_view import remove_java_comments
from base.enum import Enum


def get_change_method(diff_output_path,base_path,port,model,num_ctx,report_id,fbend=0):
   #匹配可能带有+或-符号的 Java 方法声public、private）、返回类型、方法名以及参数列表的开始部分 (，并处理可能存在的空白字符和泛型或数组类型。
    method_pattern = re.compile(r'^[+-]?\s*(public|private|protected|static|final)?\s*\w+[\w\<\>\[\]]*\s+(\w+)\s*\(')

    # 用于存储文件路径和变动方法名
    modified_methods_by_file = {}
    # 当前文件路径
    current_file = None


    method_code_stack = {}  # 用来保存每个方法的全量代码

    # 当前方法名称
    current_method = None

    # 读取本地保存的 git diff 文件diff_output.txt
    with open(diff_output_path, "r", encoding='utf-8', errors='ignore') as file:
        for line in file:
            # 检查是否是文件路径的变更行
            if line.startswith("--- a/") or line.startswith("+++ b/"):
                current_file = line.split()[1]  # 获取文件路径
                if current_file.startswith(('a', 'b')):
                    current_file = current_file[1:]
                brace_stack = ['{']  # 重置栈
                continue

            # 处理方法定义行 并更新当前方法名称
            method_match = method_pattern.search(line)
            if method_match:
                current_method = method_match.group(2)  # 提取方法名
                method_code_stack[current_method] = ""
            # 记录方法体代码（不管增减，记录所有代码行）,不是已-开头的行记录
            if current_method and line.startswith('-'):
                continue
            elif current_method:
                method_code_stack[current_method] += line.strip() + "\n"  # 将当前代码行添加到该方法的代码字符串中
            # 处理方法体 并检查方法结束符
                for char in line:
                    if char == "{":
                        brace_stack.append(char)  # 入栈
                    # 检查方法结束符
                    if char == '}':
                        if brace_stack:
                            brace_stack.pop()  #出栈
                            if  brace_stack == ["{"]:
                                current_method = None  # 重置当前方法


            # 如果该行是增减的代码，且当前方法存在，说明该方法有变动 并记录该方法名
            if (line.startswith('+') or line.startswith('-')) and current_method :
                if current_file:  # 如果当前文件路径存在
                    if current_file not in modified_methods_by_file:
                        modified_methods_by_file[current_file] = []
                    # 如果方法尚未记录过，并且栈中不是["{"]，不是["{"]表示当前行在方法体内，添加到列表中（保持顺序）
                    if current_method not in modified_methods_by_file[current_file] and brace_stack != ["{"]:
                        modified_methods_by_file[current_file].append(current_method)
    response_fin = {"code": 200, "data": {}}
    print("增量方法名，文件modified_methods_by_file:::",modified_methods_by_file)


    ollama_count = 0
    # 遍历字典，获取每个文件的方法名，补全文件路径，并获取每个方法的代码
    for key, value in modified_methods_by_file.items():
        for i in range(len(value)):
            if not key.startswith(base_path):
                key = base_path + key
            print("文件绝对路径base_path + key:::", key)
            method_name = value[i]
            body_data = {"methodPath": key}
            #判断当前路径存不存在，不存在跳过
            if not os.path.exists(key):
                print(f"当前路径不存在{key}")
                continue
            # 获取每个方法的代码
            response = requests.post(f"http://{Enum.host}}:8026/codediff/diffmethod", json=body_data)
            response_json=response.json()
            print("全量方法代码response_json:::", response_json)
            # 如果方法名不在返回的methods字典中，则跳过该方法
            if method_name not in response_json["methods"]:
                continue
            # 匹配增量方法的代码
            method_code = response_json["methods"][method_name]["methodCode"]
            begin_line = response_json["methods"][method_name]["beginLine"]
            end_line = response_json["methods"][method_name]["endLine"]
            method_code_lines = method_code.split("\n")
            numbered_code = "\n".join(
                f"{begin_line + i}{line}" for i, line in enumerate(method_code_lines)
            )
            print(numbered_code)
            re_method_code = numbered_code
            method_code =  numbered_code
            # 去除方法代码中的注释
            #re_method_code = remove_java_comments(method_code)
            print("增量方法代码method_code:::", method_code)
            # 调用ollama接口获取增量方法代码的大模型结果
            ollama_response=requests.post( f"http://{Enum.host}:{port}/ollama/generate", json={"code":re_method_code, "model":model ,"num_ctx" :num_ctx,"fbend":fbend})

            print("接口调用结果ollama_response:::", ollama_response)
            # 统计接口调用次数每调用一次增加一次
            ollama_count += 1
            print("接口调用次数ollama_count:::", ollama_count)
            ollama_json=ollama_response.json()
            if ollama_json["is_save"] == 0:
                print("增量方法大模型结果is_save:::", ollama_json["is_save"])
                continue
            print("增量方法大模型结果ollama_json:::", ollama_json)
            ollama_content = ollama_json["content"]
            print("增量方法大模型结果ollama_content:::", ollama_content)
            if key not in response_fin["data"]:
                response_fin["data"].setdefault(key, {})
            response_fin["data"][key].update({method_name: [method_code_stack[method_name],ollama_content]})
            #把response_fin["data"]写到数据库中 存储到数据库中数据库结构是这样的-- auto-generated definition
            #report_id, key, method_name, method_code, ollama_content 有一个不存在就不写库
            print("report_id, key, method_name, method_code, ollama_content:::", report_id, key, method_name, method_code, ollama_content)
            method_code = mark_added_lines(method_code, method_code_stack[method_name])
            if report_id and key and method_name and method_code and ollama_content and method_code_stack[method_name]:
                # 插入数据库
                ReportModel().report_save_model(report_id=report_id, file_path=key, method_name=method_name, modelresult=method_code, sourcecode=ollama_content ,sourcecode_stack=method_code_stack[method_name])
                print("数据插入成功")
            else:
                print("数据插入失败")






    if response_fin["data"] != {}:
        return response_fin
    else:
        response_fin = {"code": 200, "data": {}, "msg": "当前分支与基线分支代码不存在差异"}
        return response_fin