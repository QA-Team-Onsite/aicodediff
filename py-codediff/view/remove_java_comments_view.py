#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author: gaobo
@Project: py-codediff
@file: remove_java_comments_view.py
@Date: 2025/5/9 11:25
@Description: 
"""
import re

def remove_java_comments(code):
    # 去掉 // 开头的单行注释 /** ... */ 或 /* ... */ 注释
    pattern = r'''
        (//.*?$)                        # 捕获以 // 开头的整行注释
      | (/\*\*.*?\*/)                  # 捕获 Javadoc 注释 /** ... */
      | (/\*.*?\*/)                    # 捕获普通多行注释 /* ... */
    '''
    cleaned_code = re.sub(pattern, '', code, flags=re.MULTILINE | re.DOTALL | re.VERBOSE)
    cleaned_code = '\n'.join(line for line in cleaned_code.splitlines() if line.strip())

    return cleaned_code


if __name__ == '__main__':
    # 用法
    java_code = """/**
     * 判断时间区间是否符合--返回不符合list
     */
    @Override
     // 已删除城市 不处理城市下卖场
         /*  这里直接查询有 客服，导购，店长角色的用户，但是线上基本上人员都有  所有都把人员注册进去吧
            select id,phone,phone_encrypt  from easy_merchant_user emu  where is_deleted =0 and status=0 and id>0
    and exists (select emur.id  from easy_merchant_user_role emur where user_id =emu.user_id and is_deleted =0 and is_enable =1 and emur.role_id in(836262830603898880,836262690300235776,597944714915033088,840192499208294400,840304177153445888,597946542239068160) limit 1)
    order by id limit 10
            * */
    public List<CampaignTopicVo> judgeTopicDate(TopicDateReqData reqData) {
        log.info("judgeTopicDate param : {}", JSON.toJSONString(reqData));
        List<CampaignTopicVo> topicList = reqData.getTopicList();
        if (Objects.isNull(reqData.getStartDate()) || Objects.isNull(reqData.getEndDate())) {
            return topicList;
        }
        Iterator<CampaignTopicVo> iterator = topicList.iterator();
        while (iterator.hasNext()) {
            CampaignTopicVo campaignTopicVo = iterator.next();
            List<TopicMarketRelPO> topicMarketRelPOS = topicMarketRelManager.selectByParam(campaignTopicVo.getTopicCode(), reqData.getMarketId());
            if (CollectionUtils.isEmpty(topicMarketRelPOS)) {
                log.info("judgeTopicDate未查到数据,topicCode:" + campaignTopicVo.getTopicCode());
                continue;
            }
            for (TopicMarketRelPO topicMarketRelPO : topicMarketRelPOS) {
                String dateStr = DateUtils.format(topicMarketRelPO.getEndDate(), "yyyy-MM-dd") + " 23:59:59";
                Date endTime = DateUtils.parse2Date(dateStr, "yyyy-MM-dd HH:mm:ss");
                if ((reqData.getStartDate().getTime() <= topicMarketRelPO.getStartDate().getTime() && reqData.getEndDate().getTime() > topicMarketRelPO.getStartDate().getTime()) || (reqData.getStartDate().getTime() >= topicMarketRelPO.getStartDate().getTime() && reqData.getStartDate().getTime() < Objects.requireNonNull(endTime).getTime())) {
                    iterator.remove();
                    break;
                }
            }
        }
        return topicList;
    } """
    cleaned_code = remove_java_comments(java_code)
    print(cleaned_code)
