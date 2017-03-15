# -*- coding: utf-8 -*-
from wechat_sdk import WechatConf

replyConfig = {
    "welcome": "你好，欢迎关注SPIKE微信端。",
    "morning":"早上好",
    "noon":"中午好",
    "afternoon":"下午好",
    "evening":"晚上好",
    "exist" :   "-您要问的问题是不是这样滴-",
    "interesting":"-您还可能对这些问题感兴趣-",
    "greeting":"欢迎咨询关于怀孕生孩子，新生儿等相关话题，请向我提问吧。",
    "not_found": "抱歉，未找到合适答案 ，目前回答只针对怀孕生孩子科普文章，请确认所提问题属于该范围。或是尝试提问其它问题？"
}

# # my config
# wechatConfig = WechatConf(
#     token='duantao',
#     appid='wx0ce3a1537c2c29c4',
#     appsecret='d4624c36b6795d1d99dcf0547af5443d',
#     encrypt_mode='normal',  # 可选项：normal/compatible/safe，分别对应于 明文/兼容/安全 模式
# )

# 推健config
wechatConfig = WechatConf(
    token='duantao',
    appid='wx2549e45e0dcbae50',
    appsecret='63526de128da8534ac628a1f3bb790c0',
    encrypt_mode='normal',  # 可选项：normal/compatible/safe，分别对应于 明文/兼容/安全 模式
    encoding_aes_key='Q55N2Q6ld30nCf2aOtyLEiDVAy1HTwdQ22dESUvJ3vQ'  # 如果传入此值则必须保证同时传入 token, appid
)