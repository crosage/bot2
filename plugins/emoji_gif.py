import re
from tkinter import E
from typing import List
import emoji
import httpx
import traceback
from nonebot import on_regex,get_driver
from nonebot.log import logger
from nonebot.params import RegexDict #正则表达式匹配emoji参数
from nonebot.adapters.onebot.v11 import MessageSegment,Event
from .emoji_data import emojis,dates
from .managementModule.isInGroup import isInGroup

emoji_match=filter(lambda e:len(e)==1,emoji.EMOJI_DATA.keys())
pattern="("+"|".join(re.escape(e) for e in emoji_match)+")"

API = "https://www.emojiall.com/images/60/telegram/"

emojigif=on_regex(
    rf"^\s*(?P<code1>{pattern})\s*gif$",
)
#emojicode是unicode码格式 
@emojigif.handle()
async def mix(event:Event,msg:dict=RegexDict()):
    _,group,qq=str(event.get_session_id()).split("_")
    if isInGroup(group,"emoji_gif")==0:
        await emojigif.finish(None)
    emoji_code1=msg["code1"]
    result=await gif_emoji(emoji_code1)
    if isinstance(result,str):
        await emojigif.finish(result)
    else :
        await emojigif.finish(MessageSegment.image(result))

def emoji_code(emoji):
    return "-".join(map(lambda c:f"{c:x}",emoji))#

def create_url(emoji1):
    u1=emoji_code(emoji1)
    return f"{API}/{u1}.gif"

def find_emoji(emoji_code:str):
    emoji_num=ord(emoji_code)#对于一个字符串返回unicode码值
    for e in emojis:
        if emoji_num in e:
            return e
    return None

async def gif_emoji(emoji_code1:str):
#emoji是
    emoji1=find_emoji(emoji_code1)
    if not emoji1:
        return f"不支持该emoji{emoji_code1}"#本地data没有其中的一个emoji
    url:str=""#初始化为str列表
#遍历所有日期和mix的不同前后顺序的可能
    url=create_url(emoji1)
    try:#client在多次访问时保持原有TCP连接
        async with httpx.AsyncClient(timeout=20) as client:  # type: ignore
            resp = await client.get(url)
            if resp.status_code == 200:
                return resp.content
            return f"该emoji暂无动图：{emoji_code1}"
    except:
        logger.warning(traceback.format_exc())
        return "下载出错，请稍后再试"