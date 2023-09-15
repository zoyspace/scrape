from playwright.sync_api import sync_playwright
import time,json,re,os
from tqdm import tqdm

from settings import (
    DOMAIN_URL,
    PREFECTURES,
    LIST_DEV_FLAG,
    LIST_BATCH_SIZE,
    LISTS_DIR
)

RESULT_DIR = LISTS_DIR

def get_exit_file():
    if not os.path.exists(RESULT_DIR):
        os.mkdir(RESULT_DIR)
    file_names = os.listdir(RESULT_DIR)
    
    return file_names

def get_card_urls(page,prefecture_id,prefecture,page_num,card_urls):
    cards = page.query_selector_all('.slnCassetteList  .slnCassetteHeader')
    
    for index,card in enumerate(cards):
        slnName_element = card.query_selector('.slnName a')
        name_text = slnName_element.inner_text()
        url_text = slnName_element.get_attribute('href')
        work_dic = {"id":f'{prefecture_id}_{page_num}_{index+1}','prefecture':prefecture,"name":name_text,"url":url_text}
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
        exit_files = get_exit_file()
        for index,prefecture in enumerate(prefectures):
            card_urls = []
            prefecture_id = PREFECTURES[prefecture]
            out_file_name = f'lists_{prefecture_id}.json'

            if out_file_name in exit_files:
                print(f'{prefecture}の店舗一覧は既に取得済みです')
                continue

            print(f'{prefecture}の店舗一覧を取得中')
            target_url_first = DOMAIN_URL + prefecture_id

            page.goto(target_url_first)
            page.wait_for_load_state()
            allpage = get_allpage(page)
            print(f'全ページ数:{allpage}')

            card_urls = get_card_urls(page,prefecture_id,prefecture,1,card_urls)

            for page_num in tqdm(range(2,int(allpage)+1)):
                target_url = f'{target_url_first}/PN{page_num}' 
                page.goto(target_url)
                page.wait_for_load_state()
                card_urls = get_card_urls(page,prefecture_id,prefecture,page_num,card_urls)
                if page_num % LIST_BATCH_SIZE == 0:
                    print(f'{page_num}ページ取得済')
                if page_num  == 2 and LIST_DEV_FLAG:break

            with open(f'{RESULT_DIR}/{out_file_name}', 'w') as file:
                json.dump(card_urls, file, ensure_ascii=False, indent=4) # ensure_ascii=Falseで日本語文字化け対策
            if index  == 1 and LIST_DEV_FLAG:break

        
        if LIST_DEV_FLAG:
            html_content = page.content()
            with open("_output.html", "w") as file:
                file.write(html_content)
        
        browser.close()
    

if __name__ == "__main__":
    start_time = time.time()
    main()
    processing_time = time.time() - start_time
    print(f'処理時間(s）: {round(processing_time,1)}')
