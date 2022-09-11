# -*- coding:utf-8 -*-
# author:LJ

# 通过POITYPE获取，改为逐行写入CSV

import os
import math
import requests
import pandas as pd
from datetime import datetime
from geocoding_amap import geocodeamap_v2
import json
import csv


# 打网格,左上右下
class LocaDiv(object):
    def __init__(self, loc_all, divd):
        self.loc_all = loc_all
        self.divd = divd

    def lng_all(self):
        lng_nw = float(self.loc_all.split(',')[0])  # 左上，西北
        lng_es = float(self.loc_all.split(',')[2])  # 右下，东南
        # print(lng_nw, lng_es)
        lng_list = [str(lng_es)]
        while lng_es - lng_nw >= 0:
            m = lng_es - self.divd
            lng_list.append('%.2f' % m)
            lng_es = lng_es - self.divd
        return sorted(lng_list)

    def lat_all(self):
        lat_nw = float(self.loc_all.split(',')[1])
        lat_es = float(self.loc_all.split(',')[3])
        lat_list = [str(lat_nw)]
        while lat_nw - lat_es >= 0:
            m = lat_nw - self.divd
            lat_list.append('%.2f' % m)
            lat_nw = lat_nw - self.divd
        return lat_list  # 按大小排序sorted(lat_list)


    def ls_com(self):
        l1 = self.lng_all()  # 得到升序排列的经度
        l2 = self.lat_all()  # 得到升序排列的纬度
        ab_list = []
        for i in range(0, len(l1)):
            a = str(l1[i])
            for i2 in range(0, len(l2)):
                b = str(l2[i2])
                ab = a + ',' + b  # lng,lat
                ab_list.append(ab)
        return ab_list

    def ls_row(self):
        l1 = self.lng_all()
        l2 = self.lat_all()
        ls_com_v = self.ls_com()
        ls = []
        for n in range(0, len(l1) - 1):
            for i in range(len(l2) * n, len(l2) * (n + 1) - 1):
                a = ls_com_v[i]
                b = ls_com_v[i + len(l2) + 1]
                ab = a + '|' + b
                ls.append(ab)
        return ls


# 判断数量
def get_count(locationi, poitype, api_keyi):
    # 初始化网页
    page = 1
    url = "https://restapi.amap.com/v3/place/polygon?polygon=%s&types=%s&offset=%s&page=%s&output=json&key=%s" \
          % (locationi, poitype, offset, page, api_keyi)
    # print(url)
    res = requests.get(url)
    res_js = res.json()
    # print(res_js)
    count = res_js["count"]
    return count


# 预处理后爬取POI
def pre_get_poi(poitype, locs1, keynum, divd):
    global maxpage, offset
    api_keys = ["你的key列表"]
    api_keyi = api_keys[keynum]
    offset = 20  # 实例设置每页展示10条POI（官方限定25条）
    # maxpage = 30  # 设置最多页数为30页（官方限定100页）
    maxcount = 600

    i = 0
    while i < len(locs1):
        loci = locs1[i]
        # 返回数量值
        count = int(get_count(loci, poitype, api_keyi))
        print("------------------------%s初始数量为%s" % (loci, count))  # , type(count)
        if 0 < count <= maxcount:  # 如果返回数量小于最大值，执行爬取程序
            get_poi(count, loci, poitype, api_keyi)  # 执行爬取程序
        elif count > maxcount:
            print("------------------------%s初始数量超出阈值，需要进一步分割区域！" % loci)
            divd1 = divd / 2
            loci = str(loci).replace("|", ",")  # 标准化
            locs2 = LocaDiv(loci, divd1).ls_row()  # ls_com(),ls_row(),lng_all(),lat_all()  # 分割区域
            locs1.pop(i)
            [locs1.insert(i+j, locs2[j]) for j in range(len(locs2))]

        else:
            pass
        i += 1

    df_locs1 = pd.DataFrame({"locs": locs1})
    df_locs1.to_csv(filetmp, sep=',', encoding='UTF-8')
    print("------------------------已将分割信息写入%s文件！" % filetmp)


# 爬取POI
def get_poi(count, locationi, poitype, api_keyi):
    # 初始化网页
    page = 1
    pages = math.ceil(count / 20)
    print("------------------------%s共有%s页!" % (locationi, pages))
    while page <= pages:
        # print('------------------------爬取第%s页！' % page)
        url = "https://restapi.amap.com/v3/place/polygon?polygon=%s&types=%s&offset=%s&page=%s&output=json&key=%s" \
              % (locationi, poitype, offset, page, api_keyi)
        # print(url)
        try:
            res = requests.get(url)
            res_js = res.json()
            pois = res_js['pois']
            # print(pois)
            if len(pois) > 0:
                for i in range(0, len(pois)):
                    poi_id = pois[i]['id']
                    poi_name = pois[i]['name']
                    poi_type = pois[i]['type']
                    poi_typecode = pois[i]['typecode']
                    poi_biz_type = pois[i]['biz_type']
                    try:
                        poi_address = pois[i]['address']
                    except:
                        poi_address = "___"
                    poi_location = pois[i]['location']
                    poi_tel = pois[i]['tel']
                    poi_pname = pois[i]['pname']
                    poi_cityname = pois[i]['cityname']

                    poi_infos_i = [poi_id, poi_name, poi_type, poi_typecode,
                                   poi_biz_type, poi_address, poi_location, poi_tel,
                                   poi_pname, poi_cityname]  # ,img_links,pricetime,,link_zaishou,link_chengjiao
                    # print(poi_infos_i)
                    csv_write.writerow(poi_infos_i)
            else:
                pass  # 如果数量为0，认为POI已经爬完
            # print(id, cityname)
        except Exception as e:
            print(e)  # 设置错误输出z
        page += 1


'''对地理编码进行纠偏'''
def wgs(lngs, lats):
    lng=float(lngs)
    lat=float(lats)
    a=6278245.0# 克拉索夫斯基椭球参数长半轴a
    ee=0.00669342162296594323#克拉索夫斯基椭球参数第一偏心率平方
    pi=3.14159265358979324#圆周率
    # 以下为转换公式
    x = lng - 105.0
    y = lat - 35.0
    # 经度
    dlng = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    dlng += (20.0 * math.sin(6.0 * x * pi) + 20.0 * math.sin(2.0 * x * pi)) * 2.0 / 3.0
    dlng += (20.0 * math.sin(x * pi) + 40.0 * math.sin(x / 3.0 * pi)) * 2.0 / 3.0
    dlng += (150.0 * math.sin(x / 12.0 * pi) + 300.0 * math.sin(x / 30.0 * pi)) * 2.0 / 3.0
    # 纬度
    dlat = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    dlat += (20.0 * math.sin(6.0 * x * pi) + 20.0 * math.sin(2.0 * x * pi)) * 2.0 / 3.0
    dlat += (20.0 * math.sin(y * pi) + 40.0 * math.sin(y / 3.0 * pi)) * 2.0 / 3.0
    dlat += (160.0 * math.sin(y / 12.0 * pi) + 320 * math.sin(y * pi / 30.0)) * 2.0 / 3.0
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    wgslng = lng - dlng
    wgslat = lat - dlat
    return wgslng, wgslat


if __name__=='__main__':
    time_start = datetime.now()
    print('开始时间:' + str(time_start))
    print("------------------------高德POI爬取：矩形检索------------------------")

    # 设置工作环境
    configs = open(".\\config_pois.json")
    configs_datas = json.load(configs)['POIS_AMAP']
    poitypes = configs_datas["poitypes"]  # 设置POI类型
    # print(poitypes)
    locations = configs_datas["locations"]  # 设置左上和右下121.573,31.138, 121.668,30.98
    divd = configs_datas["divd"]  # 划分网络的大小0.05，与页数有关
    keynum = configs_datas["keynum"]  # key值

    # 路径设置
    basepath = os.getcwd() + "\\amap_poi\\"
    filelists = [[] for i in range(len(locations))]
    # print(filelist)

    for i in range(0, 1):  # len(locations)
        locationi = locations[i]
        filelist = filelists[i]
        print("------------------------矩形检索范围是：%s" % locationi)
        filetmp = basepath + locationi + '.csv'
        # print(filetmp)
        '''分割区域'''
        locs = LocaDiv(locationi, divd).ls_row()  # ls_com(),ls_row(),lng_all(),lat_all()
        # print(locs)
        df_locs = pd.DataFrame({"locs": locs})
        df_locs.to_csv(filetmp, sep=',', encoding='UTF-8')
        print("------------------------已将分割信息写入%s文件！" % filetmp)

        df_loc = pd.DataFrame()
        for j in range(0, len(poitypes)):  # len(poitypes)
            poitypej = poitypes[j]
            # print(poitypej)
            print("------------------------正在爬取%s类型" % poitypej)
            # 设置保存文件名
            filename = basepath + str(poitypej) + '&' + str(locationi) + '.csv'

            '''爬取POIS'''
            locs1 = pd.read_csv(filetmp, encoding='UTF-8')["locs"].to_list()

            # 写入CSV表头
            with open(filename, 'a+', newline='', encoding='UTF-8') as f:
                csv_write = csv.writer(f)
                csv_write.writerow(['id', 'name', 'type', 'typecode', 'biz_type', 'address', 'location', 'tel',
                                    'pname', 'cityname'])
                pre_get_poi(poitypej, locs1, keynum, divd)
            print("------------------------POI爬取完毕！")

            # 保存文件名到列表
            filelist.append(filename)

        '''合并同一个区域的所有类型'''
        # filelist = ["C:\\Users\\LJ\\Desktop\\061000&121.573,31.138, 121.668,30.98.csv",
        #             "C:\\Users\\LJ\\Desktop\\060400&121.573,31.138, 121.668,30.98.csv",
        #             "C:\\Users\\LJ\\Desktop\\060300&121.573,31.138, 121.668,30.98.csv",
        #             "C:\\Users\\LJ\\Desktop\\060100&121.573,31.138, 121.668,30.98.csv"]
        filenames = basepath + poitypes[0] + '_' + poitypes[-1] + '&' + locations[0] + '.csv'
        df0 = pd.DataFrame()
        for i in range(len(filelist)):
            dfi = pd.read_csv(filelist[i])
            df0 = pd.concat([df0, dfi], axis=0, ignore_index=True)
        # 数据框去重
        df0.drop_duplicates(subset=['id', 'name', 'type', 'typecode', 'biz_type', 'address', 'location', 'tel',
                                    'pname', 'cityname'],
                            keep="first")
        df0.to_csv(filenames)
        print("------------------------已合并类型！")

        '''坐标纠偏'''
        print("------------------------POI坐标纠偏中!")
        lngs1, lats1 = [[] for i in range(2)]
        df_loc0_1 = pd.read_csv(filenames, encoding='UTF-8')
        list_location = df_loc0_1['location'].to_list()
        # print(list_location)
        for y in range(0, len(list_location)):  # len(list_location)
            # print(y)
            try:
                location_y = list_location[y].split(",")
                # print(location_y)
                lngs, lats = location_y[0], location_y[1]
                # print(lngs, lats)
                lngsi, latsi = wgs(lngs, lats)
                # print(lngsi, latsi)
            except:
                lngsi, latsi = '___', '___'
                continue
            lngs1.append(lngsi)
            lats1.append(latsi)
        df_wgs = pd.DataFrame({"lng_wgs": lngs1, "lat_wgs": lats1})
        df_loc0_2 = pd.concat([df_loc0_1, df_wgs], axis=1)
        print(df_loc0_2.head())
        df_loc0_2.to_csv(filenames, encoding='UTF-8')
        print("------------------------坐标纠偏完毕！")

    time_end = datetime.now()
    print('结束时间:'+str(time_end))
    time_last = time_end - time_start
    print('用时'+str(time_last))

    # 保存参数为日志
    print("------------------------正在保存参数！")
    log_csv = ".\\logs_pois.csv"
    records = [str(time_end), configs_datas["city"], poitypes, locations]
    with open(log_csv, "a+", newline='') as f:
        csv_write = csv.writer(f)
        # csv_write.writerow(['time', 'city', 'poitypes', 'locations'])
        csv_write.writerow(records)
    print("------------------------已保存参数！")