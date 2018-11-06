# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 16:48:25 2018

@Author: Diheng Chen
@Email: dc3829@nyu.edu
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm

class signal_1():
    def __init__(self,data_dict,period=[8,16,32,24,48,96],DofY=252):
        self.data_dict=data_dict
        self.date=data_dict[list(data_dict.keys())[0]].date
        self.signal_df=pd.DataFrame()
        self.period=period
        self.day=DofY
        
    def EMA_dict_cal(self,FX):
        return {i:FX.ewm(alpha=1/i,adjust=False).mean() 
                    for i in self.period}
    
    def signal_u(self,X,price):
        if self.day==252:
            std1=price.rolling(63).std(ddof=0)
            #substitute 0 to 10e-6
            std1.replace(0,10e-6,inplace=True)
            Y=X/std1
            std2=Y.rolling(252).std(ddof=0)
            std2.replace(0,10e-6,inplace=True)
            Z=Y/std2
            U=Z*np.exp(-Z**2/4)/np.sqrt(2)/np.exp(-0.5)
        else:
            std1=price.rolling(91).std(ddof=0)
            #substitute 0 to 10e-6
            std1.replace(0,10e-6,inplace=True)
            Y=X/std1
            std2=Y.rolling(365).std(ddof=0)
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

class signal_2():
    """
    Mean Reverting and Momentum Strategy
    Reference: 'Identifying Small Mean Reverting Portfolios'
    """
    def __init__(self, ret,card=3,period=182):

        assert isinstance(ret, pd.DataFrame)
        assert ret.isnull().values.sum() == 0

        self.ret = ret
        self.sample_size=len(ret)
        self.num_symbol=ret.columns.size
        self.period=period
        self.k=card
        self.signal_df=pd.DataFrame(columns=ret.columns)
        self.date=ret.index
        
    def get_signal(self,opt='max'):
        
        for n in range(self.period,self.sample_size+1):
        
            St=self.ret.iloc[n-182:n,:]
            S=St.iloc[1:,:].values
            S_lag=St.iloc[:-1,:].values
            gamma = St.cov().values
            if np.linalg.det(S_lag.T @ S_lag)==0:
                self.signal_df.loc[self.date[n-1]]=self.signal_df.loc[self.date[n-2]]
                continue
            A_ = np.linalg.inv(S_lag.T @ S_lag) @ S_lag.T @ S
            
            A = A_.T @ gamma @ A_
            B = gamma
            
            def target(A, B, x):
                return (x.T @ A @ x) / (x.T @ B @ x)
            
            I = []
            I_c = [s for s in range(self.num_symbol)]
            for i in range(self.k):
                if len(I) == 0:
                    if opt == 'max':
                        index = (np.diag(A) / np.diag(B)).argmax()
                    elif opt == 'min':
                        index = (np.diag(A) / np.diag(B)).argmin()

                    I.append(index)
                    I_c.remove(index)
                else:
                    gain = -np.inf if opt == 'max' else np.inf
                    for j in I_c:

                        ran_ge = np.ix_(I + [j], I + [j])
                        a = A[ran_ge]
                        b = B[ran_ge]
                        b_inv = np.linalg.inv(b)
                        mat = b_inv @ a
                        eig_val, eig_vec = np.linalg.eig(mat)

                        if opt == 'max':
                            x = eig_vec[:, eig_val.argmax()].reshape(-1, 1)
                            if target(a, b, x) > gain:
                                gain = target(a, b, x)
                                z = x
                                index = j
                        elif opt == 'min':
                            x = eig_vec[:, eig_val.argmin()].reshape(-1, 1)
                            if target(a, b, x) < gain:
                                gain = target(a, b, x)
                                z = x
                                index = j

                    I.append(index)
                    I_c.remove(index)

            weights = np.zeros((self.num_symbol, 1))
            weights[I, 0] = z.ravel()
            self.signal_df.loc[self.date[n-1]]=weights.reshape(1,-1)[0]