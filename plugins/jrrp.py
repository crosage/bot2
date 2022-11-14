import datetime 
import random
from nonebot.plugin import on_keyword
from nonebot.adapters.onebot.v11 import Bot,Event
from nonebot.adapters.onebot.v11.message import Message
from .managementModule.isInGroup import isInGroup
from nonebot.log import logger

jrrp=on_keyword(['jrrp','今日人品'],priority=20)
@jrrp.handle()
async def jrrp_handle(bot:Bot,event:Event):
    _,group,qq=str(event.get_session_id()).split("_")
    t=await ha()
    logger.info(t)
    if isInGroup(group,"jrrp")==0:
        await jrrp.finish(None)
    user_id=event.get_user_id()
    rp=getit(user_id)
    msg=Message(f'[CQ:at,qq={user_id}]'+rp)
    await jrrp.finish(msg)

async def ha():
    return 1
def getit(user_id):
    i=datetime.datetime.now()
    random.seed(user_id*i.day*i.month)
    x=random.random()
    if x<0.3 :
        y=random.randint(1,40)
        if y<15:
            return f'你今天的人品是{y}(寄)' 
        else :
            return f'你今天的人品是{y}(末吉)' 
    else :
        y=random.randint(40,100)
        if y>=40 and y<=60 :
            return f'你今天的人品是{y}(小吉)'
        elif y>60 and y<=80 :
            return  f'你今天的人品是{y}(吉)'
        else :
            return  f'你今天的人品是{y}(大吉)'