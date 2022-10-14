from pydantic import BaseModel
from .pixivfetcher import HttpFecher
from typing import TypeVar
from nonebot.log import logger
class PreviewImageThumbs():
    """字节形式存储的图"""
    def __init__(self,string,bytesString) -> None:
        self.desc_text=string
        self.preview_thumb=bytesString
class PreviewImageModel():
    """含有多张预览图的图"""
    def __init__(self) -> None:
        self.preview_name=""
        self.count=0
        self.previews=[]

class PixivArtworkPreviewModel(PreviewImageModel):
    """Pixiv 作品预览图 Model"""

class PixivArtworkPreviewBody(PreviewImageThumbs):
    """Pixiv 作品预览图中的缩略图数据"""
