#                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 10:31:45 2018

@author: DihengChen
"""

import get_data
import generate_signals
import numpy as np
import pandas as pd
pd.options.display.max_colwidth = 60
%matplotlib inline
import matplotlib.pyplot as plt
from IPython.core.pylabtools import figsize
figsize(25, 7)
import seaborn as sns
import itertools
import datetime
period=[8,16,32,24,48,96]
G10_daily = get_data.currency()
print(G10_daily.get_all_symbols())
G10_daily_category=['DEXUSAL','DEXCAUS','DEXSZUS','DEXUSUK','DEXJPUS',\
                    'DEXNOUS','DEXUSNZ','DEXSDUS']
data_dict=G10_daily.get_currency(G10_daily_category)

for i in range(len(G10_daily_category)):
    index=G10_daily_category[i]
    data_dict[index].value.fillna(method='pad',inplace=True)
    #del duplicate data
    dup=data_dict[index].duplicated('date')
    data_dict[index]=data_dict[index][~dup]
    #use USD as basic currency
    if i in [0,3,5,8]:
        data_dict[index].value=1/data_dict[index].value

#if date is all the same
for j,k in itertools.combinations(range(len(G10_daily_category)),2):
    if(sum(data_dict[G10_daily_category[j]].date!=\
              data_dict[G10_daily_category[k]].date)>0):
        print('Dates of dataset '+G10_daily_category[j]+' and '+\
              G10_daily_category[k]+' are different')

date=data_dict[list(data_dict.keys())[0]].date

def EMA_dict_cal(FX):
    return {i:FX.ewm(alpha=1/i,adjust=False).mean() 
                for i in period}

def signal_u(X,price):
    std1=price.rolling(63).std(ddof=0)
    #substitute 0 to 10e-6
    std1.replace(0,10e-6,inplace=True)
    Y=X/std1
    std2=Y.rolling(252).std(ddof=0)
    std2.replace(0,10e-6,inplace=True)
    Z=Y/std2
    U=Z*np.exp(-Z**2/4)/np.sqrt(2)/np.exp(-0.5)
    return U

def signal_sum(EMA_dict,period_,price):
    X1=EMA_dict[period_[0]]-EMA_dict[period_[3]]
    X2=EMA_dict[period_[1]]-EMA_dict[period_[4]]
    X3=EMA_dict[period_[2]]-EMA_dict[period_[5]]
    return (signal_u(X1,price)+signal_u(X2,price)+signal_u(X3,price))/3

signal_df=pd.DataFrame()
for index in G10_daily_category:
    EMA_dict_temp=EMA_dict_cal(data_dict[index].value) 
    signal_df[index]=signal_sum(EMA_dict_temp,period,data_dict[index].value)
signal_df.set_index(date,inplace=True)
signal_df.dropna(inplace=True)

price_df=pd.DataFrame()
for index in G10_daily_category:
    price_df[index]=data_dict[index].value
price_df.set_index(date,inplace=True)
price_df=price_df.loc[signal_df.index]

#TS
position=signal_df/8    
#weight=price_df.apply(lambda x:x/np.sum(x),axis=1)
return_matrix=(price_df-price_df.shift(1))/price_df.shift(1)
return_sep=position.shift(1)*return_matrix
return_sep=return_sep.dropna()
daily_re=return_sep.sum(axis=1)
daily_cum_re=(daily_re+1).cumprod()-1
plt.plot(daily_cum_re)
aunual_re=daily_cum_re[-1]/len(daily_cum_re.index)*252
aunnual_std=np.std(daily_re)*np.sqrt(252)
aunual_sp=np.mean(daily_re)/np.std(daily_re)*np.sqrt(252)

#CS    
signal_L3=signal_df.apply(lambda x: x.where(x<x.nlargest(3)[2],60),axis=1)
signal_S3=signal_L3.apply(lambda x: x.where(x>x.nsmallest(3)[2],-60),axis=1)
signal_else=signal_S3.apply(lambda x:x.where(np.abs(x)>1,0),axis=1)
position=signal_else/360

return_matrix=(price_df-price_df.shift(1))/price_df.shift(1)
return_sep=position.shift(1)*return_matrix
return_sep=return_sep.dropna()
daily_re=return_sep.sum(axis=1)
daily_cum_re=(daily_re+1).cumprod()-1
plt.plot(daily_cum_re)
aunual_re=daily_cum_re[-1]/len(daily_cum_re.index)*252
aunnual_std=np.std(daily_re)*np.sqrt(252)
aunnual_sp=np.mean(daily_re)/np.std(daily_re)*np.sqrt(252)
