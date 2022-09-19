"""
塔罗牌部分修改自omega_miya

"""
from io import BytesIO
from typing import Literal
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Event
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot import on_command
from .managementModule.isInGroup import isInGroup
from .tarot_data import TarotCards
from .tarot_typing import TarotCard
import random
import os

tarot=on_command("tarot",aliases={"塔罗牌"})
@tarot.handle()
async def tarot_handle(event:Event,matcher:Matcher):
    _,group,qq=str(event.get_session_id()).split("_")
    if isInGroup(group,"tarot")==0:
        await tarot.finish(None)
    card = random.randint(1,77)
    # 随机正逆
    direction = random.choice([-1, 1])
    if direction == 1:
        need_upright = True
        need_reversed = False
    else:
        need_upright = False
        need_reversed = True
        # 绘制卡图
    card_image = generate_tarot_card(
        id_=card,
        direction=direction,
        need_desc=1,
        need_upright=need_upright,
        need_reversed=need_reversed
    )#返回路径
    card_image.replace("\\","/")
    await matcher.send(MessageSegment.image("file:///"+card_image))

    
#分割多行文本
class TextUtils(object):
    def __init__(self, text: str):
        self._text = text

    def __repr__(self):
        return f'<TextUtils(text={self._text})>'

    @property
    def text(self) -> str:
        return self._text

    def split_multiline(
            self,
            width: int,
            font: ImageFont.FreeTypeFont,
            *,
            stroke_width=0) -> "TextUtils":
        spl_num = 0
        spl_list = []
        for num in range(len(self._text)):
            text_width, text_height = font.getsize_multiline(self._text[spl_num:num], stroke_width=stroke_width)
            if text_width > width:
                spl_list.append(self._text[spl_num:num])
                spl_num = num
        else:
            spl_list.append(self._text[spl_num:])

        self._text = '\n'.join(spl_list)
        return self

def get_card_by_id(id:int)->TarotCard:
    lst=TarotCards.get_all_cards()
    for i in lst:
        if i.id==id:
            return i

def generate_tarot_card(
        id_: int,
        direction: int = 1,
        *,
        need_desc: bool = True,
        need_upright: bool = True,
        need_reversed: bool = True,
        width: int = 1024):

    # 获取这张卡牌
    tarot_card=get_card_by_id(id=id_)
    tarot_card_file = os.getcwd()+"\\awesomebot\\plugins\\localResource\\tarot\\bilibili\\"+f"{id_}.png"

    """绘制卡片图片"""
    # 获取卡片图片
    draw_tarot_img: Image.Image = Image.open(tarot_card_file)
    # 正逆
    if direction < 0:
        draw_tarot_img = draw_tarot_img.rotate(180)

    # 调整头图宽度
    tarot_img_height = int(width * draw_tarot_img.height / draw_tarot_img.width)
    draw_tarot_img = draw_tarot_img.resize((width, tarot_img_height))

    # 字体
    """
    取整除
    """
    font_path=os.getcwd()+"\\awesomebot\\plugins\\font\\fzzxhk.ttf"
    title_font = ImageFont.truetype(font_path, width // 10)
    m_title_font = ImageFont.truetype(font_path, width // 20)
    text_font = ImageFont.truetype(font_path, width // 25)

    # 标题
    title_width, title_height = title_font.getsize(tarot_card.name)
    m_title_width, m_title_height = m_title_font.getsize(tarot_card.name)

    # 描述
    desc_text = TextUtils(
        text=tarot_card.desc).split_multiline(width=(width - int(width * 0.125)), font=text_font).text
    desc_text_width, desc_text_height = text_font.getsize_multiline(desc_text)

    # 正位描述
    upright_text = TextUtils(
        text=tarot_card.upright).split_multiline(width=(width - int(width * 0.125)), font=text_font).text
    upright_text_width, upright_text_height = text_font.getsize_multiline(upright_text)

    # 逆位描述
    reversed_text = TextUtils(
        text=tarot_card.reversed).split_multiline(width=(width - int(width * 0.125)), font=text_font).text
    reversed_text_width, reversed_text_height = text_font.getsize_multiline(reversed_text)

    # 计算高度
    background_height = title_height + m_title_height + tarot_img_height + int(0.09375 * width)
    if need_desc:
        background_height += desc_text_height + int(0.125 * width)
    if need_upright:
        background_height += m_title_height + upright_text_height + int(0.125 * width)
    if need_reversed:
        background_height += m_title_height + reversed_text_height + int(0.125 * width)

    # 生成背景
    background = Image.new(
        mode="RGB",
        size=(width, background_height),
        color=(255, 255, 255))

    # 开始往背景上绘制各个元素
    # 以下排列从上到下绘制 请勿变换顺序 否则导致位置错乱
    this_height = int(0.0625 * width)
    ImageDraw.Draw(background).text(xy=(width // 2, this_height),
                                    text=tarot_card.name, font=title_font, align='center', anchor='mt',
                                    fill=(0, 0, 0))  # 中文名称

    this_height += title_height
    ImageDraw.Draw(background).text(xy=(width // 2, this_height),
                                    text=tarot_card.orig_name, font=m_title_font, align='center', anchor='ma',
                                    fill=(0, 0, 0))  # 英文名称

    this_height += m_title_height + int(0.03125 * width)
    background.paste(draw_tarot_img, box=(0, this_height))  # 卡面

    this_height += tarot_img_height
    if need_desc:
        this_height += int(0.0625 * width)
        ImageDraw.Draw(background).multiline_text(xy=(width // 2, this_height),
                                                    text=desc_text, font=text_font, align='center', anchor='ma',
                                                    fill=(0, 0, 0))  # 描述
        this_height += desc_text_height

    if need_upright:
        this_height += int(0.0625 * width)
        ImageDraw.Draw(background).text(xy=(width // 2, this_height),
                                        text='【正位】', font=m_title_font, align='center', anchor='ma',
                                        fill=(0, 0, 0))  # 正位

        this_height += m_title_height + int(0.03125 * width)
        ImageDraw.Draw(background).multiline_text(xy=(width // 2, this_height),
                                                    text=upright_text, font=text_font, align='center', anchor='ma',
                                                    fill=(0, 0, 0))  # 正位描述
        this_height += upright_text_height

    if need_reversed:
        this_height += int(0.0625 * width)
        ImageDraw.Draw(background).text(xy=(width // 2, this_height),
                                        text='【逆位】', font=m_title_font, align='center', anchor='ma',
                                        fill=(0, 0, 0))  # 逆位

        this_height += m_title_height + int(0.03125 * width)
        ImageDraw.Draw(background).multiline_text(xy=(width // 2, this_height),
                                                    text=reversed_text, font=text_font, align='center', anchor='ma',
                                                    fill=(0, 0, 0))  # 逆位描述

    background_path=os.getcwd()+"\\awesomebot\\plugins\\imagetmp\\tarottmp.jpg"
    background.save(background_path)
    return background_path
