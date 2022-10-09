"""
输出第几个睡觉的
"""


import datetime
import random 
from pymysql import *
from nonebot.plugin import on_keyword
from nonebot.plugin import on_command
from nonebot.plugin.on import on_fullmatch
from nonebot.adapters.onebot.v11 import Bot,Event
from nonebot.adapters.onebot.v11.message import Message
from .managementModule.isInGroup import isInGroup

morning=on_fullmatch(msg=["晚安","呼呼","晚安捏","晚安大家","おやすみ"])
@morning.handle()
async def morning_handle(bot:Bot,event:Event):
    _,group,qq=str(event.get_session_id()).split("_")
    if isInGroup(group,"night")==0:
        await morning.finish(None)
    msg=getmsg(qq,group)
    await morning.send(msg)


def getmsg(user_id:int,group_id:int):
    """
    我统计当天晚上8点到第二天凌晨4点间的所有已睡觉的人
    存在表中的值应当被统计的，和当天时间关系分两种 
    1.如果现在是0-4点
        和昨天晚上8点时间相差不超过28800s
    2.如果现在是20-24点
        跟今天20点时间相差不超过14400s
    """
    i=datetime.datetime.now()
    daynow=i.day
    hournow=i.hour
    minutenow=f'{i.minute}' if i.minute>=10 else f'0{i.minute}'
    secondnow=f'{i.second}' if i.second>=10 else f'0{i.second}'
    if hournow>4 and hournow<20 :
        return f'现在还没到晚上呢'
    datezero=datetime.datetime(i.year,i.month,i.day,0,0,0)
    dateyest=datezero+datetime.timedelta(hours=-4)
    dateEight=datezero+datetime.timedelta(hours=20)

    conn=connect(host="localhost",user="root",password="allforqqbot",database="qqbot",port=3306,charset="UTF8")
    cur=conn.cursor()
    sql=f"select * from data_night where groupnum=%s"
    tmp=cur.execute(sql,[group_id])
    result=cur.fetchall()

    tnd=1
    for raws in result:
        dateraw:datetime.datetime=raws[2]
        qq:int=raws[1]
        minutepre=f'{dateraw.minute}' if dateraw.minute>=10 else f'0{dateraw.minute}'
        secondpre=f'{dateraw.second}' if dateraw.second>=10 else f'0{dateraw.second}'
        if hournow<=4:
            if (dateraw-dateyest).seconds<=28800 and (dateraw-dateyest).days==0:
                if int(user_id)==qq:
                    cur.close()
                    conn.close()
                    return f'晚安mua~，你是群里第{tnd}个睡觉的人，睡觉时间是{dateraw.hour}:{minutepre}:{secondpre}'
                else :
                    tnd=tnd+1
        elif hournow>=20:
#            print(f"dateraw{dateraw} dateEight{dateEight} second{(dateraw-dateEight).seconds}")
            if (dateraw-dateEight).seconds<=14400 and (dateraw-dateEight).days==0:
                if int(user_id)==qq:
                    cur.close()
                    conn.close()
                    return f'晚安mua~，你是群里第{tnd}个睡觉的人，睡觉时间是{dateraw.hour}:{minutepre}:{secondpre}'
                else :
                    tnd=tnd+1
    sql=f"insert into data_night (groupnum,qqnum,time) values(%s,%s,now())"
    cur.execute(sql,[group_id,user_id])
    conn.commit()
    cur.close()
    conn.close()
    return f'晚安mua~，现在是{hournow}:{minutenow}:{secondnow}，你是群里第{tnd}个睡觉的人哦'
