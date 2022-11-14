import os
import random
from PIL import Image
from loguru import logger
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot import get_bots
from nonebot.adapters.onebot.v11 import Event
from nonebot.adapters.onebot.v11.message import MessageSegment
from .managementModule.isInGroup import isInGroup
filename=os.getcwd()#调用目录在第一层awesomebot
mylib=os.listdir(filename+"\\awesomebot\\plugins\\localResource\\capoo")
filename="file:///"+filename+"\\awesomebot\\plugins\\localResource\\capoo"
sz=len(mylib)


capoo=on_command("猫猫虫",aliases={"蓝皮猪","capoo"})
@capoo.handle()
async def work(event:Event,matcher:Matcher):
    bot,=get_bots().values()
    image_id=random.randint(0,sz-1)
    _,group,qq=str(event.get_session_id()).split("_")
    if isInGroup(group,"capoo")==0:
        await capoo.finish(None)
    logger.info(f"{filename}"+f"\{mylib[image_id]}")
    await capoo.send(MessageSegment.image(filename+f"\{mylib[image_id]}"))
