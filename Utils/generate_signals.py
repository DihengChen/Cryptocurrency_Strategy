# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 16:48:25 2018

@Author: Diheng Chen
@Email: dc3829@nyu.edu
"""
import pandas as pd
import numpy as np
class signal_1():
    def __init__(self,data_dict,period=[8,16,32,24,48,96]):
        self.data_dict=data_dict
        self.date=data_dict[list(data_dict.keys())[0]].date
        self.signal_df=pd.DataFrame()
        self.period=period
        
    def EMA_dict_cal(self,FX):
        return {i:FX.ewm(alpha=1/i,adjust=False).mean() 
                    for i in self.period}
    
    def signal_u(self,X,price):
        std1=price.rolling(63).std(ddof=0)
        #substitute 0 to 10e-6
        std1.replace(0,10e-6,inplace=True)
        Y=X/std1
        std2=Y.rolling(252).std(ddof=0)
        std2.replace(0,10e-6,inplace=True)
        Z=Y/std2
        U=Z*np.exp(-Z**2/4)/np.sqrt(2)/np.exp(-0.5)
        return U
    
    def signal_sum(self,EMA_dict,period_,price):
        X1=EMA_dict[period_[0]]-EMA_dict[period_[3]]
        X2=EMA_dict[period_[1]]-EMA_dict[period_[4]]
        X3=EMA_dict[period_[2]]-EMA_dict[period_[5]]
        return (self.signal_u(X1,price)+self.signal_u(X2,price)+self.signal_u(X3,price))/3
    def get_signal(self):
        if len(self.signal_df)!=0:
            self.signal_df=pd.DataFrame()
        for index in self.data_dict.keys():
            EMA_dict_temp=self.EMA_dict_cal(self.data_dict[index].value) 
            self.signal_df[index]=self.signal_sum(EMA_dict_temp,self.period,\
                          self.data_dict[index].value)
        self.signal_df.set_index(self.date,inplace=True)
        self.signal_df.dropna(inplace=True)
