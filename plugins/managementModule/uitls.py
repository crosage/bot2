

from nonebot.adapters.onebot.v11.message import Message,MessageSegment

class messageTools(object):
    """
    message 工具：
    get_user_head_img_url：根据qq获取头像url
    get_all_img_url：获取该聊天消息中所有图片的url，返回message类型
    get_all_at_qq：获取被at人的qq
    """

    def __init__(self,message:Message):
        self._message=message
    def get_user_head_img_url(user_id:int,head_img_size:int=5):
        """根据qq获取头像url"""
        return f'https://q1.qlogo.cn/g?b=qq&nk={user_id}&s={head_img_size}'
    def get_all_img_url(self)->list[str] :
        """获取聊天消息中所有图片的url"""
        return [str(msg_seg.data.get("url")) for msg_seg in self._message if msg_seg.type =="image"]
    def get_all_at_qq(self)->list[int]:
        """获取聊天消息中被@人的qq"""
        return [int(msg_seg.data.get("qq")) for msg_seg in self._message if msg_seg.type=="at"]