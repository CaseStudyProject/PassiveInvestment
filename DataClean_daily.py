# -*-encoding:utf-8 -*-

import os
import pandas as pd
from pandas import ExcelWriter
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

import basic_function as bf

TimeController = '2018-01-01'
TimeLength = '_3y'
file_path = "./data"
files = os.listdir(file_path)
print([i for i in files if '_3y' in i])
tmp = {'0005':'汇丰控股', '1088':'中国神华', '0388':'香港交易所', '1299':'友邦保险', '0700':'腾讯控股', '0939':'建设银行', '0011':'恒生银行', '0101':'恒隆地产', '2318':'中国平安', '1398':'工商银行'}

target_dict = {}
for i in files:
    if TimeLength in i and 'HSIndex' not in i:
        target_dict[i[4:8]] = tmp[i[4:8]]
print('target_dict:', target_dict)


HSZSdata = pd.read_excel(file_path + "/HSIndex_3y.xlsx", sheet_name='data', encoding='utf-8')
HSZSdata = HSZSdata[['Exchange Date', '%Chg']][::-1]
HSZSdata.columns = ['DateTime', 'PriceChg']
HSZSdata = HSZSdata[HSZSdata['DateTime'] >= TimeController].reset_index(drop=True).reset_index(drop=False).iloc[1:, :]
print(HSZSdata)

dfList = []
for i in files:
    if TimeLength in i and "HSIndex" not in i:
        df = pd.read_excel(file_path + '/' + i, encoding='utf-8', sheet_name='data')
        df = df[['Exchange Date', '%Chg']][::-1]
        df.columns = ['DateTime', 'PriceChg']
        df = df[df['DateTime'] >= TimeController].reset_index(drop=True).reset_index(drop=False).iloc[1:, :]
        tmp = [i[4:8]] * len(df)
        # df.insert(3, 'StockNum', tmp)
        # print('df:\n', df.head(3))
        dfList.append(df)


def SelectStockStatD(file_path, files, target_dict, index_file):
    '''
    To calculate the target stocks' correlation with the index, prints the correlation between target stocks and index
    :param file_path: The data's file path
    :param files: the file name (xlsx name)
    :param target_dict: the stock number and name of the files, should be recorded in order
    :param index_file: the index data
    :return: correlation between target stocks and index
    '''
    for e, i in enumerate(target_dict):
        print(i, target_dict[i])
        print(dfList[e])
        maxValue, minValue, meanValue, varValue = bf.DescData(np.array(dfList[e]['PriceChg']))
        print('涨跌幅 max:', maxValue, 'min:', minValue, 'mean:', meanValue, 'var:', varValue, '\n')

    maxValue, minValue, meanValue, varValue = bf.DescData(np.array(HSZSdata['PriceChg']) * 100)
    print('800000 恒生指数\n涨跌幅 max:', maxValue, 'min:', minValue, 'mean:', meanValue, 'var:', varValue, '\n')

    index_PivTbl = bf.AvgPrd(HSZSdata, 'DateTime', 'PriceChg')
    index_PivTbl['PriceChg'] = index_PivTbl['PriceChg'] * 100

    PivotDFlist = []
    for s in dfList:
        pivotS = bf.AvgPrd(s, 'DateTime', 'PriceChg')
        pivotS.columns = ['label', 'YM', 'PriceChg']
        pivotS['PriceChg'] = pivotS['PriceChg'] * 100
        print('pivotS:\n', pivotS)
        PivotDFlist.append(pivotS)

    npCorrList = []
    for e, i in enumerate(PivotDFlist):
        npCorrMtx = np.corrcoef(np.array(index_PivTbl['PriceChg']), np.array(i['PriceChg']))
        npCorr = round(npCorrMtx[1,0], 3)
        npCorrList.append(npCorr)

    print('相关关系:')
    for e, i in enumerate(target_dict):
        print(target_dict[i], ":", npCorrList[e],'\n')

    # 涨跌势与大盘比较
    ULarray = np.array(index_PivTbl['PriceChg']>0)*1
    index_PivTbl['ULindex'] = ULarray
    print('index_PivTbl:\n', index_PivTbl)

    print('个股', '同趋势平均涨跌', '不同趋势平均涨跌(-)', '不同趋势平均涨跌(+)', '相关关系')
    for e, i in enumerate(target_dict):
        tmp = PivotDFlist[e]
        tmparray = np.array(tmp['PriceChg']>0) * 1
        tmp['ULindex'] = tmparray
        name1 = "S" + i
        name2 = "ULindex" + i
        headname = list(index_PivTbl.columns.values)
        headname.append(name1)
        headname.append(name2)
        index_PivTbl = pd.merge(index_PivTbl, tmp, on=['label', 'YM'], how='inner')
        index_PivTbl.columns = headname

        hszsPC = np.array(index_PivTbl['PriceChg']) # PriceChg 价格变动幅度
        hszsULI = np.array(index_PivTbl['ULindex']) # ULindex 价格涨/跌变动
        sP = np.array(index_PivTbl.iloc[:, -2])
        sIDX = np.array(index_PivTbl.iloc[:, -1])

        Trendcorr = sIDX-hszsULI # 同向变动/非同向变动
        ChgDiff = sP-hszsPC # 变动幅度，比起恒生指数变动幅度的变化应该是多少【个股变动幅度与恒生指数变动幅度之差】
        name1 = 'ChgDiff' + i
        name2 = 'TrendCorr' + i
        index_PivTbl[name1] = ChgDiff
        index_PivTbl[name2] = Trendcorr

        # print(HSZS_PivTbl.head(), '\n', len(HSZS_PivTbl))
        sameTrend = round(sum(np.array(index_PivTbl[name1][index_PivTbl[name2]==0])),3)
        PoorTrend = round(sum(np.array(index_PivTbl[name1][index_PivTbl[name2]==-1])),3)
        GoodTrend = round(sum(np.array(index_PivTbl[name1][index_PivTbl[name2]==1])),3)
        print(target_dict[i], sameTrend, PoorTrend, GoodTrend, npCorrList[e])

    return index_PivTbl

Data = SelectStockStatD(file_path, files, target_dict, HSZSdata)
print('Data:\n', Data)

write = ExcelWriter('DataInfo.xlsx')
Data.to_excel(write, 'data', index=False)
write.save()