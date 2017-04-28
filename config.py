# -*- coding: utf-8 -*-
from wechat_sdk import WechatConf

replyConfig = {
    "welcome": "您好！我是段涛大夫的机器人小助手 。如果有怀孕期间的困惑想提问，您就找对人啦！希望能陪您顺利快乐地渡过一段幸福孕期时光",
    "welcome2": "只需要点击屏幕左下角的键盘，切换到打字模式，就可以输入您的问题。我会基于段涛大夫《怀孕生孩子那些事》系列科普文章来回答。",
    "morning":"早上好",
    "noon":"中午好",
    "afternoon":"下午好",
    "evening":"晚上好",
    "exist" :   "-您要问的问题是不是这样滴-",
    "interesting":"-您还可能对这些问题感兴趣-",
    "greeting":"欢迎咨询关于怀孕生孩子，新生儿等相关话题，请向我提问吧。",
    "not_found": "您的问题暂时没有答案，建议咨询妇产科医生专家，或者尝试提其它怀孕生孩子的问题。我也会虚心去请教段大夫滴～",
    "nothanks":"不用客气！"
}

# 段涛config
# wechatConfig = WechatConf(
#     token='0d5965e9b5862fe57c2d',
#     appid='wxcb0743a6ac990cce',
#     appsecret='e5c828a7c309c8338e61f26e583fb5bf',
#     encrypt_mode='normal',  # 可选项：normal/compatible/safe，分别对应于 明文/兼容/安全 模式
#     encoding_aes_key='sJpCqbdZJOFhn9uHe8gEdA5tQJuIKmQ8vpHrzsNsoci'  # 如果传入此值则必须保证同时传入 token, appid
# )

# my config
wechatConfig = WechatConf(
    token='0d5965e9b5862fe57c2d',
    appid='wx0ce3a1537c2c29c4',
    appsecret='d4624c36b6795d1d99dcf0547af5443d',
    encrypt_mode='normal',  # 可选项：normal/compatible/safe，分别对应于 明文/兼容/安全 模式
)

# 推健config
# wechatConfig = WechatConf(
#     token='duantao',
#     appid='wx2549e45e0dcbae50',
#     appsecret='63526de128da8534ac628a1f3bb790c0',
#     encrypt_mode='normal',  # 可选项：normal/compatible/safe，分别对应于 明文/兼容/安全 模式
#     encoding_aes_key='Q55N2Q6ld30nCf2aOtyLEiDVAy1HTwdQ22dESUvJ3vQ'  # 如果传入此值则必须保证同时传入 token, appid
# )


