from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import pandas as pd
import time


def extract_data(html_code):

    current_page_data = []
    item_pattern = re.compile(r'<li>\s*<div class="item">(.*?)</div>\s*</li>', re.S)
    items = re.findall(item_pattern, html_code)
    print(f"匹配到的电影条目数量：{len(items)}")

    for item in items:
        # 提取中文名称
        chinese_title = re.findall(r'<span class="title">([^<]+)</span>', item)
        chinese_title = chinese_title[0] if chinese_title else ''

        # 提取英文名称
        foreign_title = re.findall(r'<span class="title">&nbsp;/&nbsp;(.*?)</span>', item)
        foreign_title = foreign_title[0].replace('&nbsp;', ' ').strip() if foreign_title else ''

        # 提取评分
        rating = re.findall(r'<span class="rating_num".*?>([^<]+)</span>', item)
        rating = rating[0] if rating else ''

        # 提取评价人数
        votes = re.findall(r'<span>(\d+)人评价</span>', item)
        votes = votes[0] if votes else ''

        soup = BeautifulSoup(item, 'html.parser')
        p_tag = soup.find('p')
        if p_tag:
            text = p_tag.text
            director_start = text.find('导演: ') + len('导演: ')
            director_end = text.find('主')
            director = text[director_start:director_end].strip()



        # 提取年份、国家、类型（精确匹配结构）
        details_match = re.search(r'<br>\s*([\d]{4})&nbsp;/&nbsp;([^&<]+)&nbsp;/&nbsp;([^<]+)',item)
        year = details_match.group(1) if details_match else ''
        country = details_match.group(2).strip() if details_match else ''
        genre = details_match.group(3).strip() if details_match else ''

        # 提取简介（包含换行符处理）
        quote_match = re.search(r'<p class="quote">\s*<span>(.*?)</span>',item)
        quote = quote_match.group(1).strip() if quote_match else ''

        current_page_data.append({
            '中文名称': chinese_title,
            '外文名称': foreign_title,
            '评分': rating,
            '评价人数': votes,
            '导演': director,
            '年份': year,
            '国家/地区': country,
            '类型': genre,
            '评价': quote
        })

    return pd.DataFrame(current_page_data)

def get_douban_movies(start_page, end_page):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    browser = webdriver.Chrome(options=chrome_options)
    browser.maximize_window()

    all_data = []

    for page in range(start_page, end_page + 1):
        url = f'https://movie.douban.com/top250?start={(page - 1) * 25}'
        browser.get(url)
        try:
            # 显式等待直到电影条目加载完成
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "item"))
            )
        except:
            print(f"第{page}页加载超时")
            continue

        # 提取数据
        df = extract_data(browser.page_source)
        if not df.empty:
            all_data.append(df)
            print(f'已爬取第{page}页数据，共{len(df)}条记录')
        else:
            print(f'第{page}页未提取到数据，请检查页面结构或正则表达式')

        time.sleep(3)  # 避免频繁请求

    browser.quit()

    if all_data:

        final_df = pd.concat(all_data, ignore_index=True)
        final_df.to_excel('Top250.xlsx', index=False)
        print('数据已保存至 Top250.xlsx')

    else:
        print('未获取到任何数据')


# 测试爬取
get_douban_movies(1, 10)