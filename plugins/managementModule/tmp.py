from pymysql import *
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot,Event
from nonebot.matcher import Matcher
#获取参数 对参数操作
from nonebot.params import Arg,CommandArg,ArgPlainText
from PIL import ImageDraw
import os

queryGroup=on_command("功能",aliases={"功能查询"},priority=3)
@queryGroup.handle()
async def queryGroup_handle(matcher:Matcher,state:T_State,event:Event):
    conn=connect(host="localhost",user="root",password="allforqqbot",database="qqbot",port=3306,charset="UTF8")
    cur=conn.cursor()
    _,group,qq=str(event.get_session_id()).split("_")


    sql=f"select name from name_of_functions"
    tmp=cur.execute(sql)
    result=cur.fetchall()
    msg="yz有以下功能\n"
    cnt=0
    for raw in result :
        cnt=cnt+1
        msg=msg+f"{cnt}："+raw[0]+"\n"

    sql=f"select functions from group_function_list where group_num=%s"
    tmp=cur.execute(sql,group)
    result=cur.fetchall()
    msg=msg+"该群已启用的功能有\n"
    cnt=0
    for raw in result:
        cnt=cnt+1
        msg=msg+f"{cnt}："+raw[0]+"\n"
    cur.close()
    conn.close()
    await queryGroup.send(msg)