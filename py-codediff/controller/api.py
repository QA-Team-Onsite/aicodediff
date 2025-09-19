#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: gaobo
@Project: aicodediff
@file: api.py
@Date: 2025/1/23 17:03
@Description: 
"""
import logging

import ollama
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import JSONResponse

from view import get_change_method_view, read_report_view, fe_view
import uvicorn
#初始化FastAPI应用
app = FastAPI(
    title="AI Code Diff API Wrapper",
    description="ollama与获取全部代码的接口",
    version="1.0.0"
)

# 添加 CORS 中间件（跨域支持）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 根据需求限制允许的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# ollama 客户端初始化配置
client = ollama.Client(host="10.230.205.1:1088")
# 日志配置
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# 定义请求模型
class GenerateRequest(BaseModel):
    code: str
    model: str = "deepseek-coder:6.7b"
    num_ctx: int = 16384
    temperature: float = 0.8 #原来的值为0.9
    fbend: int = 0
    stype: str = "java"
    repeat_penalty:float = 1.3 #增强重复惩罚
    # repeat_last_n:int = 200 #扩大重复检测窗口
    # mirostat:int  = 2 #启用mirostat 2.0算法
    # mirostat_tau:float = 3.0 #增强逻辑连贯性
    # top_k:int = 50 #过滤低概率选项
    # top_p:float = 0.85 #平衡多样
    #seed:int = 12345 #确保结果可复现
    # num_predict:int = 1024 #避免冗余代码
    # mirostat_eta:float = 0.12 #精细调整反馈速度
class DiffRequest(BaseModel):
    diff_output_path: str
    base_path: str
    port: int = 8025
    model: str = "deepseek-coder:6.7b"
    num_ctx: int = 16384
    report_id: str = ""
    fbend:int = 0


class ReportRequest(BaseModel):
    report_id: str

# 获取源代码语言类型
def get_code_type(code_type: str):
    # Define a list of HTML code types
    html: list = ["html", "xhtml"]
    # Define a list of CSS code types
    css: list = ["css", "scss", "less",'sass']
    # Define a list of JavaScript code types
    javascript: list = ["js","mjs","cjs", "jsx"]
    typescript: list = ["ts", "tsx","d.ts"]
    #框架相关
    framework_vue: list = ["vue"]
    # Check if the source_code is of type HTML, CSS, or JavaScript
    if code_type in html:
        return "html"
    elif code_type in css:
        return "css"
    elif code_type in javascript:
        return "JavaScript"
    elif code_type in typescript:
        return "TypeScript"
    else:
        return "text"


# 文本生成接口
@app.post("/ollama/generate", summary="生成文本", description="使用 Ollama API 生成文本。")
async def generate_text(request: Request, data: GenerateRequest):
    global response, is_save
    # 默认data.fbend为0,代表后端,1代表前端
    if  not data.fbend:
        prompt = f"""
    角色： 你是一位java专家，请对以下代码进行代码检查,严格遵守以下要求：

    约束条件：
    1. 如果方法没有实体，则跳过该方法的检测，并输出：方法无实体，跳过检测
    2. 如果方法没有问题，则跳过该方法的检测，并输出：方法无问题，跳过检测
    3. 只关注bug和安全问题
    4. 忽略日志类型的问题
    5. 忽略注释：在代码中，请忽略以下几种注释：// 忽略此行 /* */ 中的代码 /** */ 中的代码
    6. 如果优化后的代码与源代码逻辑完全一致，避免将其作为改进建议输出。
    7. 源码中已经处理的问题，如空值检查已经在源码中处理过，则无需输出
    8. 如果优化后的代码已经在源代码中存在，则不需要输出

    变量说明：
    变量1为有问题的代码片段,变量2为优化建议的详细描述,例如：在获取参数之前，先进行非空检查，并确保其类型安全。变量3为优化后的代码片段,变量4为发现的问题梳理。

    报告输出示例：
    ### 审查报告
    #### 1. 空指针异常风险
       - **问题描述**：问题详细描述。
       - **问题代码片段**：
         ```java
          变量1
         ```
       - **优化建议**：变量2
       - **优化后的代码**：
         ```java
         变量3
         ```
    #### 2. 其他问题
       - **问题描述**：问题详细描述。
       - **问题代码片段**：
         ```java
          变量1
         ```
       - **优化建议**：变量2
       - **优化后的代码**：
         ```java
         变量3
         ```
    ......
    ### 总结
    本次代码审查发现以下问题：
    变量4
    通过实施上述优化建议，可以有效提高代码的健壮性和安全性。

    {data.code}
    """
    else:
        prompt= """
    - Role: 你是一位资深的Android研发专家，拥有丰富的Java和Android编程经验，对代码质量和安全性有深刻的理解。
    - Background: 用户需要对一段Java/Android代码进行CodeReview，重点关注空值判断、逻辑一致性、潜在的bug和安全问题，以确保代码的健壮性和安全性。
    - Profile: 你是一位经验丰富的Android开发专家，熟悉Android开发的最佳实践，能够从代码的可读性、性能、安全性和逻辑一致性等多个角度进行审查。
    - Skills: 你具备代码审查、优化、安全漏洞检测、逻辑一致性分析等关键能力，能够识别并解决代码中的潜在问题。
    - Goals: 对给出的代码进行全面的CodeReview，检查空值判断、逻辑一致性、潜在的bug和安全问题，并提供优化建议和优化后的代码片段。
    - Constrains:
      1. 对比分析问题代码与优化建议的差异度。
      2. 当优化内容与原始代码相似度>70%时，必须重构实现方案。
      3. 逻辑一致性检查：如果优化后的代码与源代码逻辑完全一致，请避免将其作为改进建议输出。
      4. 审查报告中，如果优化后的代码已经在源代码中存在，则不需要输出。
      5. 检查范围只包含bug和安全漏洞。
      6. 不检查没有方法体的方法。
      7. 日志类型的问题，不要输出到审查报告中。
      8. 忽略用//单行注释的代码行，如：//忽略此行。
      9. 忽略用/* */注释的代码行，如：/* */中的代码。
      10. 忽略用/** */注释的代码行，如：/** */中的代码。
      11. 忽略注释：在代码中，请忽略以下几种注释：//忽略此行/* */中的代码/** */中的代码。
    - OutputFormat: 按照以下格式进行报告的输出：
    ### 审查报告
    #### 1. 空指针异常风险
    ####     问题描述：问题详细描述。
    #####   问题代码片段：
         ```java
              变量1
         ```
     ####    优化建议：变量2
     #####  优化后的代码：
         ```java
         变量3
         ```
         **优化标记：** 标记出优化的具体代码行
    ......
    ### 总结
    本次代码审查发现以下问题：
    变量4
    通过实施上述优化建议，可以有效提高代码的健壮性和安全性。
    - Workflow:
      1. 分析代码片段，识别潜在的空值判断、逻辑一致性、潜在的bug和安全问题。
      2. 提出优化建议，确保优化后的代码与原始代码的差异度符合约束条件。
      3. 生成审查报告，按照指定格式输出问题描述、问题代码片段、优化建议和优化后的代码。
    - Examples:
      - 例子1：空指针异常风险
        问题代码片段：
        ```java
            if (data.getEquityTagsMap().bigVTag != null) {
                GoodsSimpleFlowData jrhSimpleFlowData = new GoodsSimpleFlowData();
                jrhSimpleFlowData.setType(NewSimpleFlowAdapter.DW_JRH_TYPE);
                jrhSimpleFlowData.setObj(data.getEquityTagsMap().bigVTag);
                tags.add(jrhSimpleFlowData);
            }
        ```
        优化建议：在访问`data.getEquityTagsMap()`之前，先进行非空检查。
        优化后的代码：
        ```java
        if (data != null && data.getEquityTagsMap() != null && data.getEquityTagsMap().bigVTag != null) {
            GoodsSimpleFlowData jrhSimpleFlowData = new GoodsSimpleFlowData();
            jrhSimpleFlowData.setType(NewSimpleFlowAdapter.DW_JRH_TYPE);
            jrhSimpleFlowData.setObj(data.getEquityTagsMap().bigVTag);
            tags.add(jrhSimpleFlowData);
        }
        ``` 
        **优化标记：** 在`if`条件中添加了`data != null && data.getEquityTagsMap() != null`的检查。
      - 例子2：逻辑优化
        问题代码片段：
        ```java
        if (data != null && data.getEquityTagsMap() != null) {
            if (data.getEquityTagsMap().getEasyHomeProtect() != null) {
                imageType = DwStringUtils.ImageType.JJB;
            } else if (data.getEquityTagsMap().getHourToReach() != null) {
                imageType = DwStringUtils.ImageType.XSD;
            } else if (data.getEquityTagsMap().getMeasuringRoom() != null) {
                imageType = DwStringUtils.ImageType.MFLF;
            }
        }
        ```
        优化建议：将`data.getEquityTagsMap()`的调用提取到一个变量中，避免重复调用。
        优化后的代码：
        ```java
        if (data != null) {
            EquityTagsMap tagsMap = data.getEquityTagsMap();
            if (tagsMap != null) {
                if (tagsMap.getEasyHomeProtect() != null) {
                    imageType = DwStringUtils.ImageType.JJB;
                } else if (tagsMap.getHourToReach() != null) {
                    imageType = DwStringUtils.ImageType.XSD;
                } else if (tagsMap.getMeasuringRoom() != null) {
                    imageType = DwStringUtils.ImageType.MFLF;
                }
            }
        }
        ```
        **优化标记：** 提取`data.getEquityTagsMap()`到变量`tagsMap`中，避免重复调用。
      - 例子3：资源泄漏问题
        问题代码片段：
        ```java
        UIHelper.getInstance().setImgShop(data != null ? data.getLogo_key() : null, iv_cover);
        ```
        优化建议：确保在调用`setImgShop`时，`iv_cover`不为`null`，避免潜在的空指针异常。
        优化后的代码：
        ```java
        if (iv_cover != null) {
            UIHelper.getInstance().setImgShop(data != null ? data.getLogo_key() : null, iv_cover);
        }
        ```
        **优化标记：** 添加了`if (iv_cover != null)`的检查。
      - 例子4：潜在的逻辑问题
        问题代码片段：
        ```java
            if (data != null && data.getGoodsVoList() != null && data.getGoodsVoList().size() >= 3) {
                rv_shopmall_goods.setVisibility(View.VISIBLE);
                rv_shopmall_goods.update(data.getGoodsVoList().size() > 3 ? data.getGoodsVoList().subList(0, 3) : data.getGoodsVoList());
            } else {
                rv_shopmall_goods.setVisibility(View.GONE);
            }
        ```
        优化建议：在调用`subList`之前，确保列表的大小足够，避免`IndexOutOfBoundsException`。
        优化后的代码：
        ```java
        if (data != null && data.getGoodsVoList() != null) {
            if (data.getGoodsVoList().size() >= 3) {
                rv_shopmall_goods.setVisibility(View.VISIBLE);
                rv_shopmall_goods.update(data.getGoodsVoList().subList(0, Math.min(3, data.getGoodsVoList().size())));
            } else {
                rv_shopmall_goods.setVisibility(View.GONE);
            }
        }
        ```
        **优化标记：** 在`subList`调用中添加了`Math.min(3, data.getGoodsVoList().size())`，确保不会超出列表范围。

    """ + data.code
    try:
        flag = True
        while flag:
            response = client.generate(model=data.model, prompt=prompt,keep_alive="1h",
                                       options={'num_ctx': data.num_ctx, 'temperature': data.temperature,'repeat_penalty': data.repeat_penalty
                                                })

            # response = client.generate(model=data.model, prompt=prompt,keep_alive="1h",
            #                            options={'num_ctx': data.num_ctx})
            content = response["response"]
            number = content.count("改进后的代码示例")
            number_zongjie = content.count("总结")
            if number < 2 or number_zongjie ==1:
               flag = False
            if "方法无实体" in content or "方法无问题" in content:
                is_save = 0
            else:
                is_save = 1
        return JSONResponse({"status":200,"content":response.response.replace('<think>\n\n</think>',''),"is_save":is_save})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 获取模型列表
@app.get("/ollama/models", summary="获取模型列表", description="获取所有可用的模型")
async def list_models(request: Request):
    # url = f"{OLLAMA_API_URL}/v1/models"
    # headers = {}
    try:
        response = client.list()
        return response.models
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#获取增量代码覆盖率方法名
@app.post("/codediff/getchangemethod")
def get_change_method_api(request: DiffRequest):
    diff_output_path = request.diff_output_path
    base_path = request.base_path
    port = request.port
    model = request.model
    num_ctx = request.num_ctx
    report_id = request.report_id
    fbend = request.fbend
    # 获取增量代码覆盖率方法名
    modified_methods_by_file = get_change_method_view.get_change_method(diff_output_path,base_path,port,model,num_ctx,report_id,fbend=fbend)
    return modified_methods_by_file

@app.post("/codediff/fe")
def get_change_method_api(request: DiffRequest):
    diff_output_path = request.diff_output_path
    base_path = request.base_path
    port = request.port
    model = request.model
    num_ctx = request.num_ctx
    report_id = request.report_id
    # 获取增量代码覆盖率方法名
    modified_methods_by_file = fe_view.fe(diff_output_path,base_path,port,model,num_ctx,report_id)
    return modified_methods_by_file

@app.post("/codediff/readreport")
def read_report_api(request: ReportRequest):
    report_id = request.report_id
    # 获取增量代码覆盖率方法名
    report = read_report_view.read_report(report_id)
    return report

@app.post("/codediff/reporttime")
def report_time_api(request: ReportRequest):
    report_id = request.report_id
    # 获取增量代码覆盖率方法名
    report = read_report_view.report_time(report_id)
    return report

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8025)