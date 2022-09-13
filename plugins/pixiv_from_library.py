import os
import random
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot import get_bots
from nonebot.adapters.onebot.v11 import Event
from nonebot.adapters.onebot.v11.message import MessageSegment
filename=os.getcwd()#调用目录在第一层awesomebot
mylib=os.listdir(filename+"\mylibrary")
filename="file:///"+filename.replace("\\","/")+"/mylibrary"
sz=len(mylib)


pixiv_from_lib=on_command("来一张",aliases={"随机萌图","色图","涩图","不色图","来张"})
@pixiv_from_lib.handle()
async def work(event:Event,matcher:Matcher):
    bot,=get_bots().values()
    image_id=random.randint(0,sz-1)
    _,group,qq=str(event.get_session_id()).split("_")
    await pixiv_from_lib.send(MessageSegment.image(filename+f"/{mylib[image_id]}"))