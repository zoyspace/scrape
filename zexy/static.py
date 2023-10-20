import requests
from bs4 import BeautifulSoup
import json
import time
# import pretty_errors
from rich import print
from tqdm import tqdm

# URLを指定
target_todofuken = ['北海道', '東京都', '神奈川県', '千葉県', '埼玉県', '大阪府', '京都府', '兵庫県',
                    '滋賀県', '奈良県', '和歌山県', '福岡県', '佐賀県', '大分県', '長崎県', '熊本県', '宮崎県', '鹿児島県', '沖縄県']
main_url = 'https://zexy.net/'
out_todofuken_folder = 'todofuken/'
out_detail_folder = 'detail/'
out_todofuken = []


def main():
    domain_url = 'https://zexy.net/wedding/'
    list_url_part = '/clientList/'
    with open('todofuken.json', 'r', encoding='utf-8') as file:
        dic_todofuken = json.load(file)

    for key, value in dic_todofuken.items():
        target_url = f'{domain_url}{value}{list_url_part}'
        getHallList(key, target_url)


def getHallList(todofuken, url):
    out_list = []
    print(f'都道府県名: {todofuken}')
    page_num = 1
    # HTTP GETリクエストを送信
    response = requests.get(url)

    # ステータスコードを確認（200なら成功）
    if response.status_code != 200:
        print(f'Failed to get data from {url}')
        exit()

    html = response.text
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(html)

    soup = BeautifulSoup(html, 'html.parser')
    total_text = soup.select_one('.locator strong.total').text
    print(f'店舗数: {total_text}')
    total_num = int(total_text.replace(',', ''))

    out_list.extend(getHollUrlPage(soup))
    list_num = len(out_list)

    while total_num > list_num:
        page_num += 1
        target_url = f'{url}p_{page_num}/'
        response = requests.get(target_url)
        if response.status_code != 200:
            print(f'Failed to get data from {target_url}')
            exit()
        soup = BeautifulSoup(response.text, 'html.parser')
        out_list.extend(getHollUrlPage(soup))
        list_num = len(out_list)

    print(f'page_num: {page_num} list_num: {list_num}')
    with open(f'{out_todofuken_folder}{todofuken}_list.json', "w", encoding="utf-8") as file:
        json.dump(out_list, file, ensure_ascii=False, indent=4)


def getHollUrlPage(soup):
    out = []

    hall_elements = soup.select('ul.clientList > li')
    print(len(hall_elements))
    # selectメソッドを使ってhrefとlabelを取得
    for index, element in enumerate(hall_elements):
        tmp = {}
        a_tag = element.select_one('a.jscTitleLink')

        tmp['hall_name'] = a_tag.text
        tmp['hall_url'] = main_url + a_tag['href']
        if (element.select_one('dl')):
            tmp['detail'] = True
        else:
            tmp['detail'] = False

        # print(f'{index+1} {tmp["hall_name"]}')

        out.append(tmp)
    with open(f'{out_todofuken_folder}{todofuken}_list.json', "w", encoding="utf-8") as file:
        json.dump(out_list, file, ensure_ascii=False, indent=4)



def getHallDetail(url):
    out_detail = []
    tmp_dic = {}
    tmp_dic['URL'] =  url
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f'Failed to get data from {url}')
    soup = BeautifulSoup(response.text, 'html.parser')
    title_element = soup.select_one('div.clientName')
    title =  title_element.find('h1').get_text(strip=True)
    subtitle= title_element.get_text(strip=True).replace(title, '')
    if subtitle == '':
        subtitle = 'none'
    tmp_dic['ホール名'] =  title
    tmp_dic['グループ名'] =  subtitle

    location_area_text = soup.select_one('.locationInner .locationLink').get_text(strip=True)
    tmp_dic['エリア名'] =  location_area_text

    location_row = soup.find('th', string='所在地').find_parent('tr')
    location_text = location_row.find('span').get_text(strip=True)
    tmp_dic['所在地'] =  location_text

    return tmp_dic

def hallDetailWithFile(file_name = '神奈川県_list.json'):
    with open(f'{out_todofuken_folder}{file_name}', 'r', encoding='utf-8') as file:
        dic_todofuken = json.load(file)
    out = []
    print(f'{file_name}店舗数：{len(dic_todofuken)}')

    for dic in tqdm(dic_todofuken):
        if dic['detail'] == False:
            continue
        target_url = dic['hall_url']
        out.append(getHallDetail(target_url))

    with open(f'{out_detail_folder}detail.json', "w", encoding="utf-8") as file:
        json.dump(out, file, ensure_ascii=False, indent=4)



if __name__ == '__main__':
    start_time = time.time()

    # getHallDetail('https://zexy.net/wedding/c_7770077091/?inrlead=hallClient_topMenuTab')
    # getHallDetail('https://zexy.net/wedding/c_7770042511/?inrlead=hallClient_topMenuTab')
    # main()
    hallDetailWithFile()

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
