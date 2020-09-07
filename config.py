# coding: utf-8
import configparser

config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')


SLACK = config_ini['SLACK']

BITFLYER = config_ini['BITFLYER']
