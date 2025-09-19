#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: gaobo
@Project: py-codediff
@file: mark_added_lines_view.py
@Date: 2025/7/17 12:03
@Description: 
"""
import difflib
import re

def extract_code(line: str) -> str:
    """
    从一行代码中提取出“纯净的代码”部分，去掉 diff 行中的 '+' 或者原始代码中的行号前缀。
    """
    line = line.lstrip('+').rstrip()  # 去掉开头的 '+' 和结尾多余空格

    # 匹配行号格式，例如 "35    some code" 或 "  42: some code"
    match = re.match(r'^\s*\d+\s*[:]?\s*(.*)', line)

    # 如果匹配到了，就返回冒号/空格后面的真正代码部分；否则直接返回去除首尾空格的内容
    return match.group(1) if match else line.strip()

def mark_added_lines(original_code: str, diff_code: str, similarity_threshold: float = 0.8) -> str:
    """
    对 original_code 中与 diff_code 中新增代码相似度大于等于阈值的行加 '+' 标记。
    original_code：带有行号的原始代码字符串。
    diff_code：标准 diff 格式（以 + 开头为新增行）。
    similarity_threshold：匹配相似度阈值，默认是 0.8（即 80% 相似度视为“相似”）。
    """
    # 原始代码按行切割，并去除每行末尾空格
    original_lines = original_code.strip().splitlines()
    cleaned_original_lines = [line.rstrip() for line in original_lines]

    # 处理 diff 中新增行，只保留 '+' 开头的行（排除像 "+++ file.java" 这种 diff 元信息）
    added_lines = [
        extract_code(line)  # 提取新增行的纯代码内容
        for line in diff_code.strip().splitlines()
        if line.strip().startswith('+') and not line.strip().startswith('+++')
    ]

    marked_lines = []  # 最终标记后的结果
    for line in cleaned_original_lines:
        # 从原始代码行中提取纯代码内容（忽略行号前缀）
        stripped_line = extract_code(line)

        # 计算当前行与所有新增行的相似度，并取最大值
        max_similarity = max(
            difflib.SequenceMatcher(None, stripped_line, added).ratio()
            for added in added_lines
        ) if added_lines else 0.0

        if max_similarity >= similarity_threshold:
            # 如果最大相似度大于等于阈值，说明这行是“新增”内容，进行标记

            # 匹配并分离出前缀部分（如行号）和代码部分
            prefix_match = re.match(r'^(\s*\d+\s*[:]?)(.*)', line)

            if prefix_match:
                prefix = prefix_match.group(1)  # 行号部分
                code = prefix_match.group(2)    # 代码部分
                marked_lines.append(f'+{prefix}{code}')  # 在行号前加上 '+'
            else:
                marked_lines.append(f'+{line}')  # 没有行号的行，直接整体加 '+'
        else:
            # 非新增内容，原样保留
            marked_lines.append(line)

    return "\n".join(marked_lines)
