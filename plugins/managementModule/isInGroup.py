from pymysql import *


def isInGroup(group_num:int,functions:str)->int:
    """群里是否有该功能"""
    conn=connect(host="localhost",port=3306,user="root",password="allforqqbot",database="qqbot",charset="UTF8")
    cur=conn.cursor()
    sql=f"select * from group_function_list where group_num=%s and functions=%s"
    tmp=cur.execute(sql,[group_num,functions])
    if tmp==0 :
        cur.close()
        conn.close()
        return 0
    cur.close()
    conn.close()
    return 1