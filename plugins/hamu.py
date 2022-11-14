import datetime 
import random
from nonebot.plugin import on_keyword
from nonebot.adapters.onebot.v11 import Bot,Event
from nonebot.adapters.onebot.v11.message import Message
from .managementModule.isInGroup import isInGroup
from nonebot.plugin.on import on_fullmatch
from nonebot.adapters.onebot.v11.message import Message,MessageSegment
from nonebot.log import logger
hamu=on_fullmatch(['哈姆？哈姆！',"哈姆"],priority=20)
import os
@hamu.handle()
async def hamu_handle(bot:Bot,event:Event):
    _,group,qq=str(event.get_session_id()).split("_")
    if isInGroup(group,"hamu")==0:
        await hamu.finish(None)
    filename=os.getcwd()+"\\awesomebot\\plugins\\hamu.gif"
    await hamu.send("哈姆，哈姆，哈姆")
    await hamu.send("哈姆的哈的贝哈姆哈姆的的哈贝贝，哈姆的哈的贝哈姆哈姆的哈贝贝")
    await hamu.send("哈姆，哈姆")
    await hamu.send("古莫德那德米列洛玛，古莫德那德米列洛玛，阿珂么德哈马迪，阿珂么德哈马迪")
    logger.debug("file:///"+filename)
    await hamu.send(MessageSegment.image("file:///"+filename))