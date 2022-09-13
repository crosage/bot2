from pymysql import *
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot,Event
from nonebot.adapters import Message
from nonebot.matcher import Matcher #matcher 匹配器
from nonebot.params import Arg,CommandArg,ArgPlainText #param 参数，对参数的操作

petpet=on_command("petpet",aliases={"摸摸"})