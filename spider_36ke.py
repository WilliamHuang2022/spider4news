from bs4 import BeautifulSoup
import datetime
from playwright.sync_api import sync_playwright
from funcs import *

def parse_date(html):
    #按前天的日期作为锚
    bs=BeautifulSoup(html,'html.parser')
    date_list=[ele.string for ele in bs.select('.date-bg')]
    if len(date_list)<3:
        raise ValueError('获取的日期不够3天，无法准确定位日期')
    day_by=date_list[2]#前天的日期 如10.04
    day_by_list=[int(ele) for ele in day_by.split('.')]
    if day_by_list[0]==12:#就是当前天是29号的时候比较麻烦
        if day_by_list[1]==29:
            if datetime.datetime.now().strftime("%m")=='01':#跨年了，锚要减回一年
                year=str(int(datetime.datetime.now().strftime("%Y"))-1)
            else:
                year=datetime.datetime.now().strftime("%Y")
        elif day_by_list[1]<29:
            year=datetime.datetime.now().strftime("%Y")
        elif day_by_list[1]>29:
            year=str(int(datetime.datetime.now().strftime("%Y"))-1)
        day_by=year+'.'+day_by
        dates=[]
        for i in range(2,-(len(date_list)-2),-1):
            dates.append((datetime.datetime.strptime(day_by,"%Y.%m.%d")+datetime.timedelta(days=i)).strftime("%Y-%m-%d"))
    else:
        year=datetime.datetime.now().strftime("%Y")
        day_by=year+'.'+day_by
        # day_by=datetime.datetime.strptime(day_by,"%Y.%m.%d").strftime("%Y-%m-%d")
        dates=[]
        for i in range(2,-(len(date_list)-2),-1):
            dates.append((datetime.datetime.strptime(day_by,"%Y.%m.%d")+datetime.timedelta(days=i)).strftime("%Y-%m-%d"))
    return dates

def parse_html(html_mobile):
    bs=BeautifulSoup(html_mobile,'html.parser')
    time_list=[]
    title_list=[]
    summary_list=[]
    url_list=[]

    for ele in bs.select('.item_datetime'):
        try:
            time_list.append(ele.select('div[class="left-time"]')[0].string)
        except:
            continue
        try:
            title_list.append(ele.h2.string)
        except:
            title_list.append('')
        try:
            summary=ele.p.span.string
            if summary:
                summary_list.append(summary)
            else:
                summary_list.append('')
        except:
            summary_list.append('')
        try:
            url_list.append(ele.a.attrs['href'] if ele.a.attrs['class']==['article-link'] else '')
        except:
            url_list.append('')
    # time_list=[ele.select('div[class="left-time"]')[0].string for ele in bs.select('.item_datetime')]
    # title_list=[ele.h2.string for ele in bs.select('.item_datetime')]
    # summary_list=[ele.p.span.string for ele in bs.select('.item_datetime')]
    # url_list=[ele.a.attrs['href'] if ele.a.attrs['class']==['article-link'] else '' for ele in bs.select('.item_datetime')]

    times,titles,urls,summarys=sep_list(time_list,title_list,url_list,summary_list)# [[],[]]

    return times,titles,urls,summarys

def html2dic(html):
    times,titles,urls,summarys=parse_html(html)
    dates=parse_date(html)
    dic={}
    for i in range(len(dates)):# 一个日期对应一个子字典
        date=dates[i]
        time_list=times[i]
        title_list=titles[i]
        url_list=urls[i]
        summary_list=summarys[i]
        new_dic=pack(date,time_list,title_list,url_list,summary_list)
        dic[date]=new_dic
    return dic

def htmls2jsons(filepath,website):
    # 获取该路径下的所有文件
    files = os.listdir(filepath)
    
    # 遍历所有文件
    for file in files:
        # 把文件路径和文件名结合起来
        file_d = os.path.join(filepath, file)
        # 判断该文件是单个文件还是文件夹
        if os.path.isdir(file_d):  # 如果是文件夹则递归调用 scanDir() 函数
            pass
        else:
            if website in file_d:
                print("scan file: "+file_d)
                with open(file_d,'r',encoding='utf-8') as f1:
                    html=f1.read()
                try:
                    dic=html2dic(html)
                    save_dic(dic,website)
                except:
                    print('有一个不满足3天条件：'+file_d)

if __name__=='__main__':
    #需要用移动端的才可以获取到具体时间戳
    # html_mobile=get_html('https://www.36kr.com/newsflashes','.kr-loading-more-button-default',60,device='iPhone X')# 起码要刷够60秒才能将最近的三天的新闻都凑够，然后利用前天的日期作为锚来获取date

    # save_html(html_mobile,'36ke')
    # dic=html2dic(html_mobile)
    # save_dic(dic,'36ke')
    htmls2jsons('./html','36ke')
    