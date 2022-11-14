import re
from tkinter import E
from typing import List
import emoji
import aiohttp
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

API = "https://www.gstatic.com/android/keyboard/emojikitchen/"


emojimix=on_regex(
    rf"^\s*(?P<code1>{pattern})\s*(?P<code2>{pattern})\s*$",
)
@emojimix.handle()
async def mix(event:Event,msg:dict=RegexDict()):
    _,group,qq=str(event.get_session_id()).split("_")
    if isInGroup(group,"emoji_mix")==0:
        await emojimix.finish(None)
    emoji_code1=msg["code1"]
    emoji_code2=msg["code2"]
    result=await mix_emoji(emoji_code1,emoji_code2)
    if isinstance(result,str):
        await emojimix.finish(result)
    else :
        await emojimix.finish(MessageSegment.image(result))

def emoji_code(emoji):
    return "-".join(map(lambda c:f"u{c:x}",emoji))#

def create_url(date:str,emoji1,emoji2):
    u1=emoji_code(emoji1)
    u2=emoji_code(emoji2)
    return f"{API}{date}/{u1}/{u1}_{u2}.png"

def find_emoji(emoji_code:str):
    emoji_num=ord(emoji_code)#对于一个字符串返回unicode码值
    for e in emojis:
        if emoji_num in e:
            return e
    return None

async def mix_emoji(emoji_code1:str,emoji_code2:str):
    logger.debug("enter mix emoji function")
    emoji1=find_emoji(emoji_code1)
    emoji2=find_emoji(emoji_code2)
    if not emoji1 or not emoji2:
        return f"不支持该emoji组合，我的库没有其中的某个emoji：{emoji_code1}{emoji_code2}"#本地data没有其中的一个emoji
    urls: List[str]=[]#初始化为str列表
#遍历所有日期和mix的不同前后顺序的可能
    for date in dates:
        urls.append(create_url(date,emoji1,emoji2))
        urls.append(create_url(date,emoji2,emoji1))
    try:
        async with aiohttp.ClientSession() as session:  # type: ignore
            logger.warning("start request")
            for url in urls:
                logger.error(f"{url}")
                async with session.get(url=url,proxy="http://localhost:7890") as resp:
                    r=await resp.read()
                    if resp.status == 200:
                        return r
            return f"出错了，该emoji组合暂无合成结果：{emoji_code1}{emoji_code2}"
    except Exception as e:
        logger.warning(traceback.format_exc())
        return "下载出错，请稍后再试"