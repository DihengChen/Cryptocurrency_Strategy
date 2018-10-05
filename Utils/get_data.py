# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 12:31:16 2018

@Author: Diheng Chen
@Email: dc3829@nyu.edu
"""

from fredapi import *
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
