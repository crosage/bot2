from pymysql import *
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot,Event
from nonebot.matcher import Matcher
from PIL import Image,ImageDraw,ImageFont
#获取参数 对参数操作
from nonebot.params import Arg,CommandArg,ArgPlainText
from PIL import ImageDraw
import os

queryGroup=on_command("功能",aliases={"功能查询"},priority=3)
@queryGroup.handle()
async def queryGroup_handle(matcher:Matcher,state:T_State,event:Event,width:int=1024):
    conn=connect(host="localhost",user="root",password="allforqqbot",database="qqbot",port=3306,charset="UTF8")
    cur=conn.cursor()
    _,group,qq=str(event.get_session_id()).split("_")
    

    #字体
    font_path=os.getcwd()+"\\awesomebot\\plugins\\font\\fzzxhk.ttf"
    head_font=ImageFont.truetype(font_path,width//10)
    m_head_font=ImageFont.truetype(font_path,width//20)
    text_font=ImageFont.truetype(font_path,width//25)

    #先生成对应文本
    #返回标题宽度和高度的元组，计算需要生成的图片的高度
    sql=f"select name from name_of_functions"
    tmp=cur.execute(sql)
    result=cur.fetchall()
    head_width,head_height=head_font.getsize("yz有以下功能")
    cnt=0
    all_function_msg:str=""
    for raw in result :
        cnt=cnt+1
        all_function_msg=all_function_msg+f"{cnt}："+raw[0]+"\n"
    text1_width,text1_height= text_font.getsize(all_function_msg)
    
    sql=f"select functions from group_function_list where group_num=%s"
    tmp=cur.execute(sql,group)
    result=cur.fetchall()
    m_head_width,m_head_height=m_head_font.getsize("该群已启用的功能有")
    cnt=0
    this_function_msg:str=""
    for raw in result:
        cnt=cnt+1
        this_function_msg=this_function_msg+f"{cnt}："+raw[0]+"\n"
    text2_width,text2_height=text_font.getsize(this_function_msg)
    
    #生成图片
    background=Image.new(
        mode="RGB",
        size=(width,background_height),
        color=(255,255,255)
    )
    
    msg=msg+"该群已启用的功能有\n"
    cnt=0
    for raw in result:
        cnt=cnt+1
        msg=msg+f"{cnt}："+raw[0]+"\n"
    cur.close()
    conn.close()
    await queryGroup.send(msg)