"""
爬取原网页的html，过滤新闻内容并重新拼接，保留原网页样式。
"""

import pymysql
import datetime
import requests
from lxml import etree
import urllib3
import re
import pdfkit
from PyPDF2 import PdfFileMerger
import os
import time
# 敏感词过滤类，AC自动机
import Ac_auto

# 爬取的地址
spider_url = 'http://news.zzu.edu.cn/'
# 睡眠时间
sleep_time = 5
# mysql登录信息
conn = pymysql.connect(
    host='192.168.1.132',
    port=3307,
    user='root',
    passwd='123456',
    db='archive-spider',
    use_unicode=True,
    charset="utf8mb4"
)

# mysql 插入
# 插入spider任务表
insert_task = '''
INSERT INTO t_spider_task VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
'''
# 插入spider配置表
insert_conf = '''
INSERT INTO t_spider_conf VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
'''
# 插入spider结果表
insert_result = '''
INSERT INTO t_spider_result VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
'''

# pdfkit配置
confg = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

# 伪装http请求头部
headers = {
    'User-Agent':
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;'
}


# 查找所有栏目的url（栏目url），并保存
def all_urls_list():
    # 存储index的记录，放进数据库，如果已经存在，则不存储
    cur.execute("SELECT IFNULL((SELECT 1 from t_spider_result where url = %s limit 1), 0)", spider_url)
    judge = cur.fetchone()
    judge = judge[0]
    if not judge:
        # 获取配置表的id，赋值给结果表
        cur.execute("SELECT id FROM t_spider_conf WHERE domain = %s", spider_url)
        conf_id = cur.fetchone()
        conf_id = conf_id[0]

        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(insert_result, (conf_id, 'index', spider_url, '', '', '', time_now, '', '', ''))
        conn.commit()
    else:
        print('该主页记录已爬取过且保存在数据库中！')

    urls_list = []

    r = requests.get(spider_url, headers=headers)
    r.encoding = 'UTF-8'
    html = etree.HTML(r.text)

    # 郑大共有8个栏目
    for i in range(1, 9):
        news_heading_url = html.xpath('//*[@id="mytop_3"]/a[' + str(i) + ']/@href')
        news_heading_url = ''.join(news_heading_url)
        urls_list.append(news_heading_url)
    # print(urls_list)
    # 添加郑大通知公告url(学术动态和学校办公通知)：
    extra_url = ['http://www16.zzu.edu.cn/msgs/vmsgisapi.dll/vmsglist?mtype=m&lan=101,102,103',
                 'http://www16.zzu.edu.cn/msgs/vmsgisapi.dll/vmsglist?mtype=m&lan=105']
    for url in extra_url:
        urls_list.append(url)

    return urls_list


# 查找每个栏目下的每一页的url（列表url），并保存
def get_url_list(url):
    url_list = []
    r = requests.get(url, headers=headers)
    r.encoding = 'UTF-8'
    html = etree.HTML(r.text)

    # 查找最大页数
    page = html.xpath('//*[@id="bok_0"]/div[@class="zzj_4"]/text()[1]')
    page = ''.join(page)
    # print(page)
    search_obj = re.search(r'分\d+页', page)
    #print(search_obj.group())
    page = re.search(r'\d+', search_obj.group())
    # print(page.group())
    max_page = int(page.group())

    # 存储list第一页的记录，放进数据库，如果已经存在，则不存储
    temp_url = url + '&tts=&tops=&pn=1'
    cur.execute("SELECT IFNULL((SELECT 1 from t_spider_result where url = %s limit 1), 0)", temp_url)
    judge = cur.fetchone()
    judge = judge[0]
    if not judge:
        # 获取配置表的id，赋值给结果表
        cur.execute("SELECT id FROM t_spider_conf WHERE domain = %s", spider_url)
        conf_id = cur.fetchone()
        conf_id = conf_id[0]

        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(insert_result, (conf_id, 'list', temp_url, '', '', '', time_now, '', '', ''))
        conn.commit()
    else:
        print('该栏目首页记录已爬取过且保存在数据库中！')

    for i in range(1, max_page + 1):
        # print('爬取网上新闻的第{}页......'.format(i))
        temp_url = url + '&tts=&tops=&pn=' + str(i)
        url_list.append(temp_url)
    return url_list


# 查找每一页url里的新闻的url（细节url），并保存
def get_url_info(url_list):
    # 获取配置表的id，赋值给结果表
    cur.execute("SELECT id FROM t_spider_conf WHERE domain = %s", spider_url)
    conf_id = cur.fetchone()
    conf_id = conf_id[0]

    # 新闻数累加器
    sum_i = 0

    # 获取新闻栏目名
    r = requests.get(url_list[0], headers=headers)
    r.encoding = 'UTF-8'
    html = etree.HTML(r.text)
    news_heading = html.xpath('//*[@id="bok_0"]/div[@class="zzj_3"]/text()')
    news_heading = ''.join(news_heading)

    # 栏目下已存在新闻数统计器
    sql_heading = '%' + news_heading + '%'
    news_count = cur.execute("SELECT * FROM t_spider_result WHERE htmlPath LIKE %s", sql_heading)

    # 创建文件夹
    # 先判断文件夹是否存在，不存在则创建文件夹
    # now_dir = os.getcwd()
    new_dir = 'D:\\PycharmProjects\\zzu_spider' + '\\' + news_heading
    dir_judge = os.path.exists(new_dir)
    if not dir_judge:
        os.mkdir(new_dir)
        # print(new_dir)

    html_filter, news_url, news_title, news_author, news_time = '', '', '', '', ''
    # 合并pdf
    merger = PdfFileMerger()

    # 对每页的每个新闻做处理
    for i, url in enumerate(url_list):

        for j in range(0, 50):
            # 将新闻标题+内容整合，保存为字典
            # temp_info = {}

            r = requests.get(url, headers=headers)
            r.encoding = 'UTF-8'
            html = etree.HTML(r.text)
            tips = '正在获取{}栏目下第{}页第{}条新闻，总第{}条新闻......'.format(news_heading, i + 1, j + 1, sum_i + 1)
            print(tips)
            update_tips = '正在获取{}栏目下第{}页第{}条新闻，总第{}条新闻......'.format(news_heading, i + 1, j + 1, news_count + 1)
            try:
                xpath_temp = '//*[@id="bok_0"]/div[@class="zzj_5"]/div[' + str(1 + j * 2) + ']/a/'
                # temp_info['title'] = html.xpath(xpath_temp + 'span/text()')[0]
                news_title = html.xpath(xpath_temp + 'span/text()')[0]
                # 新闻的具体url
                news_url = html.xpath(xpath_temp + '@href')
                news_url = ''.join(news_url)
                # print(news_url)
                # 引入tips, 查找爬虫出错未爬取到的空的新闻内容
                # temp_info['content'] = get_url_content(news_url, tips)
                # print(temp_info)
                print('新闻标题：{}'.format(news_title))

                # 存储栏目第一页第一条新闻的记录，如果已经存在，则直接跳出循环，不再进行爬取
                # 如果不存在，则说明有更新，爬取新的并向下查找
                cur.execute("SELECT IFNULL((SELECT 1 from t_spider_result where title = %s limit 1), 0)", news_title)
                judge = cur.fetchone()
                judge = judge[0]

                if not judge:

                    res = requests.get(news_url, headers=headers)
                    res.encoding = 'UTF-8'
                    raw_html = res.text

                    # 对直接跳转的网页做处理
                    search_refresh = re.search(r'http-equiv="refresh".*\'', raw_html)
                    if search_refresh:
                        # print(search_refresh.group())
                        refresh_url = re.search(r'[a-zA-z]+://[^\s]*\w', search_refresh.group())
                        refresh_url = refresh_url.group()

                        # 使requests忽略对SSL的验证和报错, 否则会过度连接
                        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                        refresh_res = requests.get(refresh_url, headers=headers, verify=False)
                        refresh_res.encoding = 'UTF-8'
                        # print(refresh_res)
                        raw_html = refresh_res.text
                        judge_identifier = not_found_judge(raw_html)
                        # 对非404 not found的网页做进一步处理
                        if judge_identifier:
                            # print(raw_html)
                            html_filter = sensitive_word_filter(raw_html)
                            html_filter = img_update(html_filter)
                            # 增加文件是否存在的判断，避免覆盖写入，若有更新，重新起名
                            file_path = new_dir + '\\' + tips[4:-6] + '.html'
                            if os.path.exists(file_path):
                                with open(new_dir + '\\(更新)' + update_tips[4:-6] + '.html', 'w+', encoding='UTF-8') as f1:
                                    f1.write(html_filter)
                                # html转pdf
                                pdfkit.from_url(refresh_url, new_dir + '\\(更新)' + update_tips[4:-6] + '.pdf', configuration=confg)
                            else:
                                with open(file_path, 'w+', encoding='UTF-8') as f1:
                                    f1.write(html_filter)
                                # html转pdf
                                pdfkit.from_url(refresh_url, new_dir + '\\' + tips[4:-6] + '.pdf', configuration=confg)
                                # 因跳转到不同网站的xpath不同，获取不到统一的xpath，故news_author, news_time都为空
                        else:
                            # 将404 not found 记录进数据库
                            html_filter = '404 not found'
                            time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            cur.execute(insert_result,
                                        (conf_id, 'detail', news_url, html_filter, '', '', time_now,
                                         news_title, news_author, news_time))
                            conn.commit()

                    # 对非跳转网页做处理
                    else:
                        judge_identifier = not_found_judge(raw_html)
                        # 对非404 not found的网页做进一步处理
                        if judge_identifier:
                            html = etree.HTML(raw_html)
                            news_author = html.xpath('//*[@id="bok_0"]/div[@class="zzj_4"]/span[1]/text()')
                            news_time = html.xpath('//*[@id="bok_0"]/div[@class="zzj_4"]/span[3]/text()')

                            html_filter = sensitive_word_filter(raw_html)
                            # html_filter = img_update(html_filter)
                            # print(html_filter)

                            # 增加文件是否存在的判断，避免覆盖写入，若有更新，重新起名
                            file_path = new_dir + '\\' + tips[4:-6] + '.html'
                            if os.path.exists(file_path):
                                # 记录爬取的html原码
                                with open(new_dir + '\\(更新)' + update_tips[4:-6] + '.html', 'w+', encoding='UTF-8') as f1:
                                    f1.write(html_filter)

                                # 对html原码中不能正确解析的黑体做调整
                                err_index = html_filter.find('黑体')
                                if err_index != -1:
                                    html_filter = html_filter[:err_index] + '宋体' + html_filter[err_index + len('黑体'):]

                                # html转pdf
                                pdfkit.from_string(html_filter, new_dir + '\\(更新)' + update_tips[4:-6] + '.pdf',
                                                   configuration=confg)
                            else:
                                # 记录爬取的html原码
                                with open(file_path, 'w+', encoding='UTF-8') as f1:
                                    f1.write(html_filter)

                                # 对html原码中不能正确解析的黑体做调整
                                err_index = html_filter.find('黑体')
                                if err_index != -1:
                                    html_filter = html_filter[:err_index] + '宋体' + html_filter[err_index + len('黑体'):]

                                # html转pdf
                                pdfkit.from_string(html_filter, new_dir + '\\' + tips[4:-6] + '.pdf', configuration=confg)
                        else:
                            # 将404 not found 记录进数据库
                            html_filter = '404 not found'
                            time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            cur.execute(insert_result,
                                        (conf_id, 'detail', news_url, html_filter, '', '', time_now,
                                         news_title, news_author, news_time))
                            conn.commit()
                else:
                    print('该新闻《{}》已爬取过且保存在数据库中！'.format(news_title))
                    break

            except IOError:
                print("Warning: wkhtmltopdf读取文件失败, 可能是网页无法打开或者图片/css样式丢失。")
            except IndexError:
                print("该栏目《{}》下的新闻已全部爬取完！".format(news_heading))
                break
            finally:
                update_html_file = new_dir + '\\(更新)' + update_tips[4:-6] + '.html'
                update_pdf_file = new_dir + '\\(更新)' + update_tips[4:-6] + '.pdf'
                # 判断是不是栏目下新闻的更新产生了新的文件
                update_judge = os.path.exists(update_pdf_file)

                # 确保不会有重复记录存入数据库
                cur.execute("SELECT IFNULL((SELECT 1 from t_spider_result where title = %s limit 1), 0)",
                            news_title)
                judge = cur.fetchone()
                judge = judge[0]

                if not judge:
                    if not update_judge:
                        html_file = new_dir + '\\' + tips[4:-6] + '.html'
                        # 合并pdf
                        pdf_file = new_dir + '\\' + tips[4:-6] + '.pdf'
                        file_judge = os.path.exists(pdf_file)
                        if file_judge:
                            try:
                                time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                cur.execute(insert_result, (conf_id, 'detail', news_url, html_filter, html_file, pdf_file, time_now,
                                                            news_title, news_author, news_time))
                                merger.append(open(pdf_file, 'rb'))
                                conn.commit()
                            except pymysql.err.DataError:
                                print("html编码错误或值错误！")
                                html_filter = html_filter.encode(encoding='UTF-8', errors='ignore')
                                time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                cur.execute(insert_result,
                                            (conf_id, 'detail', news_url, html_filter, html_file, pdf_file, time_now,
                                             news_title, news_author, news_time))
                                merger.append(open(pdf_file, 'rb'))
                                conn.commit()

                    else:
                        try:
                            time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            cur.execute(insert_result,
                                        (conf_id, 'detail', news_url, html_filter, update_html_file, update_pdf_file, time_now,
                                         news_title, news_author, news_time))
                            merger.append(open(update_pdf_file, 'rb'))
                            conn.commit()
                        except pymysql.err.DataError:
                            print("html编码错误或值错误！")
                            html_filter = html_filter.encode(encoding='UTF-8', errors='ignore')
                            time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            cur.execute(insert_result,
                                        (conf_id, 'detail', news_url, html_filter, update_html_file, update_pdf_file, time_now,
                                         news_title, news_author, news_time))
                            merger.append(open(update_pdf_file, 'rb'))
                            conn.commit()
                else:
                    print('该新闻《{}》已保存在数据库中！'.format(news_title))
                sum_i += 1
                news_count += 1
                # 清空之前的信息
                html_filter, news_url, news_title, news_author, news_time = '', '', '', '', ''

        else:
            continue
        # 内循环break（更新已完成/无更新导致的break），则跳出双重循环
        print('该栏目《{}》下的新闻无更新或更新已完成！\n'.format(news_heading))
        time.sleep(sleep_time)
        break

    # 合并pdf
    # 如果存在更新的新闻，则合并更新的新闻
    merge_pdf_path = new_dir + '\\' + news_heading + '_合并.pdf'
    if len(merger.pages):
        if os.path.exists(merge_pdf_path):
            merger.write(new_dir + '\\' + news_heading + '_' + str(news_count-1) + '条新闻后的更新合并.pdf')
            print('{}栏目pdf更新合并完成\n'.format(news_heading))
        else:
            merger.write(merge_pdf_path)
            print('{}栏目pdf合并完成\n'.format(news_heading))


# 获取具体一条新闻的内容
# def get_url_content(news_url, tips):
#     r = requests.get(news_url, headers=headers)
#     r.encoding = 'UTF-8'
#     sub_html = etree.HTML(r.text)
#     # 对内容做处理，删除空格换行转义等等字符，并进行关键词校验屏蔽
#     # 关键字的校验屏蔽。（关键字：指的是反动言论，不文明词汇）
#     content = sub_html.xpath('//*[@id="bok_0"]/div[@class="zzj_5"]//text()')
#     content = ''.join(content)
#     content = re.sub(r'\s', '', content)
#
#     # print(content)
#     content = sensitive_word_filter(content)
#
#     # 如果出现空的内容，输出具体出错的新闻位置并生成txt
#     if content == '':
#         with open('C:/Users/mcgra/Desktop/spider_error.txt', 'a+') as f1:
#             f1.write(tips)
#             f1.write('\n')
#
#     return content


# 判断网页是否是404_not_found, 并返回一个判断标识, 0为空网页，1为正常网页
def not_found_judge(html):
    judge_identifier = 1
    # temp/temp_2 找到'404 not found'/'页面不存在'返回下标，找不到为-1
    temp = html.find('404 Not Found')
    temp_2 = html.find('页面不存在')
    temp_3 = html.find('页面未找到')
    if temp != -1 or temp_2 != -1 or temp_3 != -1:
        judge_identifier = 0
        print('该网页目前无法访问！')
    return judge_identifier


# 敏感词过滤
def sensitive_word_filter(content):
    ah = Ac_auto.ac_automation()
    path = 'sensitive_words.txt'
    ah.parse(path)
    content = ah.words_replace(content)
    # text1 = "新疆骚乱苹果新品发布会"
    # text2 = ah.words_replace(text1)
    # print(text1)
    # print(text2)

    return content


# 图片新闻板块图片替换
def img_update(content):
    new_html = content

    pattern = "(img src=\")(.*?)(.s)(.jpg\")"

    def func(m):
        rtn = m.group(1) + m.group(2) + m.group(4)
        return rtn

    temp = re.compile(pattern)
    new_html = temp.sub(func, new_html)

    return new_html


def main():
    # 郑大新闻网所有的栏目链接
    all_urls = all_urls_list()
    # all_urls.remove('http://www16.zzu.edu.cn/msgs/vmsgisapi.dll/vmsglist?mtype=x&lan=202')
    # all_urls = ['http://www16.zzu.edu.cn/msgs/vmsgisapi.dll/vmsglist?mtype=x&lan=201']

    for url in all_urls:
        url_list = get_url_list(url)
        get_url_info(url_list)

    time.sleep(sleep_time)
    print('{}的爬虫任务已完成！'.format(spider_url))


if __name__ == '__main__':
    cur = conn.cursor()
    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 任务id
    task_id = 1
    # cur.execute(insert_task, (task_id, '郑大新闻网新闻爬取', '0 0 10 ? 7 * 2020', '', 0, 0, None, time_now))
    # cur.execute(insert_conf, (task_id, spider_url, sleep_time, r'.*&tts=&tops=&pn=\d*', r'.*onemsg[?]msgid=\d*',
    #                           '//*[@id="bok_0"]/div[@class="zzj_3"]/text()',
    #                           '//*[@id="bok_0"]/div[@class="zzj_4"]/span[3]/text()',
    #                           '//*[@id="bok_0"]/div[@class="zzj_4"]/span[1]/text()',
    #                           '//*[@id="bok_0"]/div[@class="zzj_5"]//text()', time_now, time_now))
    # conn.commit()
    main()
    # 爬虫结束，更新爬虫状态为-1，停止
    cur.execute("UPDATE t_spider_task SET status = -1 WHERE id = %s", task_id)
    cur.close()
    conn.commit()
    conn.close()
