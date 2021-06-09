import time
import urllib3
import math
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

http = urllib3.PoolManager()

import mysql.connector
database=mysql.connector.connect(host="127.0.0.1",user='root',password='charan',auth_plugin='mysql_native_password',database='cashless')
mycursor=database.cursor()

import csv

import pandas as pd
hospitalName=[]
State=[]
City=[]

def get_driver():
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.headless = True
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    prefs = {'profile.default_content_setting_values.notifications': 2}
    chrome_options.add_experimental_option('prefs', prefs)
    try:
        chrome_executable = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        driver = webdriver.Chrome(executable_path=chrome_executable, options=chrome_options)
    except:
        driver = webdriver.Chrome(ChromeDriverManager("2.36").install(), options=chrome_options)
    return driver

def hospital_list_for_each_state(driver,state,city):
    hospital_list = driver.find_elements_by_xpath('//div[@class="garage-list-main"]')
    for each_hospital in range(1,len(hospital_list)+1):
        div_element=driver.find_element_by_xpath('//div[@class="garage-list-main"]['+str(each_hospital)+']')
        driver.execute_script("arguments[0].removeAttribute('style')",div_element)
        time.sleep(2.5)
        hospital_name = driver.find_element_by_xpath('//div[@class="garage-list-main"]['+str(each_hospital)+']/div/div').text
        sql = "INSERT INTO hospital (hospitalName,state,city) VALUES (%s, %s,%s)"
        val = (hospital_name,state,city)
        mycursor.execute(sql, val)
        database.commit() 
        


def states_name():
    driver = get_driver()
    driver.get('https://www.hdfcergo.com/locators/cashless-hospitals-network/')
    time.sleep(1)
    select_element = driver.find_element_by_id('StateList')
    flag = 1
    for each_option in select_element.find_elements_by_tag_name('option'):
        if (flag==1):
            flag = 0
            continue
        each_option.click()
        time.sleep(2.5)
        select_city = driver.find_element_by_id('CityList')
        for each_city_option in select_city.find_elements_by_tag_name('option'):
            each_city_option.click()
            time.sleep(5)
            hospital_list_for_each_state(driver,each_option.get_attribute('value'),each_city_option.get_attribute('value'))
    driver.close()

def get_hospitals_detail(city=None):
    states_name()
    try:
        if city==None:
            sql_select_query = """select * from hospital"""
            mycursor.execute(sql_select_query)
        else:
            sql_select_query = """select * from hospital where city = %s"""
        
            mycursor.execute(sql_select_query, (city,))
        
        record = mycursor.fetchall()

        for row in record:
            hospitalName.append(row[0])
            State.append(row[1])
            City.append(row[2])
            #print("hospital name = ", row[0], )
            #print("state = ", row[1])
            #print("city= ", row[2],"\n")

    except mysql.connector.Error as error:
        print("Failed to get record from MySQL table: {}".format(error))

dict={'hospitalName': hospitalName,'state': State,'city': City}
df=pd.DataFrame(dict)
df.to_csv('hospital.csv')

if __name__ == "__main__":
    get_hospitals_detail(input())
    

