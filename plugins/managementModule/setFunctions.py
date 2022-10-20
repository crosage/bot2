from pymysql import *
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot,Event
from nonebot.adapters import Message
from nonebot.matcher import Matcher #matcher 匹配器
from nonebot.params import Arg,CommandArg,ArgPlainText #param 参数，对参数的操作
from nonebot.log import logger

setGroup=on_command("add",aliases={"添加"},priority=10,block=True)
@setGroup.handle()
async def setGroup_handle(matcher:Matcher,event:Event,args:Message=CommandArg()):
    text=args.extract_plain_text()
    _,group,qq=str(event.get_session_id()).split("_")
    if qq!=str(2051252420):
       await setGroup.finish()
    if text :
        matcher.set_arg("functions",args)


@setGroup.got("functions",prompt="你想添加什么功能？")#设置参数functions 用Message存储Message类型的functions 用str存储字符串类型的name
async def handle_functions(event:Event,functions:Message=Arg(),name: str = ArgPlainText("functions")):
    conn=connect(host="localhost",port=3306,user="root",password="allforqqbot",database='qqbot',charset='UTF8')
    cur=conn.cursor()
    _,group,qq=str(event.get_session_id()).split("_")
    sql=f"select * from name_of_functions where name=%s"
    tmp=cur.execute(sql,[name])
    if tmp==0:
        await setGroup.finish(None)
    sql=f"select * from group_function_list where group_num=%s and functions=%s"
    tmp=cur.execute(sql,[group,name])
    if tmp==0:
        sql=f"insert into group_function_list (id,group_num,functions) values(0,%s,%s)"
        tmp=cur.execute(sql,[group,name])
        conn.commit()
        cur.close()
        conn.close()
        await setGroup.finish("添加成功")        
    else :
        conn.rollback()
        cur.close()
        conn.close()
        await setGroup.finish("该功能被重复添加")