from fileinput import filename
from pymysql import *
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot,Event
from nonebot.adapters.onebot.v11.message import Message,MessageSegment
from nonebot.adapters import Message
from nonebot.matcher import Matcher #matcher 匹配器
from nonebot.params import Arg,CommandArg,ArgPlainText #param 参数，对参数的操作
from PIL import Image
from nonebot.params import ArgStr
from .managementModule.uitls import messageTools
from .managementModule.isInGroup import isInGroup
from urllib.request import urlretrieve
import os

petpet=on_command("petpet",aliases={"摸摸"})
@petpet.handle()
async def work(event:Event,matcher:Matcher,state:T_State,cmd_message:Message=CommandArg()):
    _,group,qq=str(event.get_session_id()).split("_")
    if isInGroup(group,"petpet")==0:
        await petpet.finish(None)
    at_list=messageTools(message=cmd_message).get_all_at_qq()
    print(f"{at_list}")
    if at_list:
        avatar_url=messageTools.get_user_head_img_url(at_list[-1])
#        state.update({"source_image":avatar_url})
        
        matcher.set_arg("source_image",cmd_message)

@petpet.got("source_image",prompt="你想要摸摸谁呢")
async def handle_sticker(matcher:Matcher,source_image:Message=Arg(),name:str=ArgStr("source_image")):
    at_list=messageTools(message=source_image).get_all_at_qq()
    if at_list:
        avatar_url=messageTools.get_user_head_img_url(at_list[-1])
        await download_source_image(avatar_url)
    else :
        await petpet.finish("source_image",f"你好像没有@其他人")
    resize_paste_loc:list[tuple[tuple[int,int],tuple[int,int]]]=[
            ((95, 95), (12, 15)),
            ((97, 80), (11, 30)),
            ((99, 70), (10, 40)),
            ((97, 75), (11, 35)),
            ((96, 90), (11, 20))
    ]
    frame_list=[]
    fileurl=os.getcwd()+"\\awesomebot\\plugins\\imagetmp\\imagetmp.png"
    frameurl=os.getcwd()+"\\awesomebot\\plugins\\localResource\\petpet"
    saveurl=frameurl+"\\tmp.gif"
    image=Image.open(fileurl)
    image=image.resize((112,112))
    blank=Image.new(mode="RGBA",size=(112,112),color=(255,255,255))
    r=112/2
    loadimage=image.load()
    blankimage=blank.load()
    for i in range(112):
        for j in range(112):
            lx=abs(i-r)
            rx=abs(j-r)
            if lx*lx+rx*rx > r*r:
                loadimage[i,j]=blankimage[i,j]
    for frame_index in range(5):
        background=Image.new(mode='RGBA',size=(112,112),color=(255,255,255))
        print(frameurl+f"\\template_p{frame_index}.png")
        frame=Image.open(frameurl+f"\\template_p{frame_index}.png")
        background.paste(image.resize(resize_paste_loc[frame_index][0]),resize_paste_loc[frame_index][1])
        background.paste(frame,(0,0),mask=frame)
        frame_list.append(background)
        background.save(frameurl+f"\\tmp{frame_index}.png")
    frame_list[0].save(saveurl,save_all=True,append_images=frame_list,duration=0.02)
    try:
        await petpet.send(MessageSegment.image("file:///"+saveurl.replace("\\","/")))
    except :
        await petpet.finish("你的图像被腾讯识别成R18了（哭")

async def download_source_image(url:str):
    filename=os.getcwd()+"\\awesomebot\\plugins\\imagetmp\\imagetmp.png"
    urlretrieve(url,filename) 