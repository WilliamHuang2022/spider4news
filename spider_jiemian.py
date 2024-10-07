from bs4 import BeautifulSoup
import time,json
from playwright.sync_api import sync_playwright
from funcs import *


def transfer_month(month):
    # 将html中的月份英文转换为阿拉伯数字
    mon_list=['January','February','March','April','May',"June",'July','August','September','October','November','December']
    mon_list=[ele+'.' for ele in mon_list]
    num_list=list(range(1,13))
    for i in range(len(mon_list)):
        if month.replace('.','').lower() in mon_list[i].lower():
            return str(num_list[i])
    return month.replace('.','')

def parse_time(html):
    # 解析html输出日期
    bs=BeautifulSoup(html,'html.parser')
    day_ele=bs.select('.columns-right-center__newsflash-day')
    month_ele=bs.select('.columns-right-center__newsflash-mouth')
    year_ele=bs.select('.columns-right-center__newsflash-year')
    day_lis=[ele.string for ele in day_ele]
    month_lis=[transfer_month(ele.string) for ele in month_ele]
    year_lis=[ele.string for ele in year_ele]
    if len(day_lis)*len(month_lis)*len(year_lis)>1:
        n=max(max(len(day_lis),len(month_lis)),len(year_lis))
        if len(day_lis)==1:
            day_lis=n*day_lis
        if len(month_lis)==1:
            month_lis=n*month_lis
        if len(year_lis)==1:
            year_lis=n*year_lis
    dates=[]
    for i in range(len(day_lis)):
        dates.append(f"{year_lis[i]}-{month_lis[i]}-{day_lis[i]}")
    return dates



def parse_html(html):
    # 将html中的时间戳、标题、总结、url进行解析
    bs=BeautifulSoup(html,'html.parser')
    time_list=[]
    title_list=[]
    summary_list=[]
    url_list=[]
    for ele in bs.select("li[class='']"):
        try:
            time_list.append(ele.select(".columns-right-center__newsflash-date-node")[0].string)
        except:
            continue
        try:
            title_list.append(ele.h4.string)
        except:
            title_list.append('')
        try:
            summary_list.append(ele.select('.columns-right-center__newsflash-content__summary')[0].string)
        except:
            summary_list.append('')
        try:
            url_list.append(ele.select('.logStore')[0].attrs['href'])
        except:
            url_list.append('')

    # title_list=[ele.string for ele in bs.select("[class='logStore']")]
    # url_list=[ele.attrs['href'] for ele in bs.select("[class='logStore']")]

    # time_list=[ele.string for ele in bs.select('.columns-right-center__newsflash-date-node')]
    # summary_list=[ele.text for ele in bs.select(".columns-right-center__newsflash-content__summary")]
    times,titles,urls,summarys=sep_list(time_list,title_list,url_list,summary_list)# [[],[]]
    
    return times,titles,urls,summarys


def html2dic(html):
    dates=parse_time(html)
    times,titles,urls,summarys=parse_html(html)# [[],[]]
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




if __name__=="__main__":
    # with open('./html/jiemian_2024_10_06 10_34_21.txt','r',encoding='utf-8') as f1:
    # # with open('./html/html_2024_10_06 17_21_49.txt','r',encoding='utf-8') as f1:
    #     html=f1.read()

    html=get_html('https://www.jiemian.com/lists/4.html','body > div.pjax-wrapper > div > div.middle-content > div > div > div > div.columns-right-view > div.columns-right-center > div > div.load-view > span')
    # save_html(html,'jiemian')
    # dic=html2dic(html)
    # save_dic(dic,'jiemian')
    bs=BeautifulSoup(html,'html.parser')
    for ele in bs.select("li[class='']"):
        print(ele)
        print(ele.select(".columns-right-center__newsflash-date-node")[0].string) # time
        print(ele.h4.string) # title
        print(ele.select('.columns-right-center__newsflash-content__summary')[0].string)# summary
        print(ele.select('.logStore')[0].attrs['href']) # url
        break