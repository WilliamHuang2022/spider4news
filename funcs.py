import datetime,os
import json,time
from playwright.sync_api import sync_playwright

def jsons2mds(filepath):
    file_list=scan_files(filepath)
    for filename in file_list:
        text=""
        with open(filename,'r',encoding='utf-8') as f1:
            dic=json.load(f1)
        for time in dic.keys():
            text+=f"# {time}\n"
            lis=dic[time]
            for subdic in lis:
                text+=f"**{subdic['title']}**\n{subdic['summary']}\n[{subdic['url']}]({subdic['url']})\n"
        sep='\\'
        date=filename.split(sep)[1].split('_')[1].split('.')[0]
        with open(f'./news_md/news_{date}.md','w',encoding='utf-8') as f2:
            f2.write(text)

def merge_jsons(filepath):
    #将不同平台的新闻json按日期合并
    file_list=scan_files(filepath)
    date_list=set()
    sep='\\'
    for filename in file_list:
        date=filename.split(sep)[1].split('_')[1].split('.')[0]
        date_list.add(date)
    date_list=list(date_list)
    for date in date_list:
        candidate_file=[]
        for filename in file_list:#找出同一天的新闻json
            if date in filename:
                candidate_file.append(filename)
        total_dic={}
        for filename in candidate_file:#将所有同一天的json合并为total_dic
            with open(filename,'r',encoding='utf-8') as f1:
                dic=json.load(f1)
            if total_dic=={}:
                total_dic=dic
            else:
                total_dic=merge_dic(total_dic,dic)
        with open(f'./total_news/news_{date}.json','w',encoding='utf-8') as f1:
            file=json.dumps(total_dic,ensure_ascii=False,indent=True)
            f1.write(file)
        


def pack(date,time_list,title_list,url_list,summary_list):
    #将一天的内容列表进行组装
    dic={}
    for i in range(len(time_list)):
        subdic={}
        title=title_list[i]
        summary=summary_list[i]
        url=url_list[i]
        subdic['title']=title
        subdic['summary']=summary
        subdic['url']=url
        if dic.get(f"{date}_{time_list[i]}"):
            dic[f"{date}_{time_list[i]}"].append(subdic)
        else:
            dic[f"{date}_{time_list[i]}"]=[subdic]
    return dic

def scan_files(filepath):
    # 获取该路径下的所有文件
    files = os.listdir(filepath)
    file_list=[]
    # 遍历所有文件
    for file in files:
        # 把文件路径和文件名结合起来
        file_d = os.path.join(filepath, file)
        # 判断该文件是单个文件还是文件夹
        if os.path.isdir(file_d):  # 如果是文件夹则递归调用 scanDir() 函数
            pass
        else:
            file_list.append(file_d)
    return file_list

def get_html(url,botton_css,timeout=60,device=None):
    # device表示模拟哪个设备，可以是'iPhone X'
    html_old=""
    html_new=""
    with sync_playwright() as p:
        # browser=p.chromium.launch(headless=False)
        browser = p.chromium.launch(channel="msedge",headless=True)
        if device:
            context = browser.new_context(
            **p.devices[device]
            )
            page=context.new_page()
        else:
            page=browser.new_page()
        page.goto(url)
        page.wait_for_timeout(1000)

        html_old=page.content()
        page.wait_for_timeout(1000)
        ts=time.time()
        while True:
            if time.time()-ts>=timeout:
                # save_html(html_old,webdite)
                print(f'timeout_break')
                break
            try:
                botton=page.query_selector(botton_css)
                botton.click()
                print('press the botton')
                page.wait_for_timeout(2500)
                html_new=page.content()
                if html_old==html_new:
                    # save_html(html_new,webdite)
                    print('no more new information')
                    break
                else:
                    html_old=html_new
                    continue
            except:
                # save_html(html_old,webdite)
                try:
                    page.wait_for_timeout(1000)
                    page.mouse.wheel(0,7000)
                    print('mouse wheel')
                    page.wait_for_timeout(1000)
                    if page.content()==html_old:
                        print('no more new information')
                        break
                    else:
                        html_old=page.content()
                        continue
                except:
                    print('no botton and stop')
                    break
    return html_old


def save_html(html,website):
    now = datetime.datetime.now()  
    timestamp = now.timestamp()  
    dt = datetime.datetime.fromtimestamp(timestamp)  
    formatted_dt = dt.strftime("%Y_%m_%d %H_%M_%S")  
    with open(f'./html/{website}_{formatted_dt}.txt','w',encoding='utf-8') as f1:
        f1.write(html)

def sep_list(time_list,title_list,url_list,summary_list):
    # 将几天的内容时间戳分别截断放入大列表
    s=0
    times=[]
    titles=[]
    urls=[]
    summarys=[]
    n=min(len(time_list),len(title_list))#按短的来作为标准长度
    time_list=time_list[:n]
    title_list=title_list[:n]
    url_list=url_list[:n]
    summary_list=summary_list[:n]
    for i in range(len(time_list)-1):
        if time_list[i]<time_list[i+1]:
            times.append(time_list[s:i+1])
            titles.append(title_list[s:i+1])
            urls.append(url_list[s:i+1])
            summarys.append(summary_list[s:i+1])
            s=i+1
    times.append(time_list[s:])
    titles.append(title_list[s:])
    urls.append(url_list[s:])
    summarys.append(summary_list[s:])
    return times,titles,urls,summarys

def merge_dic(main_dic,dic):
    #特殊的字典合并，防止同一个时间戳下两个不同的新闻其中一个被覆盖
    new_dic=main_dic
    exist_keys_list=list(main_dic.keys())
    for key in dic.keys():
        if key in exist_keys_list:
            for subdic in dic[key]:
                if subdic not in new_dic[key]:#避免出现重复的新闻
                    new_dic[key].append(subdic)
        else:
            new_dic[key]=dic[key]
    return new_dic

def save_dic(dic,website):
    # 要改为按每个日期来保存
    date_list=list(dic.keys())
    for date in date_list:
        try:#已经存在新闻文件了
            with open(f'./news/{website}_{date}.json','r',encoding='utf-8') as ft:
                dic_exit=json.load(ft)
            dic_total=merge_dic(dic_exit,dic[date])
            key_list=sorted(list(dic_total.keys()))
            dic_new={}
            for key in key_list:
                dic_new[key]=dic_total[key]
            with open(f'./news/{website}_{date}.json','w',encoding='utf-8') as fr:
                file=json.dumps(dic_new,ensure_ascii=False,indent=True)
                fr.write(file)

        except:# 还没有新闻文件就创建
            dic_new={}
            key_list=sorted(list(dic[date].keys()))
            for key in key_list:
                dic_new[key]=dic[date][key]
            with open(f'./news/{website}_{date}.json','w',encoding='utf-8') as fe:
                file=json.dumps(dic_new,ensure_ascii=False,indent=True)
                fe.write(file)

