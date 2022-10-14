import os
import random
from PIL import Image
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot import get_bots
from nonebot.adapters.onebot.v11 import Event
from nonebot.adapters.onebot.v11.message import MessageSegment
from .managementModule.isInGroup import isInGroup
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
    if isInGroup(group,"pixiv_from_library")==0:
        await pixiv_from_lib.finish(None)
    try :
        await pixiv_from_lib.send(MessageSegment.image(filename+f"/{mylib[image_id]}"))
    except :
        
        await pixiv_from_lib.send(MessageSegment.text(f"图片发送失败，可能因为被吞{mylib[image_id]}\n稍后可能发一张处理过的图"))
        file_path=os.getcwd()
        file_path=file_path.replace("\\","/")+"/mylibrary"
        img=Image.open(file_path+f"/{mylib[image_id]}")
        h=img.height
        w=img.width
        img.resize(size=(int(h*0.9),int(w*0.9)))
        img.save(file_path+f"/tmp.png")
        await pixiv_from_lib.send(MessageSegment.image(file_path+f"/tmp.png"))
