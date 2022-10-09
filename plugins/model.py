from pydantic import BaseModel
class ImageUtilsBaseModel(BaseModel):
    class Config:
        extra = "ignore"
        allow_mutation=False
class PreviewImageThumbs(ImageUtilsBaseModel):
    """字节形式存储的图"""
    desc_test:str
    preview_thumb:bytes
class PreviewImageModel(ImageUtilsBaseModel):
    """含有多张预览图的图"""
    preview_name:str
    count:int
    previews:list[PreviewImageThumbs]
