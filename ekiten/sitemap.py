import requests
from bs4 import BeautifulSoup
import json
import time
# import pretty_errors
from rich import print
import tqdm

# URLを指定
target_todofuken = ['北海道', '東京都', '神奈川県', '千葉県', '埼玉県', '大阪府', '京都府', '兵庫県',
                    '滋賀県', '奈良県', '和歌山県', '福岡県', '佐賀県', '大分県', '長崎県', '熊本県', '宮崎県', '鹿児島県', '沖縄県']
max_page = 1
out_todofuken_folder = 'todofuken_group/'
out_todofuken = []

def main():
    domain_url = 'https://www.ekiten.jp/sitemap/'

    with open('todofuken.json', 'r', encoding='utf-8') as file:
        json_todofuken = json.load(file)

    for index1, todofuken in enumerate(target_todofuken):
        todofuken_city_dic = {'todofuken': todofuken}
        target_url = domain_url + json_todofuken[todofuken]
        todofuken_city_dic['url'] = target_url

        city_list = getCityList(target_url) # [{cityname:川崎市}、{横浜市}、{相模原市}...
        todofuken_city_dic['cities_length'] = len(city_list)
        
        for index11,city in enumerate(city_list):
            group_list = getGroup(city['city_url']) # [{group_name:美容室・美容院・ヘアサロン}、{ネイルサロン}、{エステサロン}...
            city_list[index11]['group_length'] = len(group_list)
            city_list[index11]['group'] = group_list

            if index11 >= 3:
                break
        todofuken_city_dic['cities'] = city_list

        with open(f'{out_todofuken_folder}{todofuken}.json', "w", encoding="utf-8") as file:
            json.dump(todofuken_city_dic, file, ensure_ascii=False, indent=4)

        if index1 >= max_page:
            break



def getCityList(url):
    out = []
    # HTTP GETリクエストを送信
    response = requests.get(url)

    # ステータスコードを確認（200なら成功）
    if response.status_code != 200:
        print(f'Failed to get data from {url}')

    html = response.text

    soup = BeautifulSoup(html, 'html.parser')
    city_elements = soup.select(
        'section.ll-m-contentSection--lv-2:nth-of-type(1) .ll-m-textList__item .ll-a-textLink')
    # selectメソッドを使ってhrefとlabelを取得
    for index ,a_tag in enumerate(city_elements):
        tmp = {}
        tmp['city_name'] = a_tag.select_one('.ll-a-textLink__label').text
        tmp['city_url'] = a_tag['href']

        out.append(tmp)

    return out


def getGroup(url):
    out = []
    response = requests.get(url)
    if response.status_code != 200:
        print(f'Failed to get data from {url}')
    soup = BeautifulSoup(response.text, 'html.parser')
    group_elements = soup.select(
        '.ll-m-textList__item > h3 > a')
    for atag in group_elements:
        tmp = {}
        tmp['group_name'] = atag.text.strip()
        tmp['group_url'] = atag['href']
        out.append(tmp)
    return out
    


if __name__ == '__main__':
    start_time = time.time()
    # getGroup('https://www.ekiten.jp/sitemap/p14/a14131/')
    main()
    processing_time = time.time() - start_time
    print(f'処理時間(s): {round(processing_time,1)}')

# [
#     {'todofuken':'神奈川県',
#      'cities':[{'city_name':'横浜市',
#               city_url:'https://aaaa',
#              'group':[{'group_name':'美容室・美容院・ヘアサロン',
#                    'group_url':'https://sssss'},
#                    {'group_name':'美容室・美容院・ヘアサロン',
#                    'group_url':'https://sssss'}]
#             },
#             {'cityname':'川崎市',
#               url:'https://aaaa',
#              'group':[{'group_name':'美容室・美容院・ヘアサロン',
#                    'group_url':'https://sssss'},

#                    {'group_name':'美容室・美容院・ヘアサロン',
#                    'group_url':'https://sssss'}]
#             },
            
#             ]
#     },
#     {'todofuken':'千葉県'}
# ]