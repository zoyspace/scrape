from playwright.sync_api import sync_playwright
import time,json,re,os
import datetime
from urllib.parse import unquote
DOMAIN_URL = 'https://beauty.hotpepper.jp/'
PREFECTURES = {'北海道':'pre01','埼玉県':'pre11','千葉県':'pre12','東京都':'pre13' ,'神奈川県':'pre14','滋賀県':'pre25','京都府':'pre26','大阪府':'pre27','兵庫県':'pre28','奈良県':'pre29','和歌山県':'pre30','福岡県':'pre40','佐賀県':'pre41','長崎県':'pre42','大分県':'pre44','熊本県':'pre43','宮崎県':'pre45','鹿児島県':'pre46','沖縄県':'pre47'}
DEV_FLAG = False
result_dir = './temp_salon_lists'

def get_last_id():
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    file_names = os.listdir(result_dir)
    if len(file_names) == 0:
        return 0,0
    sorted_file_names = sorted(file_names)
    last_file_name = sorted_file_names[-1]
    match_num = re.search(r"\d+", last_file_name) # 文字列から数値を抽出
    outfile_num = int(match_num.group(0)) # 数値に変換
    with open(f'{result_dir}/{last_file_name}', 'r', encoding='utf-8') as f:
        last_json_data = json.load(f)
    last_salon_data = last_json_data[-1]
    last_salon_id = last_salon_data['id']
    
    return outfile_num,last_salon_id

def get_card_urls(page,prefecture_id,page_num,card_urls):
    cards = page.query_selector_all('.slnCassetteList  .slnCassetteHeader')
    
    for index,card in enumerate(cards):
        slnName_element = card.query_selector('.slnName a')
        name_text = slnName_element.inner_text()
        url_text = slnName_element.get_attribute('href')
        work_dic = {"id":f'{prefecture_id}_{page_num}_{index+1}',"name":name_text,"url":url_text}
        card_urls.append(work_dic)
    return card_urls

def get_allpage(page):
    page_text = page.query_selector('div.preListHead > div > p.pa.bottom0.right0').inner_text()
    allpage = re.search(r'/(\d+)ページ', page_text) # 1/200ページのうち、200を取得
    return allpage.group(1)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        prefectures = list(PREFECTURES.keys())
        out_lists =[]
        outfile_num,resume_num = get_last_id()
        id = 0
        for index,prefecture in enumerate(prefectures):
            card_urls = []
            prefecture_id = PREFECTURES[prefecture]
            print(f'{prefecture}の店舗一覧を取得中')
            target_url_first = DOMAIN_URL + prefecture_id

            page.goto(target_url_first)
            page.wait_for_load_state()
            allpage = get_allpage(page)
            print(f'全ページ数:{allpage}')

            card_urls = get_card_urls(page,prefecture_id,1,card_urls)

            for page_num in range(2,int(allpage)+1):
                target_url = f'{target_url_first}/PN{page_num}' 
                page.goto(target_url)
                page.wait_for_load_state()
                card_urls = get_card_urls(page,prefecture_id,page_num,card_urls)
                if page_num % 20 == 0:
                    print(f'{page_num}ページ目取得中')
                if page_num  == 2 and DEV_FLAG:break

            with open(f'{result_dir}/lists_{prefecture_id}.json', 'w') as file:
                json.dump(card_urls, file, ensure_ascii=False, indent=4) # ensure_ascii=Falseで日本語文字化け対策
            if index  == 1 and DEV_FLAG:break

        
        if DEV_FLAG:
            html_content = page.content()
            with open("_output.html", "w") as file:
                file.write(html_content)
        
        browser.close()
    

if __name__ == "__main__":
    start_time = time.time()
    main()
    processing_time = time.time() - start_time
    print(f'処理時間(s）: {round(processing_time,1)}')
