# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 12:31:16 2018

@Author: Diheng Chen
@Email: dc3829@nyu.edu
"""

from fredapi import *
from requests import get
import re
import json
import datetime
import time
import pickle
import pandas as pd

class currency():
    def __init__(self,api_key=None):
        self.api_key=None
        if api_key is not None:
            self.api_key=api_key
        else:
            print('Try to get your own key, though you can use my key:)'+'\n')
            self.api_key='dd5c1b8fdddaa8fdcbda543a0773c658'
            
        self.all_symbols=['DEXUSAL','DEXCAUS','DEXSZUS','DEXUSUK','DEXJPUS','DEXNOUS',\
            'DEXUSNZ','DEXSDUS','DTWEXM','DTWEXB','DEXUSEU','DEXCHUS','DEXMXUS',\
            'DEXBZUS','DEXKOUS','DEXINUS','DEXVZUS','DEXMAUS','DEXTHUS','DEXSFUS'\
            'DEXTAUS','DEXHKUS','DEXSIUS','DEXSLUS']

    def get_all_symbols(self):
        return self.all_symbols
    def get_currency(self,symbols=None):
        #API key
        fred = Fred(self.api_key)
        
        if symbols is None:
            print('You are trying to download the whole dataset, it could take\
                  a super long time')
            symbols=self.all_symbols

        print('The currency you are downloading are '+str(symbols) )
        data_dict={index:fred.get_series_all_releases(index) for index \
                   in symbols}
        return data_dict

class cryptocurrency():
    def __init__(self):
        self.date=datetime.date.today().strftime("%Y-%m-%d")
        
    def get_all_symbols(self):
        url = 'https://min-api.cryptocompare.com/data/all/coinlist'
        page = get(url).text
        x = re.findall("\{\"Id\".*?\}", page)
        table = {"CoinName": [], "Symbol": [], "IsTrading": []}
        for i in range(len(x)):
            cache = json.loads(x[i])
            for key in table:
                table[key].append(cache[key])
        table = pd.DataFrame(table)
        return table
    
    def daily_price_historical(self, symbols, end_time=None, comparison_symbol="USD",
                           limit=2000, aggregate=1, allData='true'):
        #definition of parameters:https://min-api.cryptocompare.com/ 
        if end_time==None:
            end_time=self.date
        timestamp = time.mktime(datetime.datetime.strptime(end_time,
                                                           "%Y-%m-%d").timetuple())
        data_dict={}
        for symbol in symbols:
            url = ('https://min-api.cryptocompare.com/data/histoday?' +
                   'fsym={}&tsym={}&limit={}&aggregate={}&allData={}&toTs={}')
            url = url.format(symbol.upper(), comparison_symbol.upper(),
                             limit, aggregate, allData, timestamp)
            page = get(url)
            data = page.json()['Data']
            df = pd.DataFrame(data)
            df['time'] = [datetime.datetime.fromtimestamp(d) for d in df.time]
            df = df.loc[:, ["open", "high", "low", "close", "time"]]
            df.time = df.time.dt.strftime('%Y-%m-%d')
            df.set_index("time", inplace=True)
            data_dict[symbol]=df
        return data_dict

