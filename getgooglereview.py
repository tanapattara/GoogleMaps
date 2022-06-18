from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from datetime import datetime
import bs4
import pandas as pd
import time
import csv

def scrollandload(driver):
    data = driver.page_source
    soup = bs4.BeautifulSoup(data, features="lxml")
    all_review_score = soup.find_all('div',{'class':'fontBodySmall'})
    allcomment = int(all_review_score[0].text.split()[0].replace(',', ''))
    loaded = 0
    n = 5
    count = 0
    while loaded < allcomment:
        i = 0
        while i < n:
            html = driver.find_elements(By.CLASS_NAME,'DxyBCb')
            html[0].send_keys(Keys.PAGE_DOWN)
            time.sleep(2.0)
            i += 1

        time.sleep(5.0) 
        data = driver.page_source
        soup = bs4.BeautifulSoup(data, features="lxml")
        currentload = soup.find_all('div',{'class':'jftiEf fontBodyMedium'})
        
        if loaded == len(currentload):
            count += 1
        
        loaded = len(currentload)
        print('get ' + str(loaded) + ':' + str(allcomment))

        if count == 3:
            break
        
        n *= 2

def loaddata(driver):
    data = driver.page_source
    soup = bs4.BeautifulSoup(data, features="lxml")
    all_review_score = soup.find_all('div',{'class':'jftiEf fontBodyMedium'})

    list_name = []
    list_score = []
    list_time = []
    list_comment = []

    for x in all_review_score:    
        name = x['aria-label']
        profiles = x.findChildren('div',{'class':'DU9Pgb'})
        pf = list(profiles)[0]
        score = pf.findChildren('span', {'class':'kvMYJc'})[0]
        score = score['aria-label'].split()[0]
        stime = pf.findChildren('span', {'class':'rsqaWe'})[0]
        stime = stime.text    
        comment = x.findChildren('span', {'class':'wiI7pd'})
        comment = comment[0].text

        list_name.append(name)
        list_score.append(score)
        list_time.append(stime)
        list_comment.append(comment)

    df = pd.DataFrame([list_name, list_score, list_time, list_comment])
    df = df.transpose()
    df.columns = ['name', 'score', 'time', 'comment']
    return df

with open('data/placelist.csv', newline='', encoding='utf-8') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar=',')
    for row in spamreader:      
        place_name = row[0].split('|')[0]
        place_url = row[0].split('|')[1]

        print('Open ', place_name)
        #open chrome
        driver = webdriver.Chrome()
        driver.get(place_url)

        # wait for loadcontent
        time.sleep(3.0)

        #get review button
        review_buttons = driver.find_elements(By.CLASS_NAME, 'HHrUdb')
        if len(review_buttons) > 0:
            last_element = review_buttons[-1]
            ActionChains(driver).click(last_element).perform()
            time.sleep(3.0)
            print('load... data')
            scrollandload(driver)
            print('save data')
            dataloaded = loaddata(driver)
            print('save ' + place_name + ' to excel')
            dataloaded.to_excel('results/' + place_name + '.xlsx')
        else:
            print('can\'t find review button')            
            continue

        driver.close()
