# -*- coding:utf-8 -*-
# author:LJ

# 通过POITYPE获取
import csv
import os
import math
import requests
import pandas as pd
from geocoding_amap import geocodeamap_v2


# 打网格('116.460988,40.007381, 116.48231,40.006919')左上右下
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


def get_poi(poitype_keywordj, locationi, url_x):
    api_keys = ["你的key"]

    maxpage = 50  # 设置最多页数为10页（官方限定100页）
    offset = 25  # 实例设置每页展示10条POI（官方限定25条）
    page = 1

    while page < maxpage + 1:
        print('爬取第%s页！' % page)
        # typei = type(eval(poitype_keywordj))
        # print(poitype_keywordj, typei)
        url = "https://restapi.amap.com/v3/place/polygon?polygon=%s&%s=%s&page=%s&output=json&key=%s" \
              % (locationi, url_x, poitype_keywordj, page, api_keys[3])

        try:
            res=requests.get(url)
            res_js=res.json()
            # print(res_js)
            pois=res_js['pois']
            # print(pois)
            if len(pois) > 0:
                for i in range(0, len(pois)):  # len(pois)
                    poi_id=pois[i]['id']
                    poi_name = pois[i]['name']
                    poi_type = pois[i]['type']
                    poi_typecode = pois[i]['typecode']
                    poi_biz_type = pois[i]['biz_type']
                    try:
                        poi_address = pois[i]['address']
                    except:
                        poi_address = "***"
                    poi_location = pois[i]['location']
                    poi_tel = pois[i]['tel']
                    poi_pname = pois[i]['pname']
                    poi_cityname = pois[i]['cityname']
                    # print(id, cityname)
                    pois_infoi = [poi_id, poi_name, poi_type, poi_typecode, poi_biz_type, poi_address,
                                  poi_location, poi_tel, poi_pname, poi_cityname]
                    # 'id', 'name', 'type', 'typecode', 'biz_type', 'address', 'location', 'tel',
                    #                                     'pname', 'cityname']
                    # print(xq_infos_i)
                    csv_write.writerow(pois_infoi)
            else:
                break  # 如果数量为0，认为POI已经爬完
            # print(id, cityname)
        except Exception as e:
            print(e) # 设置错误输出z

        page += 1


def wgs(lngs, lats):
    '''对地理编码进行纠偏'''
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
    # 设置POI类型
    poitypes_keywords = [110200, 170400, '门球', '羽毛球', 170000]  #　170100
    # 设置左上和右下116.460988,40.106919|116.48231,40.007381
    locations = [('116.460988,40.106919,116.48231,40.007381'),
                 ('120.798416,31.468341,122.009658,30.696816'),
                 ('121.306363,31.173686,121.425839,31.077876')]
    # 路径设置
    basepath = os.getcwd() + "\\amap_poi\\"
    for i in range(2, len(locations)):
        locationi = locations[i]
        print(locationi)
        df_loc = pd.DataFrame()
        for j in range(4, 5):  # len(poitypes_keywords)
            poitype_keywordj = poitypes_keywords[j]
            print(poitype_keywordj)
            # 设置保存文件名
            filename = basepath + str(poitype_keywordj) + '&' + str(locationi) + '.csv'
            # filename1 = filename.replace('.csv', '_1.csv')
            filetmp = basepath + locationi + '.csv'
            print(filename)

            '''分割区域'''
            # divd = 0.02  # 划分网络的大小0.05，与页数有关
            # locs = LocaDiv(locationi, divd).ls_row()  # ls_com(),ls_row(),lng_all(),lat_all()
            # # print(locs)
            # df_locs = pd.DataFrame({"locs": locs})
            # df_locs.to_csv(filetmp, sep=',', encoding='utf-8')
            # print("已将分割信息写入%s文件！" % filetmp)

            '''爬取POIS'''
            # locs1 = pd.read_csv(filetmp, encoding='utf-8')["locs"].to_list()
            #
            # try:
            #     if poitype_keywordj > 0:
            #         print('按POITYPE爬取！')
            #         url_x = 'types'
            #     else:
            #         pass
            # except:
            #     print('按KEYWORD爬取！')
            #     url_x = 'keywords'
            #
            # with open(filename, 'a+', newline='') as f:
            #     csv_write = csv.writer(f)
            #     csv_write.writerow(['id', 'name', 'type', 'typecode', 'biz_type', 'address', 'location', 'tel',
            #                         'pname', 'cityname'])  # '参考月份',, '在售链接', '成交链接'
            #
            #     # 逐行将POI写入CSV
            #     for x in range(0, len(locs1)):  # len(locs1)
            #         print(x)
            #         loci = locs1[x]
            #         get_poi(poitype_keywordj, loci, url_x)

            '''坐标纠偏'''
            lngs1, lats1 = [[] for i in range(2)]
            df_loc0_1 = pd.read_csv(filename, encoding='ANSI', index_col=0)  #
            # print(df_loc0_1.head())
            list_location = df_loc0_1['location'].to_list()
            # print(list_location)
            for y in range(0, len(list_location)):  # len(list_location)
                print(y)
                location_y = list_location[y].split(",")
                # print(location_y)
                try:
                    lngs, lats = location_y[0], location_y[1]
                    # print(lngs, lats)
                    lngsi, latsi = wgs(lngs, lats)
                    # print(lngsi, latsi)
                except:
                    lngsi, latsi = '***', '***'
                    continue
                lngs1.append(lngsi)
                lats1.append(latsi)
            df_wgs = pd.DataFrame({"lng_wgs": lngs1, "lat_wgs": lats1})
            df_loc0_2 = pd.concat([df_loc0_1, df_wgs], axis=1)
            print(df_loc0_2.head())
            df_loc0_2.to_csv(filename, encoding='ANSI')

    print("POI爬取完毕！")