import os
import spider_36ke
import spider_jiemian
import spider_cls
import funcs

op=1
'''
op=1：爬虫并且保存
op=2：将本地的html重新扫描保存
op=3：将各个平台的json按日期合并
'''
if op==1:
    os.system('python spider_36ke.py')
    os.system('python spider_jiemian.py')
    os.system('python spider_cls.py')

if op==2:
    spider_36ke.htmls2jsons('./html','36ke')
    spider_jiemian.htmls2jsons('./html','jiemian')
    spider_cls.htmls2jsons('./html','cls')

if op==3:
    funcs.merge_jsons('./news')

