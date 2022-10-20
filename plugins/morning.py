import datetime
import random
from re import fullmatch
from socket import MsgFlag 
from pymysql import *
from nonebot.matcher import Matcher
from nonebot.plugin import on_keyword
from nonebot.plugin import on_command
from nonebot.plugin.on import on_fullmatch
from nonebot.adapters.onebot.v11 import Bot,Event
from nonebot.adapters.onebot.v11.message import Message
from .managementModule.isInGroup import isInGroup
greetings=["早安","早上好","早哦"]

morning=on_fullmatch(msg=["早上好","早","早安","早哦","早捏","おはよ"])
@morning.handle()
async def morning_handle(bot:Bot,event:Event):
    _,group,qq=str(event.get_session_id()).split("_")
#    print(str(event.get_session_id()).split("_"))
    if isInGroup(group,"morning")==0:
        await morning.finish(None)
    msg=getmsg(qq,group)
    await morning.send(msg)


def getmsg(user_id:int,group_id:int):
    i=datetime.datetime.now()
    daynow=i.day
    hournow=i.hour
    minutenow=f'{i.minute}' if i.minute>=10 else f'0{i.minute}'
    secondnow=f'{i.second}' if i.second>=10 else f'0{i.second}'
    
    conn=connect(host="localhost",user="root",password="allforqqbot",database="qqbot",port=3306,charset="UTF8")
    cur=conn.cursor()
    sql=f"select * from data_morning where groupnum=%s"
    tmp=cur.execute(sql,[group_id])
    result=cur.fetchall()

    tnd=1
    for raws in result:
        dateraw:datetime.datetime=raws[2]
        qq:int=raws[1]
        minutepre=f'{dateraw.minute}' if dateraw.minute>=10 else f'0{dateraw.minute}'
        secondpre=f'{dateraw.second}' if dateraw.second>=10 else f'0{dateraw.second}'
#        print(f"{daynow} {dateraw.day} {qq} {user_id} {type(group_id)} )")
        if dateraw.day==daynow:
#            print(f"{user_id} {qq} {type(user_id)} {type(qq)}")
            if int(user_id)==qq:
                return f'{greetings[random.randint(0,2)]}，你是群里第{tnd}个起床的人，起床时间是{dateraw.hour}:{minutepre}:{secondpre}'
            else :
                tnd=tnd+1
#        print(dateraw)
    sql=f"insert into data_morning (groupnum,qqnum,time) values(%s,%s,now())"
    cur.execute(sql,[group_id,user_id])
    conn.commit()
    cur.close()
    conn.close()
    return f'{greetings[random.randint(0,2)]}，现在是{hournow}:{minutenow}:{secondnow}，你是群里第{tnd}个起床的人哦'
#    cur.execute(f"select * from morning where qqnum={user_id}")
