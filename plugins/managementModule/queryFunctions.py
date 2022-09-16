from pymysql import *
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import Bot,Event
from nonebot.matcher import Matcher
from PIL import Image,ImageDraw,ImageFont
#获取参数 对参数操作
from nonebot.params import Arg,CommandArg,ArgPlainText
from nonebot.adapters.onebot.v11.message import MessageSegment
from PIL import ImageDraw
import os

queryGroup=on_command("云栀功能",aliases={"云栀功能查询"},priority=3)
@queryGroup.handle()
async def queryGroup_handle(matcher:Matcher,state:T_State,event:Event,width:int=1024):
    conn=connect(host="localhost",user="root",password="allforqqbot",database="qqbot",port=3306,charset="UTF8")
    cur=conn.cursor()
    _,group,qq=str(event.get_session_id()).split("_")
    

    #字体
    font_path=os.getcwd()+"\\awesomebot\\plugins\\font\\fzzxhk.ttf"
    head_font=ImageFont.truetype(font_path,width//18)
    m_head_font=ImageFont.truetype(font_path,width//20)
    text_font=ImageFont.truetype(font_path,width//25)

    #先生成对应文本
    #返回标题宽度和高度的元组，计算需要生成的图片的高度
    background_height=0
    text_width,text_height=text_font.getsize("填充符5Hh")

    sql=f"select name from name_of_functions"
    tmp=cur.execute(sql)
    result=cur.fetchall()
    head_width,head_height=head_font.getsize("yz有以下功能")
    background_height=background_height+head_height+int(0.0325*width)#加上标题高度和标题与表头的空隙
    cnt1=0
    all_function_msg:list[str]=[]
    for raw in result :
        cnt1=cnt1+1
        all_function_msg.append(f"{cnt1}："+raw[0])
        background_height=background_height+text_height+int(0.0125*width)
    
    background_height=background_height+int(0.0325*width)#已有功能和本群已启用的功能的空隙

    sql=f"select functions from group_function_list where group_num=%s"
    tmp=cur.execute(sql,group)
    result=cur.fetchall()
    m_head_width,m_head_height=m_head_font.getsize("该群已启用的功能有")
    background_height=background_height+m_head_height#加上副标题高度
    cnt2=0
    this_function_msg:list[str]=[]
    for raw in result:
        cnt2=cnt2+1
        this_function_msg.append(f"{cnt2}："+raw[0])
        background_height=background_height+text_height+int(0.0125*width)
    background_height=background_height+int(0.0325*width)
    
    #生成背景图片
    background=Image.new(
        mode="RGB",
        size=(width,background_height),
        color=(255,255,255)
    )
    
    #绘制文本
    this_height=int(0.0325*width)#标题与最上面的空隙
    ImageDraw.Draw(background).text(xy=(0,this_height),text="云栀有以下功能：",font=head_font,aligh="left",fill=(0,0,0))
    this_height=this_height+head_height
    for i in range(cnt1):
        this_height=this_height+int(0.0125*width)#每行的空隙
        ImageDraw.Draw(background).text(xy=(0,this_height),text="       "+all_function_msg[i],font=text_font,aligh="left",fill=(0,0,0))
        this_height=this_height+text_height

    this_height=this_height+int(0.0325*width)
    ImageDraw.Draw(background).text(xy=(0,this_height),text="该群已启用的功能有：",font=m_head_font,aligh="left",fill=(0,0,0))
    this_height=this_height+m_head_height
    for i in range(cnt2):
        this_height=this_height+int(0.0125*width)#每行的空隙
        ImageDraw.Draw(background).text(xy=(0,this_height),text="       "+this_function_msg[i],font=text_font,aligh="left",fill=(0,0,0))
        this_height=this_height+text_height
    
    this_height=this_height+int(0.0325*width)
    #保存并输出图片
    background_path=os.getcwd()+"\\awesomebot\\plugins\\querytmp\\tmp.jpg"
    background.save(background_path)
    background_path="file:///"+os.getcwd().replace("\\","/")+"/awesomebot/plugins/querytmp/tmp.jpg"
    cur.close()
    conn.close()
    await queryGroup.send(MessageSegment.image(background_path))