import os
from PIL import Image
from nonebot.adapters.onebot.v11 import Bot
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot import get_bots
from nonebot.adapters.onebot.v11 import Event
from nonebot.adapters.onebot.v11.message import MessageSegment
from .managementModule.isInGroup import isInGroup
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.message import Message
import datetime
cnt=0
otto=on_command("电棍",aliases={"活字印刷"})
@otto.handle()
async def otto_handle(bot:Bot,event:Event,args:Message=CommandArg()):
    text=str(args)
    _,group,qq=str(event.get_session_id()).split("_")
    if isInGroup(group,"huoziyinshua")==0:
        await otto.finish(None)
    # text.replace("\n","")
    # text.replace("\r","")
    # text.replace(" ","")
    global cnt
    os.chdir("D:\\bot\\HuoZiYinShuasrc\\HuoZiYinShua\\")
    logger.info(text)
    cnt=cnt+1
    os.system(f"python HZYS.py -t {text} -y -o ./{cnt}.wav")
    # logger.debug(datetime.datetime.microsecond())
    await otto.send(MessageSegment.record(f"file:///D:/bot/HuoZiYinShuasrc/HuoZiYinShua/{cnt}.wav"))
    os.chdir("D:\\bot\\awesomebot")
