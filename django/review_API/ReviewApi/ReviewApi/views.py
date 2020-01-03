from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
import elasticsearch
import json, requests
from elasticsearch import Elasticsearch, helpers
import requests
import time
import numpy as np


def requestGet():
    url = "http://192.168.2.109:9200/review_recs/_search"
    r = requests.get(url)
    data = r.json()
    # print(data)
    return data


es = Elasticsearch(["192.168.2.101:9200", "192.168.2.109:9200", "192.168.2.108:9200"],
                   # ["es1.nps.deepdraw.online","es3.nps.deepdraw.online","es2.nps.deepdraw.online"],
                   sniff_on_start=True,
                   # refresh nodes after a node fails to respond
                   sniff_on_connection_fail=True,
                   # and also every 60 seconds
                   sniffer_timeout=60,
                   # http_auth=('dbr-kibana','trbl666'),
                   # scheme="http",
                   # port=80
                   )
es2 = Elasticsearch("192.168.2.104:9200")

testData = [
    0.18892711400985718,
    0.44179582595825195,
    0.19186179339885712,
    -0.182672917842865,
    -0.16897451877593994,
    0.011483825743198395,
    0.04389645904302597,
    0.05116838216781616,
    0.47192975878715515,
    0.5200067162513733,
    0.15860088169574738,
    0.09255780279636383,
    0.41139858961105347,
    0.22027963399887085,
    0.05523592233657837,
    0.0568743534386158,
    0.21820978820323944,
    0.7182787656784058,
    -0.042417898774147034,
    -0.05150901526212692,
    -0.22382205724716187,
    -0.2531544268131256,
    0.3610939085483551,
    0.1932738721370697,
    0.20352202653884888,
    0.8739648461341858,
    0.33667364716529846,
    0.49401330947875977,
    0.2154138833284378,
    -0.15730026364326477,
    0.585889458656311,
    0.46946027874946594
]
testData2 = np.random.uniform(-1, 1, size=32).tolist()


class GuideView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templetes/test.html").read())


class EsSearch(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templetes/essearch.html").read())


def hello(request):
    return HttpResponse("Hello world ! ")


def getStatus():
    global es
    bod = {"query": {"match": {"last_name": "Smith"}}}
    s = es.search(index="test_lp", body=bod)
    return s


def aggs_count(agg_name, top_num):
    global es
    s = es.search(index="review_recs",  # 索引名
                  body={
                      "track_total_hits": 1000000,
                      "aggs": {
                          "agg_count": {
                              "terms": {"field": agg_name, "size": 1000}
                          }
                      }
                  })
    buckets = s['aggregations']['agg_count']['buckets'][:top_num]
    allcount = s['hits']['total']['value']
    ##value_list = [x['doc_count'] for x in buckets]
    return buckets, allcount


# class SearchView(APIView):
#     def post(self, request, *args, **kwargs):
#         try:
#             print(request.data['what'])
#             # temp = getStatus();
#             temp = requestGet()
#             print(temp["hits"]["hits"])
#             res = temp['hits']['hits']
#             print(len(res))
#             ret = {
#                 "code": 200,
#                 "msg": "success",
#             }
#         except Exception as e:
#             print('---error----', e)
#             ret = {
#                 "code": 404,
#                 "result": "失败"
#             }
#
#         return JsonResponse(ret)
#
#     def get(self, request):
#         temp = getStatus()
#         print(temp['hits']['hits'])
#         x = temp['hits']['hits']
#         print('ok')
#         ret = {
#             "code": 200,
#             "msg": "success",
#             'data': x,
#         }
#
#         return JsonResponse(ret)

class SearchView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            print(request.data['what'])
            # temp = getStatus();
            temp = requestGet()
            print(temp["hits"]["hits"])
            res = temp['hits']['hits']
            print(len(res))
            ret = {
                "code": 200,
                "msg": "success",
            }
        except Exception as e:
            print('---error----', e)
            ret = {
                "code": 404,
                "result": "失败"
            }

        return JsonResponse(ret)

    def get(self, request):
        global testData2
        testData2 = np.random.uniform(-1, 1, size=32).tolist()
        old = time.time()
        print('yes')
        data = es_search(testData2)
        print('ok')

        ret = {
            "code": 200,
            "msg": "success",
            'data': data,
            'input': testData2
        }
        print('用时', time.time() - old, '秒')
        return JsonResponse(ret)


def es_search(testData):
    old = time.time()
    global es
    print(len(testData))
    index_name = ["label_vector", "image_vector", "recom_vector"]
    results = []
    for index in index_name:
        bod = {
            "size": 2,
            "query": {
                "script_score": {
                    "query": {
                        "bool": {
                            "filter": {
                                "term": {
                                    "status": "published"
                                }
                            }
                        }
                    },
                    "script": {
                        "source": "1 / (1 + l2norm(params.queryVector, doc[\'" + index + "\']))",
                        "params": {
                            "queryVector": testData
                        }
                    }
                }
            },
            "_source": [index]
        }
        print(bod)
        s = es2.search(index="test_vector", body=bod)
        results.append(s)
    print('耗时', time.time() - old, '秒')
    return results


'''创建索引'''
# result = es.indices.create(index='news', ignore=400)
# print(result)  # {'acknowledged': True, 'index': 'news', 'shards_acknowledged': True} acknowledged 为True表示创建成功
'''删除索引'''
# result = es.indices.delete("news", ignore=[400, 404])
# print(result) # {'acknowledged': True}
'''插入数据'''
# content = {''''''}
# index = "news"
# type = "politics"
# 1.es.create(index, type, body=content, id=1)
# 或者
# 2.es.index("news", doc_type="politics", body=data)  # ok 可以不用指定id, 参数id默认为随机创建
'''更新数据'''
# doc 必不可少
# data_doc = {'doc': {'date': '2018-01-05 12:30:00',
#   'title': 'asd123',
#   'url': 'http://view.news.qq.com/zt2011/usa_iraq/index.htm'}}
# 1.result = es.update(index='news', doc_type='politics', body=data, id=1)  # ok
# print(result)
# 或者
# data = {'date': '2018-01-05 12:30:00',
#  'title': 'asd123',
#  'url': 'http://view.news.qq.com/zt2011/usa_iraq/index.htm'}  # ok 使用data_doc也ok
# 2.es.index(index='news', doc_type='politics', body=data, id=1)
'''删除数据'''
# result = es.delete("news", "politics", id='vNaqc2cBE_LRbsBxQ94C')  # ok
