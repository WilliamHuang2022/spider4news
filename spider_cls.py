from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from funcs import*
import re


def parse_html(html):
    bs=BeautifulSoup(html,'html.parser')
    dates=[]
    time_list=[]
    title_list=[]
    summary_list=[]
    url_list=[]
    for ele in bs.select("div[class='clearfix m-b-15 f-s-16 telegraph-content-box']"):
        sep='@@@' # 用于分割的分隔符
        ele=str(ele)
        block_list=re.findall('<.*?>',ele)
        for block in block_list:
            ele=ele.replace(block,sep,1)
        block_list=re.findall(f'{sep}+',ele)
        for block in block_list:
            ele=ele.replace(block,sep,1)
        ele_list=ele.split(sep)
        if ele_list[0]=='':
            ele_list=ele_list[1:]

        title=''
        summary=''
        if '星期' in ele_list[0]: # 往日的新闻
            date=datetime.datetime.strptime(ele_list[0].split(' ')[0],"%Y.%m.%d").strftime("%Y-%m-%d")
            if date not in dates:
                dates.append(date)
            time=ele_list[1]
            time=datetime.datetime.strptime(time,'%H:%M:%S').strftime('%H:%M')
            if "【" in ele_list[2] and '】' in ele_list[2]:
                title=ele_list[2]
                summary=ele_list[3]
            else:
                title=ele_list[2]
                summary=ele_list[2]
        else: #当天的新闻
            time=ele_list[0]
            time=datetime.datetime.strptime(time,'%H:%M:%S').strftime('%H:%M')
            if "【" in ele_list[1] and '】' in ele_list[1]:
                title=ele_list[1]
                summary=ele_list[2]
            else:
                title=ele_list[1]
                summary=ele_list[1]
        time_list.append(time)
        title_list.append(title)
        summary_list.append(summary)
        url_list.append('https://www.cls.cn/telegraph')
    if dates ==[]:
        raise ValueError('没爬到昨天的新闻，无法准确定位时间')
    today=(datetime.datetime.strptime(dates[0],"%Y-%m-%d")+datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    dates=[today]+dates
    
    times,titles,urls,summarys=sep_list(time_list,title_list,url_list,summary_list)# [[],[]]
    return dates,times,titles,urls,summarys

def html2dic(html):
    dates,times,titles,urls,summarys=parse_html(html)
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
                    print('有一个爬不到昨天的新闻：'+file_d)

if __name__=='__main__':
    html=get_html('https://www.cls.cn/telegraph','#__next > div > div.m-auto.w-1200 > div.clearfix.content-main-box > div.f-l.content-left > div.f-s-14.list-more-button.more-button',120)# 至少要爬1分钟才能爬完当天

    # with open('./html/cls_2024_10_09 21_36_39.txt','r',encoding='utf-8') as f1:
    #     html=f1.read()
    save_html(html,'cls')
    dic=html2dic(html)
    save_dic(dic,'cls')
    # htmls2jsons('./html','cls')

    
    # for ele in bs.select("div[class='b-c-e6e7ea telegraph-list']"):
        # 这个的有点复杂，主要就是当天的新闻就只带一个日期，而往日的就全部都带日期
        # try:
        #     date=ele.div.string
        #     time=ele.select("span[class='f-l l-h-136363 f-w-b c-de0422 telegraph-time-box']")[0].string
        #     title=ele.select("span[class='c-34304b']")[0].contents[0].contents[0].string
        #     summary=ele.select("span[class='c-34304b']")[0].contents[0].contents[1]
        #     date_list.append(date)
        #     if date is None or time is None or title is None or summary is None:
        #         raise
        #     print(date)
        #     print(time)
        #     print(title)
        #     print(summary)
        # except:
        #     try:
        #         time=ele.div.div.span.string
        #         if len(ele.div.div.div.div.contents)>2:
        #             title=ele.div.div.div.div.contents[0].string
        #             summary=ele.div.div.div.div.contents[1]
        #         elif len(ele.div.div.div.div.contents)==2:
        #             title=ele.div.div.div.div.contents[0].string

        #         if time is None or title is None or summary is None:
        #             raise
        #         print(time)
        #         print(title)
        #         print(summary)
        #     except:
        #         try:
        #             date=ele.div.div.div.string
        #             print(date)
        #             if len(ele.select("span[class='c-de0422']")[0].contents[0].contents)>2:
        #                 item=ele.select("span[class='c-de0422']")[0].contents[0].contents
        #                 title=item[0].string
        #                 summary=item[1]
        #                 print(title)
        #                 print(summary)

        #             elif len(ele.select("span[class='c-de0422']")[0].contents[0].contents)==2:
        #                 title=ele.select("span[class='c-de0422']")[0].contents[0].contents[0].string
        #                 print(title)
        #             print(ele)
        #             break
        #         except:
        #             # print(ele)
        #             break
        # print()
    # print(date_list)
        #==========================================================
        # try:
        #     print(ele.div.div.span.string)#time

        #     if len(ele.div.div.div.div.contents)>2:
        #         print(ele.div.div.div.div.contents[0].string)# title
        #         print(ele.div.div.div.div.contents[1]) # summary
        #     elif len(ele.div.div.div.div.contents)==2:
        #         print(ele.div.div.div.div.contents[0].string) # title
        # except:
        #     try:
        #         # print(ele)
        #         print(ele.div.string) # date
        #         print(ele.select("span[class='f-l l-h-136363 f-w-b c-de0422 telegraph-time-box']")[0].string) # time
        #         print(ele.select("span[class='c-34304b']")[0].contents[0].contents[0].string) # title
        #         print(ele.select("span[class='c-34304b']")[0].contents[0].contents[1]) # summary

        #     except:
        #         print(ele)
        #         break
        # print()
    #=========================================================

    
# class="b-c-e6e7ea telegraph-list" 是每个的大表头名

# clearfix m-b-15 f-s-16 telegraph-content-box 是每个细表的头名