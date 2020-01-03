# Create your views here.

from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
import elasticsearch
import json, requests
from elasticsearch import Elasticsearch, helpers
import django

print('django版本', django.VERSION)

from random import randrange

# Create your views here.
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


class ShowView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/review_task2.html").read())

class ShowViewTest(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./templates/review.html").read())


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


def date_agg(timeType):
    global es
    if timeType == "month":
        mat = "yyyy年MM月"
    elif timeType == "day":
        mat = "yyyy年MM月dd日"
    else:
        mat = "yyyy-MM-dd HH时"
    body = {
        "track_total_hits": 10000000,
        "aggs": {
            "date": {
                "date_histogram": {"field": "updateTime", "interval": timeType, "format": mat}
            }
        }
    }
    s = es.search(index="review_recs",  # 索引名
                  body=body)
    buckets = s['aggregations']['date']['buckets']
    return buckets


def merchant_agg(type, agg_name, top_num, key):
    global es
    body = {
        "track_total_hits": 1000000,
        "query": {
            "match_phrase": {
                "merchantName": key
            }
        },
        "aggs": {
            "agg_count": {
                "terms": {"field": agg_name, "size": 1000}
            }
        }
    }
    if type == "typeMerchant":
        body['query'] = {
            "match_phrase": {
                "merchantName": key
            }
        }
    elif type == "typeOperator":
        body['query'] = {
            "match_phrase": {
                "operator": key
            }
        }
    s = es.search(index="review_recs", body=body)

    buckets = s['aggregations']['agg_count']['buckets'][:top_num]
    allcount = s['hits']['total']['value']

    ##value_list = [x['doc_count'] for x in buckets]
    return buckets, allcount


def merchant_date_agg(type, timeType, key):
    global es
    if timeType == "month":
        mat = "yyyy年MM月"
    elif timeType == "day":
        mat = "yyyy年MM月dd日"
    else:
        mat = "yyyy-MM-dd HH时"
    body = {
        "track_total_hits": 1000000,
        "query": {
            "match_phrase": {
                "merchantName": key
            }
        },
        "aggs": {
            "date": {
                "date_histogram": {"field": "updateTime", "interval": timeType, "format": mat}
            }
        }
    }
    if type == "typeMerchant":
        body['query'] = {
            "match_phrase": {
                "merchantName": key
            }
        }
    elif type == "typeOperator":
        body['query'] = {
            "match_phrase": {
                "operator": key
            }
        }
    # print(type,body)
    s = es.search(index="review_recs",  # 索引名
                  body=body)
    buckets = s['aggregations']['date']['buckets']
    # print(buckets)
    return buckets


class AggView(APIView):
    def post(self, request, *args, **kwargs):
        agg_name = request.data["agg_name"]
        top_num = int(request.data["top_num"])
        # agg_name = "merchantName.keyword"
        # agg_name = "tradeName.keyword"
        # agg_name = "operator"

        rows, allcount = aggs_count(agg_name, top_num)
        # print(rows)
        ret = {
            "code": 200,
            "msg": "success",
            "rows": rows,
            "allcount": allcount
        }

        return JsonResponse(ret)


class DateView(APIView):
    def post(self, request, *args, **kwargs):
        timeType = request.data["timeType"]
        rows = date_agg(timeType)

        ret = {
            "code": 200,
            "msg": "success",
            "rows": rows,
        }

        return JsonResponse(ret)


class AuthentictionView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data["username"]
        password = request.data["password"]
        if username == "review" and password == "trbl666":
            ret = {
                "errCode": "0",
                "msg": "验证成功"
            }
        else:
            ret = {
                "errCode": "1",
                "msg": "验证失败"
            }
        return JsonResponse(ret)


class OlddayView(APIView):
    def post(self, request, *args, **kwargs):
        import datetime

        today = datetime.date.today()
        day1 = datetime.timedelta(days=90)
        day2 = datetime.timedelta(days=0)
        startday = (today - day1).strftime("%Y-%m-%d") + " 00:00:00"
        endday = (today - day2).strftime("%Y-%m-%d") + " 00:00:00"

        def get_count(day):
            body = {
                "track_total_hits": 1000000,
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "range": {
                                    "updateTime": {
                                        # "gte":  startday,
                                        "lt": day
                                    }
                                }
                            }
                        ]
                    }
                },
                "aggs": {
                    "hist_merchant": {
                        "terms": {"field": "merchantName.keyword", "size": 1000}
                    }
                }
            }
            s = es.search(index="review_recs",  # 索引名
                          body=body)
            buckets = s['aggregations']['hist_merchant']['buckets']
            return buckets

        def get_count_after(day):
            body = {
                "track_total_hits": 1000000,
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "range": {
                                    "updateTime": {
                                        # "gte":  startday,
                                        "gt": day
                                    }
                                }
                            }
                        ]
                    }
                },
                "aggs": {
                    "hist_merchant": {
                        "terms": {"field": "merchantName.keyword", "size": 1000}
                    }
                }
            }
            s = es.search(index="review_recs",  # 索引名
                          body=body)
            buckets = s['aggregations']['hist_merchant']['buckets']
            return buckets

        new_merchantList = []
        old_merchantList = []

        active_merchantList = []
        loss_merchantList = []
        volList = []
        rateList = []
        buck1 = get_count(startday)
        buck2 = get_count(endday)
        buck3 = get_count_after(startday)
        for item in buck3:
            active_merchantList.append(item['key'])
        for item1 in buck1:
            old_merchantList.append(item1["key"])
        for item in buck1:
            if item['key'] not in active_merchantList:
                loss_merchantList.append(item)
        for item2 in buck2:
            if item2['key'] not in old_merchantList:
                new_merchantList.append(item2)

        for item1 in buck1:
            for item2 in buck2:
                if item1['key'] == item2['key']:
                    vol = item2['doc_count'] - item1['doc_count']
                    volList.append(vol)
                    rateList.append(vol / item1['doc_count'])
                    break
        # print(len(buck1))
        # print(len(buck2))
        # print(len(active_merchantList))

        ret = {
            "new_merchant": new_merchantList[:12],
            "loss_merchant": loss_merchantList[:12],
            "startday": startday,
            "rateList": rateList,
            "volList": volList
        }
        return JsonResponse(ret)


class merchantView(APIView):
    def post(self, request, *args, **kwargs):
        key = request.data['key']
        timeType = request.data['timeType']
        type = request.data['type']
        # print(key,timeType)
        rows = merchant_date_agg(type, timeType, key)
        ret = {
            'rows': rows
        }
        return JsonResponse(ret)


class merchant_aggView(APIView):
    def post(self, request, *args, **kwargs):
        agg_name = request.data["agg_name"]
        top_num = int(request.data["top_num"])
        key = request.data['key']
        type = request.data["type"]
        rows, allcount = merchant_agg(type, agg_name, top_num, key)
        ret = {
            'rows': rows,
            "allcount": allcount
        }
        return JsonResponse(ret)


class IndexView(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content=open("./static/feature_check3.html", 'rb').read())


class GetAll(APIView):
    def post(self, request, *args, **kwargs):
        global es

        def get_exists_field(model_field, interval, term_list, now_page):
            global es
            review_field = model_field[1:]
            body = {
                "track_total_hits": 100000000,
                "query": {
                    "bool": {
                        "must": [
                            {"exists": {"field": model_field}},
                            {"exists": {"field": review_field}},
                            {"exists": {"field": "updateTime"}}
                        ]
                    }
                },
                "aggs": {
                    "merchant": {
                        "terms": {
                            "field": "merchantName.keyword",
                            "size": 1002
                        }
                    },
                    "typ": {
                        "terms": {
                            "field": "typ.keyword",
                            "size": 100
                        }
                    },
                    "trade": {
                        "terms": {
                            "field": "tradeName.keyword",
                            "size": 1000
                        }
                    },
                    "date": {
                        "date_histogram": {
                            "field": "updateTime",
                            "calendar_interval": interval
                        }
                    }
                },
                "from": 0,
                "size": now_page
            }

            if len(term_list) != 0:
                for term in term_list:
                    term_field = {
                        "term": {
                            "{}.keyword".format(term['term_key']): {
                                "value": term['term_value']
                            }
                        }
                    }
                    body["query"]["bool"]["must"].append(term_field)

            s = es.search(index="review_pic_features",  # 索引名
                          body=body,
                          request_timeout=60)
            doc_count = s["hits"]["total"]["value"]
            date_buckets = s["aggregations"]["date"]["buckets"]
            return doc_count, date_buckets

        def get_change_field(model_field, interval, term_list, now_page):
            global es
            review_field = model_field[1:]
            body = {
                "track_total_hits": 100000000,
                "query": {
                    "bool": {
                        "must": [
                            {"exists": {"field": model_field}},
                            {"exists": {"field": review_field}},
                            {"exists": {"field": "updateTime"}}
                        ],
                        "filter": {
                            "script": {
                                "script": {
                                    "source": "doc['{}.keyword'] != doc['{}.keyword']".format(model_field,
                                                                                              review_field),
                                    "lang": "painless"
                                }
                            }
                        }
                    },
                },
                "aggs": {
                    "merchant": {
                        "terms": {
                            "field": "merchantName.keyword",
                            "size": 1002
                        }
                    },
                    "typ": {
                        "terms": {
                            "field": "typ.keyword",
                            "size": 100
                        }
                    },
                    "trade": {
                        "terms": {
                            "field": "tradeName.keyword",
                            "size": 1000
                        }
                    },
                    "date": {
                        "date_histogram": {
                            "field": "updateTime",
                            "calendar_interval": interval
                        }
                    }
                },
                "sort": [{
                    "updateTime": {
                        "order": "desc"
                    }
                }],
                "from": now_page,
                "size": 30
            }

            if len(term_list) != 0:
                for term in term_list:
                    term_field = {
                        "term": {
                            "{}.keyword".format(term['term_key']): {
                                "value": term['term_value']
                            }
                        }
                    }
                    body["query"]["bool"]["must"].append(term_field)
            s = es.search(index="review_pic_features",  # 索引名
                          body=body,
                          request_timeout=60)
            doc_count = s["hits"]["total"]["value"]
            doc_source = s["hits"]["hits"]
            date_buckets = s["aggregations"]["date"]["buckets"]
            merchant_buckets = s["aggregations"]["merchant"]["buckets"]
            trade_buckets = s["aggregations"]["trade"]["buckets"]
            typ_buckets = s["aggregations"]["typ"]["buckets"]
            return doc_count, doc_source, date_buckets, merchant_buckets, trade_buckets, typ_buckets

        model_field = request.data["model_field"]
        interval = request.data["interval"]
        term_list = request.data["term_list"]
        now_page = request.data["now_page"]
        now_page = now_page * 30
        # print("!!!!!!!!!!!",model_field,interval,term_list,now_page)
        try:
            term_flag = request.data["term_flag"]
        except:
            if len(term_list) == 0:
                ret = es.get(index="review_feature_temp", id=model_field + '_' + interval)["_source"]
                return JsonResponse(ret)
        change_count, change_source, change_date_agg_bucket, merchant_buckets, trade_buckets, typ_buckets = get_change_field(
            model_field, interval, term_list, now_page)
        exists_count, exists_date_agg_bucket = get_exists_field(model_field, interval, term_list, now_page)
        test_count = 0
        for item in exists_date_agg_bucket:
            test_count += item["doc_count"]
        # print(test_count)
        # print("最新改正率：{}".format(change_count/exists_count))
        # print(change_count,exists_count)
        # print(change_date_agg_bucket[-1]['key_as_string'])
        # print(exists_date_agg_bucket[-1]['key_as_string'])
        if len(change_date_agg_bucket) != 0:
            c_r_date_agg_bucket = []
            p_change_count = 0
            p_exists_count = 0
            j = 0
            head_value = change_date_agg_bucket[0]['key']
            end_value = change_date_agg_bucket[-1]['key']

            # 统一时间聚合桶的长度，以存在记录的为准，无修改记录的当日记录为0
            for i in range(len(exists_date_agg_bucket)):
                if exists_date_agg_bucket[i]['key'] < head_value:
                    rec = exists_date_agg_bucket[i].copy()
                    rec['doc_count'] = 0
                    change_date_agg_bucket.insert(j, rec)
                    j += 1
                elif exists_date_agg_bucket[i]['key'] > end_value:
                    rec = exists_date_agg_bucket[i].copy()
                    rec['doc_count'] = 0
                    change_date_agg_bucket.append(rec)
            # 统计每个时间点的改正率
            for c_doc, e_doc in zip(change_date_agg_bucket, exists_date_agg_bucket):
                p_change_count += c_doc['doc_count']
                p_exists_count += e_doc['doc_count']
                rate_rec = {
                    "key_as_string": e_doc["key_as_string"],
                    "key": e_doc["key"],
                    "doc_count": p_change_count / p_exists_count
                }
                c_r_date_agg_bucket.append(rate_rec)
            # print(p_change_count,p_exists_count)
        else:
            c_r_date_agg_bucket = []

        ret = {"change_count": change_count,
               "change_source": change_source,
               "c_r_date_agg_bucket": c_r_date_agg_bucket,
               "merchant_buckets": merchant_buckets,
               "trade_buckets": trade_buckets,
               "typ_buckets": typ_buckets
               }
        return JsonResponse(ret)


class GetAllData(APIView):
    def post(self, request, *args, **kwargs):
        request_data = request.data
        choose_merchant = request_data['merchant_data']
        choose_typ = request_data['typ_data']
        choose_field = request_data['field_data']
        choose_tradeName = request_data['tradeName_data']
        choose_interval = request_data['interval_data']
        param = {
            "model_field": '_' + choose_field,
            "term_list": [],
            "interval": choose_interval,
            "now_page": 0
        }

        if choose_merchant != 'unlimited':
            param['term_list'].append({"term_key": "merchantName", "term_value": choose_merchant})
        if choose_typ != 'unlimited':
            param['term_list'].append({"term_key": "typ", "term_value": choose_typ})
        if choose_tradeName != 'unlimited':
            param['term_list'].append({"term_key": "tradeName", "term_value": choose_tradeName})
        param = json.dumps(param)
        headers = {"Content-Type": "application/json"}
        response = requests.post('http://0.0.0.0:8080/review/v1/get_all/', data=param, headers=headers)
        # print(response.text)
        response = json.loads(response.text)
        merchant_data = []
        typ_data = []
        tradeName_data = []
        change_count = response['change_count']
        line_data = response['c_r_date_agg_bucket']
        for merchant in response['merchant_buckets']:
            merchant_data.append((merchant['key'], merchant['doc_count']))
        for typ in response['typ_buckets']:
            typ_data.append((typ['key'], typ['doc_count']))
        for tradeName in response['trade_buckets']:
            tradeName_data.append((tradeName['key'], tradeName['doc_count']))
        img_data = []
        if choose_field == 'face_outline' or choose_field == 'cloth_outline' or choose_field == 'body_outline':
            for img in response['change_source']:
                img = img['_source']
                img_data.append(
                    (img['merchantName'], img['operator'], img['url'], img['_' + choose_field], img[choose_field],
                     img['updateTime']))
        else:
            for img in response['change_source']:
                img = img['_source']
                img_data.append(
                    (img['merchantName'], img['operator'], img['url'], img['_' + choose_field], img[choose_field],
                     img['updateTime']))
        ret = {
            "change_count": change_count,
            "merchant_data": merchant_data,
            "typ_data": typ_data,
            "tradeName_data": tradeName_data,
            "line_data": line_data,
            "img_data": img_data
        }
        return JsonResponse(ret, safe=False)
