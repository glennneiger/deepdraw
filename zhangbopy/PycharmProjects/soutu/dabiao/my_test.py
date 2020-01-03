# from dabiao.models import Mark_Pic, Get_Task
#
#
# def read_into_db(self, filename):
#     import pandas as pd
#     import numpy as np
#     db_data = pd.read_csv(filename)
#     for i in range(0, len(db_data)):
#         record = db_data[i:i + 1]
#         record_list = np.array(record)
#         data = record_list.tolist()
#         url = str(data[0][0])
#         class_id = str(data[0][1])
#         t = str(data[0][2])
#         r = str(data[0][3])
#         b = str(data[0][4])
#         l = str(data[0][5])
#         isMain = str(data[0][6])
#         status = str(data[0][7])
#         pic = Mark_Pic(
#             url=url,
#             class_id=class_id,
#             t=t,
#             r=r,
#             b=b,
#             l=l,
#             isMain=isMain,
#             status=status
#         )
#         pic.save()
#         task = Get_Task(
#             class_id=class_id,
#             status=status,
#             user='null'
#         )
#         task.save()
#         ret = 'finish:' + filename + '  load success'
#     return ret
#
#
# if __name__ == '__main__':
#     # import pandas as pd
#     # import numpy as np
#     # a = pd.read_csv('/home/wangzishen/sql_file/csv_test_img_0.csv')
#     # for i in range(0,len(a)):
#     #     b = a[i:i+1]
#     #     c = np.array(b)
#     #     c_list = c.tolist()
#     #     print(str(c[0][7]),i)
#     #     # print(len(a))
#     read_into_db('/home/wangzishen/sql_file/csv_test_img_0.csv')
