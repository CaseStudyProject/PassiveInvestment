# -*-encoding:utf-8-*-

import os
import pandas as pd
from pandas import ExcelWriter
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt

import basic_function as bf

# file_path = ["./Data1.xlsx", './Data2.xlsx']
file_path = ['./DataInfo.xlsx']
# Wind Data
# StockNameDict = {'1088':'中国神华', '0101':'恒隆地产', '1398':'工商银行', '0011':'恒生银行', '0388':'香港交易所', '1299':'友邦保险', '0939':'建设银行', '2318':'中国平安', '0700':'腾讯控股', '0005':'汇丰控股'}
# Thomson Reuters
StockNameDict = {'0005':'汇丰控股', '1088':'中国神华', '0388':'香港交易所', '1299':'友邦保险', '0700':'腾讯控股', '0939':'建设银行', '0011':'恒生银行', '0101':'恒隆地产', '2318':'中国平安', '1398':'工商银行'}

# Input data
StartYM = input('pls input start year-month("yyyy-mm"):')
# StartYM = '2019-01'
# StockSelectNum = input('pls input stock select amount:')
StockSelectNum = 5

DfList = []
for i in file_path:
    df = pd.read_excel(i, encoding='utf-8')
    DfList.append(df)
    print(df.head())
    print(df.columns.values)

# # 1 correlation between changes in each stocks and Heng Seng Index
# AfterYM = '2019-01'
# period = 3
# corrDFlist = bf.StockHSCorr(AfterYM, period, DfList)
#
# for i in corrDFlist:
#     print(i)

# 2 Everyday performance
# classification
StockNum = []
PWinDays = []
PLossDays = []
NWinDays = []
NLossDays = []
PWinScope = []
PLossScope = []
NWinScope = []
NLossScope = []
for i in DfList:
    i = i[i['YM']>=StartYM]
    headname_chg = []
    headname_trnd = []
    for j in i.columns.values:
        if "ChgDiff" in j:
            headname_chg.append(j)
        elif "Trend" in j:
            headname_trnd.append(j)

    for e, j in enumerate(headname_trnd):
        df = i[['label', 'YM', 'ULindex', headname_chg[e], j]]
        UpTrendDF = df[df['ULindex']==1]
        DownTrendDF = df[df['ULindex']==0]

        # print(j[-4:])
        StockNum.append(j[-4:])
        '''
        相对优势概念
        涨势有优势，跌势有优势 - 即可盈利，亦可抗风险
        涨势有优势，跌势无优势 - 只可盈利，不可抗风险
        涨势无优势，跌势有优势 - 不可盈利，但可抗风险
        涨势无优势，跌势无优势 - 不可盈利，亦不可抗风险 
        '''
        # 2.1 Up Trend
        SameTrend = UpTrendDF[UpTrendDF[j]==0]
        sametrend_array = np.array(SameTrend[headname_chg[e]])
        indicator1 = sametrend_array>0
        indicator2 = sametrend_array<=0
        DiffTrend = UpTrendDF[UpTrendDF[j]==-1]
        difftrend_array = np.array(DiffTrend[headname_chg[e]])
        print('winning days:', sum(indicator1), 'total win:', sum(indicator1 * sametrend_array))
        print('losing days:', sum(indicator2) + sum(difftrend_array<=0), 'total lose:', sum(indicator2 * sametrend_array) + sum(difftrend_array))

        PWinDays.append(sum(indicator1))
        PLossDays.append(sum(indicator2) + sum(difftrend_array<=0))
        PWinScope.append(round(sum(indicator1 * sametrend_array), 3))
        PLossScope.append(round(sum(indicator2 * sametrend_array) + sum(difftrend_array), 3))

        # 2.2 Down Trend
        SameTrend = DownTrendDF[DownTrendDF[j]==0]
        sametrend_array = np.array(SameTrend[headname_chg[e]])
        indicator1 = sametrend_array>0
        indicator2 = sametrend_array<=0
        DiffTrend = DownTrendDF[DownTrendDF[j]==1]
        difftrend_array = np.array(DiffTrend[headname_chg[e]])
        print('winning days:', sum(indicator1) + sum(difftrend_array>0), 'total win:', sum(indicator1 * sametrend_array) + sum(difftrend_array))
        print('losing days:', sum(indicator2), 'total lose:', sum(indicator2 * sametrend_array))

        NWinDays.append(sum(indicator1) + sum(difftrend_array>0))
        NLossDays.append(sum(indicator2))
        NWinScope.append(round(sum(indicator1 * sametrend_array) + sum(difftrend_array), 3))
        NLossScope.append(round(sum(indicator2 * sametrend_array), 3))
        print('\n')

StockNum = pd.Series(StockNum)
PWinDays = pd.Series(PWinDays)
PLossDays = pd.Series(PLossDays)
NWinDays = pd.Series(NWinDays)
NLossDays = pd.Series(NLossDays)
PWinScope = pd.Series(PWinScope)
PLossScope = pd.Series(PLossScope)
NWinScope = pd.Series(NWinScope)
NLossScope = pd.Series(NLossScope)
CompDF = pd.concat([StockNum, PWinDays, PLossDays, NWinDays, NLossDays, PWinScope, PLossScope, NWinScope, NLossScope], axis=1)
CompDF.columns = ['StockNum', 'PWinDays', 'PLossDays', 'NWinDays', 'NLossDays', 'PWinScope', 'PLossScope', 'NWinScope', 'NLossScope']
print('CompDF:\n', CompDF)

write = ExcelWriter("AdvComp.xlsx")
CompDF.to_excel(write, 'data', index=False)
write.save()

# 3 Selection Score Calculation
# 3.1 Heng Seng Index Performance Dataframe
df = DfList[0][DfList[0]['YM']>=StartYM]
df = np.array(df['ULindex'])
PosiPecn = sum(df==1) / len(df)
NegaPecn = sum(df==0) / len(df)
print('PosiPecn:', PosiPecn, 'NegaPecn:', NegaPecn)

CompDF['PWinRate'] = CompDF['PWinScope'] / CompDF['PWinDays']
CompDF['PLossRate'] = CompDF['PLossScope'] / CompDF['PLossDays']
CompDF['NWinRate'] = CompDF['NWinScope'] / CompDF['NWinDays']
CompDF['NLossRate'] = CompDF['NLossScope'] / CompDF['NLossDays']
CompDF['PWL'] = CompDF['PWinRate'] / (-CompDF['PLossRate'])
CompDF['NWL'] = CompDF['NWinRate'] / (-CompDF['NLossRate'])
CompDF['FScore'] = CompDF['PWL'] / PosiPecn + CompDF['NWL'] / NegaPecn
rank = CompDF[['StockNum', 'FScore', 'PWL', 'NWL']].sort_values('FScore', ascending=False).reset_index(drop=True)
rank['FScore_rank'] = rank['FScore'].rank(ascending=False)
rank['PWL_rank'] = rank['PWL'].rank(ascending=False)
rank['NWL_rank'] = rank['NWL'].rank(ascending=False)

StockNameDf = pd.DataFrame(StockNameDict, index=[0]).T.reset_index()
StockNameDf.columns = ['StockNum', 'StockName']
rank = pd.merge(rank, StockNameDf, on='StockNum', how='inner')#.iloc[:5, :]
print('rank:\n', rank)

write = ExcelWriter('SelectedStocks.xlsx')
rank.to_excel(write, 'data', index=False)
write.save()

# 4 Calculate the proportion
for i in ['FScore', 'PWL', 'NWL']:
    tmp = np.array(rank[i])
    rank['std_'+i] = list(bf.min_man_scale(tmp))

tmp = rank.iloc[:StockSelectNum, -4:]
weighted = np.array(tmp['std_FScore']) * 0.3 + np.array(tmp['std_PWL']) * 0.4 + np.array(tmp['std_NWL']) * 0.3
basesum = sum(weighted)
Proportion = weighted / basesum
tmp['proportion'] = list(Proportion)
tmp = pd.merge(tmp, StockNameDf, on='StockName', how='inner')

PriceDict = {}
for i in range(len(tmp)):
    price = input('The current price of stock (%s,%s) is'%(tmp['StockName'][i], tmp['StockNum'][i]))
    PriceDict[i] = float(price)
maxPriceInd = list(PriceDict.keys())[list(PriceDict.values()).index(max(PriceDict.values()))]
sumValue = max(PriceDict.values()) / tmp['proportion'][maxPriceInd]
print('sumValue:', sumValue)

AmountList = []
for i in range(len(tmp)):
    value = sumValue * tmp['proportion'][i]
    amount = round(value / PriceDict[i],2)
    AmountList.append(amount)
print(AmountList)
tmp.insert(len(tmp.columns.values), 'amount', AmountList)

print('tmp:\n', tmp)