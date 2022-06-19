from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

import bs4
import pandas as pd
import time
import csv
import os.path

from sqlalchemy import false

def scrollandload(driver):
    data = driver.page_source
    soup = bs4.BeautifulSoup(data, "lxml")
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
            i += 1
        data = driver.page_source
        soup = bs4.BeautifulSoup(data, "lxml")
        currentload = soup.find_all('div',{'class':'jftiEf fontBodyMedium'})
        
        if loaded == len(currentload):
            count += 1
        
        loaded = len(currentload)
        print('get ' + str(loaded) + ':' + str(allcomment))

        if count == 2:
            break
        
        n *= 2

def loaddata(driver):
    data = driver.page_source
    soup = bs4.BeautifulSoup(data, "lxml")
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

def saveplacedetail(driver, lat, lon):
    #get name of place
    data = driver.page_source
    soup = bs4.BeautifulSoup(data, "lxml")
    name_element = soup.find_all('h1',{'class':'DUwDvf fontHeadlineLarge'})
    place_name = name_element[0].text.strip()
    #get overall score of place
    place_score = soup.find_all('div', {'class', 'F7nice mmu3tf'})
    place_score = float(place_score[0].span.text)
    #get category
    place_detail = soup.find_all('div', {'class', 'skqShb'})
    place_category = place_detail[0].contents[1].text.replace('·','') if '·' in  place_detail[0].contents[1].text else place_detail[0].contents[1].text
    
    #add place data to dataframe
    place_data = pd.DataFrame([place_name, place_score, place_category, lat, lon])
    place_data = place_data.transpose()
    place_data.columns = ['name','score','category','latitude','longitude']
    path_to_file = 'results\place.csv'
    
    #check exist data in place.csv file
    existrecord = False
    if os.path.exists(path_to_file):
        existdata = pd.read_csv(path_to_file)
        for data in existdata.values:
            if place_name in data:
                existrecord = True
        if not existrecord:
            place_data = existdata.append(place_data, ignore_index = True)        
    
    #save to csv
    place_data.to_csv(path_to_file, index=False)
    return [existrecord, place_name]

with open('data/placelist.csv', newline='', encoding='utf-8') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar=',')
    for row in spamreader:      
        place_url = row[0]

        #find location
        surl = place_url.split('/')
        locations = [x for x in surl if "@" in x]
        if len(locations) > 1:
            i = 0
            for loc in locations:
                if len(loc.split(',')) == 3:
                    break
                i += 1
            locations = locations[i]
        else:
            locations = locations[0]

        lat = float(locations.split(',')[0].replace('@',''))
        lon = float(locations.split(',')[1])

        #open chrome
        driver = webdriver.Chrome()
        driver.get(place_url)

        # wait for loadcontent
        time.sleep(3.0)
  
        place_name = saveplacedetail(driver, lat, lon)

        if place_name[0]:
            continue

        place_name = place_name[1]
        #get review button
        #
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
            dataloaded.to_excel('results/' + place_name + '.xlsx', index=False)
        else:
            print('can\'t find review button')            
            continue

        driver.close()