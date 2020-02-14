# -*-encoding:utf-8 -*-

import os
import pandas as pd
import numpy as np

def DescData(array):
    '''
    To calculate the max, min, mean, var of the data array
    :param array: target array
    :return: max, min, mean, var
    '''
    maxValue = round(max(array), 3)
    minValue = round(min(array), 3)
    meanValue = round(np.mean(array), 3)
    varValue = round(np.var(array), 3)
    return maxValue, minValue, meanValue, varValue


def AvgPrd(df, datename, volvarname):
    '''
    To calculate the average change according to the week's trading situation
    :param df: change of price dataframe with trading date
    :param datename: the column name of the trading date
    :param volvarname: the column name of the change of price name
    :return: each trading week's average changing price
    '''
    df_array = np.array(df[datename])
    # print(df_array)
    label = 0
    label_list = []
    date_list = [str(df_array[0])[:7]]
    for i in range(len(df)-1):
        DayDiff = np.timedelta64(df_array[i+1]-df_array[i], 'D')
        # print(DayDiff, DayDiff>np.timedelta64(1, 'D'))
        if DayDiff>np.timedelta64(1, 'D'):
            label += 1
            date_list.append(str(df_array[i])[:7])
        label_list.append(label)
    if np.timedelta64(df_array[len(df_array)-2]-df_array[len(df_array)-1], 'D')>np.timedelta64(1, 'D'):
        label_list.append(label)
        date_list.append(str(df_array[len(df_array)-1])[:7])
    else:
        label_list.append(label+1)
        date_list.append(str(df_array[len(df_array)-1])[:7])
    df.insert(0, 'label', label_list)

    PivotTable = pd.pivot_table(df[['label', volvarname]], values=[volvarname], index=['label'], aggfunc={volvarname:np.mean}).reset_index(drop=False)
    PivotTable.insert(1, 'YM', date_list)
    return PivotTable


def AvgPrd2(df, IndicatorName, DateName, PriceChgName):
    '''
    To calculate the average change according to the week's trading situation
    :param df: Dataframe with indicator,and change of price
    :param IndicatorName: The indicator that indicates the continuous trading period
    :param DateName: The trading date column name
    :param PriceChgName: The change of price column name
    :return: The average price change of the trading period
    '''
    tmp = df[IndicatorName]
    LabelList = []
    label = 0
    for i in tmp:
        if i==0:
            LabelList.append(label)
        else:
            label += 1
            LabelList.append(label)
    df.insert(0, 'label', LabelList)

    PivotTable = pd.pivot_table(df[['label', DateName, PriceChgName]], values=[PriceChgName], index=['label', DateName], aggfunc={PriceChgName:np.mean}).reset_index(drop=False)
    return PivotTable

# YearMonth Select
def YMSel(AfterYM, period, df, DT_list):
    '''
    Select period of data according to pointed year and month
    :param AfterYM: The start year and month
    :param period: The extracted period, counted according to months
    :param df: The original dataframe
    :param DT_list: The datetime of the original dataframe
    :return: The list of extracted dataframe
    '''
    DT_sel = [i for i in DT_list if i >= AfterYM][::-1]
    SelDFList = []
    for i in DT_sel[:-2]:
        startdate = i[:5] + str('0' + str(int(i[5:])-period) if int(i[5:])-period<10 else str(int(i[5:])-period))
        tmpdf = df[(df['YM']<=i) & (df['YM']>startdate)]
        SelDFList.append(tmpdf)
    return SelDFList

# Correlation dataframe
def StockHSCorr(AfterYM, period, DfList):
    '''
    To construct a dataframe describes the correlation between each stocks and Heng Seng Index according to different period of time
    :param AfterYM: The start year and month
    :param period: The extracted period, counted according to months
    :param DfList: The original dataframe list
    :return: the correlation dataframe of each stocks and Heng Seng Index in different period of time
    '''
    corrDFlist = []
    for k in DfList:
        DT_list = sorted(list(set(list(k['YM']))))

        SelDFList = YMSel(AfterYM, period, k, DT_list)
        # Acquire target features
        TargetFeatures = [i for i in SelDFList[0].columns.values if 'Chg' in i]
        # Correlation between target features in different period of time
        corrList = []
        for i in SelDFList:
            df = i[TargetFeatures]
            corr = df.corr()
            corrList.append(corr)
        # Correlation changes in certain period of time
        headnameList = list(corrList[0].columns.values)[1:]
        headnameList.insert(0, 'DT')
        CorrInfoDF = []
        DT_sel = [i for i in DT_list if i >= AfterYM][::-1]
        for e, i in enumerate(DT_sel[:-2]):
            df = corrList[e]
            OrgList = list(df.iloc[1:, 0])
            OrgList.insert(0, i)
            CorrInfoDF.append(pd.DataFrame(OrgList))
        CorrInfoDF = pd.concat(CorrInfoDF, axis=1).T
        CorrInfoDF.columns = headnameList
        CorrInfoDF = CorrInfoDF.set_index('DT', drop=True)
        corrDFlist.append(CorrInfoDF)
    return corrDFlist

def min_man_scale(array):
    '''
    Input the original data array, return the scaled array
    :param array: original array, in array type
    :return: the scaled array
    '''
    Amin = np.min(array)
    Amax = np.max(array)
    ScaleData = (array - Amin) / (Amax - Amin)
    return ScaleData


def TimeAdjust(df, Time):
    '''
    Clean up those missing data
    :param df: Original dataset
    :param Time: The timestamp that want to delete in the dataframe, in datetime type
    :return: Clean up dataframe without the pointed datetime
    '''
    label_list = []
    for i in df['DateTime']:
        if i.time()==Time:
            label_list.append(1)
        else:
            label_list.append(0)
    df.insert(0, 'tmp', label_list)
    df = df[df['tmp']==0].reset_index(drop=True).drop(['tmp'], axis=1)
    return  df


def InsertTimeDiffLabel(df, dtLabelName, newlabelname):
    '''
    Insert Label that indicates the continous trading period
    :param df: Target dataframe
    :param dtLabelName: Datetime column name of the original data
    :param newlabelname: The indicator name
    :return: New dataframe with the indicator
    '''
    datalist = list(df[dtLabelName])
    datalist2 = datalist[1:]
    datalist = datalist[:-1]
    TimeDiffLabel = []
    for e, i in enumerate(datalist):
        if np.timedelta64(datalist2[e] - i, 'm')==np.timedelta64(30, 'm'):
            TimeDiffLabel.append(0)
        else:
            TimeDiffLabel.append(1)
    df = df.iloc[1:, :]
    DTlist = []
    for i in datalist2:
        DTlist.append(np.datetime64(i, 'D'))
    df.insert(1, newlabelname, TimeDiffLabel)
    df = df.drop(dtLabelName, axis=1).reset_index(drop=True).reset_index(drop=False)
    df.insert(2, dtLabelName, DTlist)
    return df