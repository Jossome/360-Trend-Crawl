from selenium import webdriver
import urllib.parse
import time
import re
import pandas as pd
import datetime
import pickle

def get_source(name, date):
    _name = urllib.parse.quote(name)
    url="http://index.so.com/result/trend?keywords=" + _name + "&region=%E5%85%A8%E5%9B%BD&time=" + date
    driver = webdriver.PhantomJS(r'E:\\phantomjs-2.1.1-windows\\bin\\PhantomJS.exe') #, service_args=['--webdriver=8643 --ignore-ssl-errors=true'])
    driver.get(url)
    src = driver.page_source
    while src.find('正在加载数据') != -1:
        driver.get(url)
        src = driver.page_source
        print('Fail to fetch data, trying again...')
        time.sleep(1)
    driver.quit
    return src

def extract_pos(source):
    f = re.findall(r'<g name="line"><path d=".*?"', source)
    pos = {'trend':[], 'media':[]}
    for i in [0, 1]:
        raw_pos = f[i][24:-1]
        pos1 = []
        c_pos = raw_pos.find('C')
        s_pos = raw_pos.find('S')
        pos1.append(raw_pos[1:c_pos].split(',')[1])
        pos1.append(raw_pos[c_pos:s_pos].split(' ')[-1].split(',')[1])
        pos2 = [x.split(' ')[0].split(',')[1] for x in raw_pos[s_pos+1:].split('S')]
        if i == 0:
            pos['trend'] = [float(x) for x in pos1 + pos2]
        else:
            pos['media'] = [float(x) for x in pos1 + pos2]
    return pos

def extract_scale(source):
    '''
    In the graph, zero is 250, max_scale is 47.
    This function calculates the scale of real value on graph.
    '''
    scale = {'trend': 0, 'media': 0}
    a = source.find('y="47"')
    b = source.find(';">', a)
    c = source.find('<', b)
    scale['trend'] = float(source[b+3:c]) / (250 - 47)
    a = source.find('y="47"', c)
    b = source.find(';">', a)
    c = source.find('<', b)
    scale['media'] = float(source[b+3:c]) / (250 - 47)
    return scale
    
def date_list(start, end):
    date = [start]
    next_date = datetime.datetime.strptime(date[-1],'%Y-%m-%d') + datetime.timedelta(days = 1)
    end_date = datetime.datetime.strptime(end,'%Y-%m-%d') + datetime.timedelta(days = 1)
    while next_date != end_date:
        date.append(next_date.strftime('%Y-%m-%d'))
        next_date = datetime.datetime.strptime(date[-1],'%Y-%m-%d') + datetime.timedelta(days = 1)
    return date

with open('shit.pkl', 'rb') as file:
    stock_dict = pickle.load(file) #shenzhen, shanghai, chuangye
'''
driver = webdriver.PhantomJS(r'E:\\phantomjs-2.1.1-windows\\bin\\PhantomJS.exe') #, service_args=['--webdriver=8643 --ignore-ssl-errors=true'])

invalid = ['600253', '600832', '601299', '601566', '603010', '000024', '000522', '000522', '000602', '000787', '300149', '300186', '300266', '300283', '300382', '300393']
for name in invalid:
    _name = name.split('.')[0]
    url="http://index.so.com/result/trend?keywords=" + _name + "&region=%E5%85%A8%E5%9B%BD&time=" + "201301|201312"
    
    driver.get(url)
    source = driver.page_source
    
    cnt = 0
    flag = False
    while source.find('正在加载数据') != -1:
        cnt += 1
        driver.get(url)
        source = driver.page_source
        print('Fail to fetch data, trying again...')
        time.sleep(1)
        if cnt > 3: #retry too many times... it needs more sleep time or may be banned
            time.sleep(2)
        if cnt > 6:
            print("Invalid " + _name)
            invalid.append(_name)
            flag = True            
            break
    if flag:
        continue
    
    pos = extract_pos(source)
    scale = extract_scale(source)
    index_t = [(250 - x) * scale['trend'] for x in pos['trend']]
    index_m = [(250 - x) * scale['media'] for x in pos['media']]
    date = date_list('2013-01-11', '2013-12-31')
    trend = pd.DataFrame({'Date': date, 'Index': index_t})
    media = pd.DataFrame({'Date': date, 'Index': index_m}) 
    
    for each in ['4', '5', '6']:
        time.sleep(2)
        url="http://index.so.com/result/trend?keywords=" + _name + "&region=%E5%85%A8%E5%9B%BD&time=" + '201' + each + '01|201' + each + '12'
        
        driver.get(url)
        source = driver.page_source
        cnt = 0
        flag = False
        while source.find('正在加载数据') != -1:
            cnt += 1
            driver.get(url)
            source = driver.page_source
            print('Fail to fetch data, trying again...')
            time.sleep(1)
            if cnt > 3: #retry too many times... it needs more sleep time or may be banned
                time.sleep(2)
            if cnt > 6:
                print("Invalid " + _name)
                invalid.append(_name)
                flag = True
                break
        if flag:
            continue
        pos = extract_pos(source)
        scale = extract_scale(source)
        index_t = [(250 - x) * scale['trend'] for x in pos['trend']]
        index_m = [(250 - x) * scale['media'] for x in pos['media']]
        date = date_list('201' + each + '-01-01', '201' + each + '-12-31')
        trend = pd.concat([trend, pd.DataFrame({'Date': date, 'Index': index_t})])
        media = pd.concat([media, pd.DataFrame({'Date': date, 'Index': index_m})])
    trend.reset_index(drop = True).to_csv('./trend/' + _name + '.csv')
    media.reset_index(drop = True).to_csv('./media/' + _name + '.csv')
    print("finish with " + _name)
    time.sleep(5)
    
driver.quit
'''
#上面这段是用来爬很多股票的，下面是爬单个的。

source = get_source('欢乐颂','201505|201603')
pos = extract_pos(source)
scale = extract_scale(source)
index = [(250 - x) * scale['trend'] for x in pos['trend']]

date = date_list('2015-05-01', '2016-03-31')
trend = pd.DataFrame({'Date': date, 'Index': index})

source = get_source('欢乐颂','201605|201703')
pos = extract_pos(source)
scale = extract_scale(source)
index = [(250 - x) * scale['trend'] for x in pos['trend']]

date = date_list('2016-05-01', '2017-03-31')
trend = pd.concat([trend, pd.DataFrame({'Date': date, 'Index': index})])
'''