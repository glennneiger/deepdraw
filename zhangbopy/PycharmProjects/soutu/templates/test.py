# line_list = []
# with open('classfication.txt','r',encoding='utf-8') as f:
#     for line in f:
#         line = line.replace('|','')
#         line = line.replace('\'','')
#         line = line.replace('\n','')
#         line = line.replace(' ', '')
#         line_list.append(line)
#     print(line_list)
import pymysql
connect = pymysql.Connect(
    host='192.168.2.101',
    port=3306,
    user='root',
    passwd='666666',
    db='soutu',
    charset='utf8'
)

cur = connect.cursor()
sql = """select * from dabiao_mark_pic;"""
cur.execute(sql)
ret = cur.fetchall()
print(ret)