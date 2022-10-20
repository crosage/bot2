
import asyncio
from math import ceil
from PIL import ImageFont,Image,ImageDraw

from nonebot.adapters.onebot.v11 import MessageSegment
from numpy import argsort
import priority
from .pixivfetcher import HttpFecher
from datetime import datetime
from pydantic import BaseModel
from nonebot.log import logger
from io import BytesIO
import aiohttp
import re
from .model import PreviewImageModel, PreviewImageThumbs
from .model import PixivArtworkPreviewModel
from .Configs import pixiv_preview_path
from .Configs import pixiv_path,default_font_path
import datetime
import random 
from pymysql import *
from nonebot.plugin import on_keyword
from nonebot.plugin import on_command
from nonebot.plugin.on import on_fullmatch
from nonebot.adapters.onebot.v11 import Bot,Event
from nonebot.adapters.onebot.v11.message import Message
from .managementModule.isInGroup import isInGroup
from nonebot.typing import T_State
from nonebot.params import CommandArg,ArgStr

class Pixiv(object):
    _default_headers=HttpFecher._default_headers
    _api_fetcher=HttpFecher(timeout=10, headers=_default_headers, cookies={"cookies":"42279487_AG4HmdEZ5UhzySdgn5imxVARbCYk6p0W"})
def resize_with_filling(preimage, size: tuple[int, int]):
    """在不损失原图长宽比的条件下, 使用透明图层将原图转换成指定大小"""
    _image = preimage
        # 计算调整比例
    width, height = _image.size
    rs_width, rs_height = size
    scale = min(rs_width / width, rs_height / height)

    _image = _image.resize((int(width * scale), int(height * scale)))
    box = (int(abs(width * scale - rs_width) / 2), int(abs(height * scale - rs_height) / 2))
    background = Image.new(mode="RGBA", size=size, color=(255, 255, 255, 0))
    background.paste(_image, box=box)

    preimage = background
    return preimage
async def generate_thumbs_preview_image(
        preview:PreviewImageModel,
        preview_size: tuple[int, int]=(512,512),
        *,
        font_path: str=default_font_path,
        header_color: tuple[int, int, int] = (255, 255, 255),
        hold_ratio: bool = True,
        num_of_line: int = 5,
        limit: int = 1000
) :
    """生成多个带说明的缩略图的预览图

    :param preview: 经过预处理的生成预览的数据
    :param preview_size: 单个小缩略图的尺寸
    :param font_path: 用于生成预览图说明的字体
    :param header_color: 页眉装饰色
    :param hold_ratio: 是否保持缩略图原图比例
    :param num_of_line: 生成预览每一行的预览图数
    :param limit: 限制生成时加载 preview 中图片的最大值
    :param output_folder: 输出文件夹
    """

    previews = preview.previews
    preview_name=preview.preview_name
    def _handle_preview_image() -> bytes:
        """用于图像生成处理的内部函数"""
        _thumb_w, _thumb_h = preview_size
        _font_path = default_font_path
        _font_main = ImageFont.truetype(_font_path, _thumb_w // 15)
        _font_title = ImageFont.truetype(_font_path, _thumb_w // 5)

        # 输出图片宽度
        _preview_w = _thumb_w * num_of_line

        # 标题
        _title = preview.preview_name
        # 计算标题尺寸
        _title_w, _title_h = _font_title.getsize_multiline(text=_title)

        # 根据缩略图计算标准间距
        _spacing_w = int(_thumb_w * 0.4)
        _spacing_title = _spacing_w if _title_h <= int(_spacing_w * 0.75) else int(_title_h * 1.5)

        _background = Image.new(
            mode="RGB",
            size=(_preview_w, (_thumb_h + _spacing_w) * ceil(len(previews) / num_of_line) + _spacing_title),
            color=(255, 255, 255))

        # 画一个装饰性的页眉
        # 处理颜色
        light = tuple(z if z > 0 else 0 for z in (y if y < 255 else 255 for y in (int(x / 0.9) for x in header_color)))
        dark = tuple(z if z > 0 else 0 for z in (y if y < 255 else 255 for y in (int(x * 0.9) for x in header_color)))

        ImageDraw.Draw(_background).polygon(
            xy=[(0, 0), (0, _title_h), (_title_h, 0)],
            fill=dark
        )  # 左上角下层小三角形
        ImageDraw.Draw(_background).polygon(
            xy=[(0, 0), (_preview_w, 0), (_preview_w, int(_title_h / 8)), (0, int(_title_h / 8))],
            fill=header_color
        )  # 页眉横向小蓝条
        ImageDraw.Draw(_background).polygon(
            xy=[(0, 0), (0, int(_title_h * 5 / 6)), (int(_title_h * 5 / 6), 0)],
            fill=light
        )  # 左上角最上层小三角形

        # 写标题
        ImageDraw.Draw(_background).multiline_text(
            xy=(_preview_w // 2, int(_title_h / 3)), text=_title, font=_font_title,
            align='center', anchor='ma', fill=(0, 0, 0))

        # 处理拼图
        _line = 0
        for _index, _preview in enumerate(previews):
            with BytesIO(_preview.preview_thumb) as bf:
                _thumb_img: Image.Image = Image.open(bf)
                _thumb_img.load()
            # 调整图片大小
            if hold_ratio:
                _thumb_img = resize_with_filling(_thumb_img,preview_size)
            h=_thumb_img.height
            w=_thumb_img.width
            bili:float=0
            if h>=w:
                bili=preview_size[0]/h
            else :
                bili=preview_size[1]/w
            if _thumb_img.size != preview_size:
                _thumb_img = _thumb_img.resize(size=(int(w*bili),int(h*bili)))

            # 确认缩略图单行位置
            seq = _index % num_of_line
            # 能被整除说明在行首要换行
            if seq == 0:
                _line += 1
            logger.info(f"{seq*_thumb_h}      {seq * _thumb_w + _thumb_w /2}")
            # 按位置粘贴单个缩略图
            _background.paste(_thumb_img, box=(seq * _thumb_w, (_thumb_h + _spacing_w) * (_line - 1) + _spacing_title))
            ImageDraw.Draw(_background).multiline_text(
                xy=(seq * _thumb_w + _thumb_w //2,
                    (_thumb_h + _spacing_w) * (_line - 1) + _spacing_title + _thumb_h + _spacing_w // 10),
                text=_preview.desc_text, font=_font_main,
                align='center', anchor='ma', fill=(0, 0, 0))
        # 生成结果图片
        with BytesIO() as _bf:
            _background.save(_bf, 'JPEG')
            _content = _bf.getvalue()
        return _content

    image_content = _handle_preview_image()
    image_file_name = f"preview_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.jpg"
    newpath=pixiv_preview_path+"\\"+image_file_name
    logger.warning(f"{newpath}")
    with open(pixiv_preview_path+"\\"+image_file_name,"wb") as f:
        f.write(image_content)
    return pixiv_preview_path+"\\"+image_file_name

class PixivRanking(Pixiv):
    ranking_url:str="https://www.pixiv.net/ranking.php"
    @classmethod
    async def query_ranking(cls,mode="daily",content="illust",page:int =1):
        params={"format":"json","mode":mode,"p":page,"content":content}
        ranking_data=await cls._api_fetcher.get_json_dict(url=cls.ranking_url,params=params)
        if ranking_data["status"]!=200:
            print(f"FATAL status={ranking_data.result}")
        ranking_data=ranking_data["result"]
        # logger.debug(f"{ranking_data.keys()}")
        logger.info("开始")
        preview=PreviewImageModel()
        preview.preview_name=f"Pixiv {mode} Ranking {datetime.datetime.now().strftime('%Y-%m-%d')}"
        # logger.error(f"{ranking_data}")
        async with aiohttp.ClientSession() as session:
            cnt=0
            for content in ranking_data["contents"]:
                cnt=cnt+1
                imgurls=content["url"]
                imgurls=imgurls.replace("c/240x480/img-master","img-original")
                imgurls=imgurls.replace("0_master1200.jpg","")
                # logger.error(f"加工之前：{imgurls}")
                illust_page_count=int(content["illust_page_count"])
                # logger.error(f"url={imgurls}")
                new_headers=HttpFecher.get_default_headers()
                new_headers.update({"Referer":"https://www.pixiv.net/artworks/"+str(content["illust_id"])})
                for i in range(0,1):
                    imgurl=imgurls+str(i)+".jpg"
                    logger.info(f"url={imgurl}")
                    async with session.get(url=imgurl,headers=new_headers,cookies={"cookies":"你的cookie"},proxy="http://localhost:7890") as resp:
                        if resp.status==200:
                            # logger.warning("运行到这了")
                            _bytes=await resp.read()
                            preview.previews.append(PreviewImageThumbs(f"Pid:{content['illust_id']}\n[No.{content['rank']}]:{content['title']}\nAuther:{content['user_name']}",_bytes))
                            # imgtype=str(imgurl.split(".")[-1])
                            # new_path=pixiv_path+f"\\{content['illust_id']}"
                            # with open(new_path+f"_p{i}."+imgtype,"wb") as f:
                            #     f.write(_bytes)
                        else :
                            imgurl=imgurl.replace("jpg","png")
                            async with session.get(url=imgurl,headers=new_headers,cookies={"cookies":"你的cookie"},proxy="http://localhost:7890") as resp2:
                                _bytes=await resp2.read()
                                preview.previews.append(PreviewImageThumbs(f"Pid:{content['illust_id']}\n[No.{content['rank']}]:{content['title']}\nAuther:{content['user_name']}",_bytes))
                                # imgtype=str(imgurl.split(".")[-1])
                                # new_path=pixiv_path+f"\\{content['illust_id']}"
                                # with open(new_path+f"_p{i}."+imgtype,"wb") as f:
                                #     f.write(_bytes)
        returnpath=await generate_thumbs_preview_image(preview=preview)
        return returnpath      
        # logger.info("结束")
    @classmethod
    async def get_by_id(cls,id):
        logger.warning("开始开始")
        _headers=HttpFecher.get_default_headers()
        _headers.update({"referer":"https://www.pixiv.net"})
        imgurl=f"https://www.pixiv.net/ajax/illust/{id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=imgurl,headers=_headers,cookies={"cookies":"你的cookie"},proxy="http://localhost:7890") as resp:
                logger.info(resp.headers)
                result=await resp.text()
            if resp.status !=200:
                return "error"
        # logger.error(result)
            pattern=re.compile(r'\"https:\\/\\/i.pximg.net\\/img-original\\/img.*?\"')
        # logger.info(pattern.search(result).group())
            newurl=pattern.search(result).group()
            newurl=newurl.replace("\\","")
            newurl=newurl.replace("\"","")
            logger.error(f"{newurl}")
            async with session.get(url=newurl,headers=_headers,cookies={"cookies":"你的cookie"},proxy="http://localhost:7890") as resp2:
                result2=await resp2.read()
                new_path=pixiv_path+f"\\{id}"
                imgtype=str(newurl.split(".")[-1])
                with open(new_path+f"_p{0}."+imgtype,"wb") as f:
                    f.write(result2)
                return new_path+f"_p{0}."+imgtype

    '''
    @classmethod
    async def query_daily_illust_ranking_with_preview(cls, page: int = 1):
        ranking_result = await cls.query_ranking(mode='daily', page=page, content='illust')
        name = f'Pixiv Daily Ranking {datetime.now().strftime("%Y-%m-%d")}'
        preview_request = await emit_preview_model_from_ranking_model(ranking_name=name, model=ranking_result)
        preview_img_file = await generate_artworks_preview_image(
            preview=preview_request, preview_size=(512, 512), hold_ratio=True, num_of_line=6)
        return preview_img_file
    def printit():
        print("haha")
    '''
#        return None
#    @classmethod
#    async def query_daily_illust_ranking_with_preview(cls,page:int =1):
#        ranking_result=await cls.query_ranking(mode="daily",page=page,content="illust")
#        name=f"Pixiv Daily Ranking {datetime.now().strftime('%Y-%m-%d')}"
#        preview_request=await em
#loop=asyncio.get_event_loop()
#res=loop.run_until_complete((PixivRanking.query_ranking(mode="daily")))
# loop.close()
pixiv=on_command("pixiv日榜",priority=20,block=True)
@pixiv.handle()
async def pixiv_handle(bot:Bot,event:Event,state:T_State,cmd_arg: Message = CommandArg()):
    _,group,qq=str(event.get_session_id()).split("_")
    logger.error("errorrrrrrrrrrr")
    if isInGroup(group,"pixiv")==0:
        return 
    page=cmd_arg.extract_plain_text().strip()
    logger.info(f"{page}******")
    if page:
        logger.info(f"接收到{page}")
        state.update({"page":page})
    else :
        state.update({"page":1})
@pixiv.got("page")
async def pixivwork(bot:Bot,pid:str=ArgStr("page")):
    logger.info("haha")
    pid=pid.strip()
    await pixiv.send("别急")
    path=await PixivRanking.query_ranking(page=pid)    
    path.replace("\\","/")
    await pixiv.send(MessageSegment.image("file:///"+path))

pixiv_week=on_command("pixiv周榜",priority=20,block=True)
@pixiv_week.handle()
async def pixiv_week_handle(bot:Bot,event:Event,state:T_State,cmd_arg: Message = CommandArg()):
    _,group,qq=str(event.get_session_id()).split("_")
    # logger.error("errorrrrrrrrrrr")
    if isInGroup(group,"pixiv")==0:
        return 
    page=cmd_arg.extract_plain_text().strip()
    # logger.info(f"{page}******")
    if page:
        logger.info(f"接收到{page}")
        state.update({"page":page})
    else :
        state.update({"page":1})
@pixiv_week.got("page")
async def pixivweekwork(bot:Bot,pid:str=ArgStr("page")):
    logger.info("haha")
    pid=pid.strip()
    await pixiv_week.send("别急")
    path=await PixivRanking.query_ranking(mode="weekly",page=pid)    
    path.replace("\\","/")
    await pixiv_week.send(MessageSegment.image("file:///"+path))

pixiv_month=on_command("pixiv月榜",priority=20,block=True)
@pixiv_month.handle()
async def pixiv_month_handle(bot:Bot,event:Event,state:T_State,cmd_arg: Message = CommandArg()):
    _,group,qq=str(event.get_session_id()).split("_")
    # logger.error("errorrrrrrrrrrr")
    if isInGroup(group,"pixiv")==0:
        return 
    page=cmd_arg.extract_plain_text().strip()
    # logger.info(f"{page}******")
    if page:
        logger.info(f"接收到{page}")
        state.update({"page":page})
    else :
        state.update({"page":1})
@pixiv_month.got("page")
async def pixivmonthwork(bot:Bot,pid:str=ArgStr("page")):
    logger.info("haha")
    pid=pid.strip()
    await pixiv_month.send("别急")
    path=await PixivRanking.query_ranking(mode="monthly",page=pid)    
    path.replace("\\","/")
    await pixiv_month.send(MessageSegment.image("file:///"+path))

pixiv_18_daily=on_command("pixiv18+日榜",priority=20,block=True)
@pixiv_18_daily.handle()
async def pixiv_handle(bot:Bot,event:Event,state:T_State,cmd_arg: Message = CommandArg()):
    _,group,qq=str(event.get_session_id()).split("_")
    logger.info("被18+接收到")
    if isInGroup(group,"pixiv")==0:
        return 
    page=cmd_arg.extract_plain_text().strip()
    if page:
        logger.info(f"接收到{page}")
        state.update({"page":page})
    else :
        state.update({"page":1})
@pixiv_18_daily.got("page")
async def pixiv18work(bot:Bot,page:str=ArgStr("page")):
    logger.info("haha??")
    page=page.strip()
    await pixiv_18_daily.send("别急")
    path=await PixivRanking.query_ranking(mode="daily_r18",page=page)    
    path.replace("\\","/")
    await pixiv_18_daily.send(MessageSegment.image("file:///"+path))



pixiv_id=on_command("pixiv",priority=30,block=True)
@pixiv_id.handle()
async def pixiv_id_handle(bot:Bot,event:Event,state:T_State,cmd_arg: Message = CommandArg()):
    # return 
    _,group,qq=str(event.get_session_id()).split("_")
    logger.info("被pixiv接收到")
    if isInGroup(group,"pixiv")==0:
        return 
    pid=cmd_arg.extract_plain_text().strip()
    if pid:
        path:str=await PixivRanking.get_by_id(pid)
        if path=="error":
            await pixiv.send(f"没有这个图QAQ {pid}")
        else :
            try:
                await pixiv.send(MessageSegment.image("file:///"+path))
            except:
                await pixiv.send(f"这个图被吞了，对不起喵{pid}")
