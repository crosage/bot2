from weakref import proxy
from .pixivfetcher import HttpFecher
from datetime import datetime
from pydantic import BaseModel
import aiohttp

async def emit_preview_model_from_ranking_model(
        ranking_name: str, model: PixivRankingModel) -> PixivArtworkPreviewModel:
    """从排行榜结果中获取生成预览图所需要的数据模型"""
    request_list = [
        PixivArtworkPreviewRequestModel(
            desc_text=format_artwork_preview_desc(
                pid=data.illust_id,
                title=f'【No.{(model.page - 1) * len(model.contents) + index + 1}】{data.title}',
                uname=data.user_name),
            request_url=data.url)
        for index, data in enumerate(model.contents)]
    preview_model = await _request_preview_model(preview_name=ranking_name, requests=request_list)
    return preview_model

class Pixiv(object):
    HttpFecher()
    _default_headers=HttpFecher._default_headers
    _api_fetcher=HttpFecher(timeout=10, headers=_default_headers, cookies={"cookies":"42279487_AG4HmdEZ5UhzySdgn5imxVARbCYk6p0W"})
    
class PixivRanking(Pixiv):
    ranking_url:str="https://www.pixiv.net/ranking.php"
    @classmethod
    async def query_ranking(cls,mode,content="illust",page:int =1):
        params={"format":"json","mode":mode,"p":page,"content":content}
        ranking_data=await cls._api_fetcher.get_json_dict(url=cls.ranking_url,params=params)
        if ranking_data.status!=200:
            print(f"FATAL status={ranking_data.result}")
        print(ranking_data.result)
    @classmethod
    async def query_daily_illust_ranking_with_preview(cls,page:int =1):
        ranking_result=await cls.query_ranking(mode="daily",page=page,content="illust")
        name=f"Pixiv Daily Ranking {datetime.now().strftime('%Y-%m-%d')}"
        preview_request=await em
