from pymysql import *
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot,Event
from nonebot.adapters import Message
from nonebot.matcher import Matcher #matcher 匹配器
from nonebot.params import Arg,CommandArg,ArgPlainText #param 参数，对参数的操作


delFunctions=on_command("del",aliases={"删除"},priority=1,block=True)
@delFunctions.handle()
async def delFunctions_handle(matcher:Matcher,event:Event,args:Message=CommandArg()):
    text=args.extract_plain_text()
    if text :
        matcher.set_arg("functions",args)


@delFunctions.got("functions",prompt="你要删除哪个功能？")#设置参数functions 用Message存储Message类型的functions 用str存储字符串类型的name
async def handle_del(event:Event,functions:Message=Arg(),name: str = ArgPlainText("functions")):
    conn=connect(host="localhost",port=3306,user="root",password="allforqqbot",database='qqbot',charset='UTF8')
    cur=conn.cursor()
    _,group,qq=str(event.get_session_id()).split("_")
    sql=f"select * from group_function_list where group_num=%s and functions=%s"
    tmp=cur.execute(sql,[group,name])
    if tmp==0:
        sql=f"delete from group_function_list where group_num=%s and functions=%s"
        tmp=cur.execute(sql,[group,name])
        conn.commit()
        cur.close()
        conn.close()
        await delFunctions.finish("删除成功")
    else :
        conn.rollback()
        cur.close()
        conn.close()
        await delFunctions.finish("删除失败,该群好像没有这个功能")