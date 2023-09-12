from playwright.sync_api import sync_playwright
import time,json,re
import datetime
from urllib.parse import unquote
DOMAIN_URL = 'https://beauty.hotpepper.jp/'
PREFECTURES = {"神奈川県":"pre14",'東京都':"pre13",'大分':'pre44','長崎':'pre42'}
DEV_WRITEFILE_FLAG = True

def get_card_urls(page,page_num,card_urls):
    cards = page.query_selector_all('.slnCassetteList  .slnCassetteHeader')
    
    for index,card in enumerate(cards):
        slnName_element = card.query_selector('.slnName a')
        name_text = slnName_element.inner_text()
        url_text = slnName_element.get_attribute('href')
        work_dic = {"id":f'{page_num}_{index+1}',"name":name_text,"url":url_text}
        card_urls.append(work_dic)
    return card_urls

def extract_data_from_page(page):
    shop_data = {}
    name_element = page.query_selector('.sprtHeaderInner')
    shop_data['name'] = name_element.query_selector('.detailTitle').inner_text()
    shop_data['name_kana'] = name_element.query_selector('p.fs10').inner_text()
    shop_data['pankuzu'] = page.query_selector('.pankuzu').inner_text()
    slide_image_element = page.query_selector_all('.slnHeaderSliderPoint li')
    shop_data['slide_num'] = len(slide_image_element)
    shop_data['catch_copy'] = page.query_selector('.shopCatchCopy').inner_text()  

    rows = page.query_selector_all("table.slnDataTbl tr")
    for row in rows:
        th_elements = row.query_selector_all("th")
        td_elements = row.query_selector_all("td")

        if th_elements and td_elements:
            for th, td in zip(th_elements, td_elements):
                th_text = th.inner_text()
                td_text = td.inner_text()
                shop_data[th_text] = td_text
    
    
                # print(f"{th_text}: {td_text}")
        
    return shop_data

def get_allpage(page):
    page_text = page.query_selector('div.preListHead > div > p.pa.bottom0.right0').inner_text()
    allpage = re.search(r'/(\d+)ページ', page_text) # 1/200ページのうち、200を取得
    return allpage.group(1)

def read_file_urls():
    with open('urls.json', 'r') as f:
        json_data = json.load(f)
    for data in json_data:
        prefecture = data['prefecture']
        card_urls = data['card_urls']
        print(f'{prefecture}:{len(card_urls)}')
    return urls

def main():
    with sync_playwright() as p:
        # browser = p.chromium.launch()
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        prefectures = list(PREFECTURES.keys())
        out_urls =[]
        for index,prefecture in enumerate(prefectures):
            print(f'{index+1}:{prefecture}')
            target_url_first = DOMAIN_URL + PREFECTURES[prefecture]
            prefecture_obj = {'prefecture':prefecture}

            page.goto(target_url_first)
            page.wait_for_load_state()
            allpage = get_allpage(page)
            prefecture_obj['allpage'] = allpage

            card_urls = []
            card_urls = get_card_urls(page,1,card_urls)

            for page_num in range(2,int(allpage)+1):
                target_url = f'{target_url_first}/PN{page_num}' 
                page.goto(target_url)
                page.wait_for_load_state()
                card_urls = get_card_urls(page,page_num,card_urls)
                if page_num  == 2 and DEV_WRITEFILE_FLAG:break
            prefecture_obj['card_urls'] = card_urls
            out_urls.append(prefecture_obj)
            if index  == 1 and DEV_WRITEFILE_FLAG:break

        with open("urls.json", "w") as file:
            json.dump(out_urls, file, ensure_ascii=False, indent=4) # ensure_ascii=Falseで日本語文字化け対策
        
        shop_datas = []
        for index1,shops in enumerate(out_urls):
            prefecture = shops['prefecture']
            for i2,shop in enumerate(shops['card_urls']):
                target_url = shop['url']
                page.goto(target_url)
                page.wait_for_load_state()
                # 関数
                shop_data = extract_data_from_page(page)
                shop_data['prefecture'] = prefecture
                shop_data['shop_url'] = target_url
                shop_datas.append(shop_data)
                if i2 == 2 and DEV_WRITEFILE_FLAG:break
            if index1 == 2 and DEV_WRITEFILE_FLAG:break
        with open("shop_datas.json", "w") as file:
            json.dump(shop_datas, file, ensure_ascii=False, indent=4) # ensure_ascii=Falseで日本語文字化け対策

        # print(f'current_url: {target_url}')
        # with open("titles.txt", "w") as file:
        # for index,prefecture in enumerate(prefectures):
        # target_url = DOMAIN_URL + PREFECTURES[prefecture]
        # page.goto(target_url)
        # page.wait_for_load_state()
        
        
        # page.wait_for_load_state()
    
        
        #　店舗ページに移動
        # page.goto(card_urls[0])
        # page.wait_for_load_state()
        
        # extract_data_from_page(page)

        if DEV_WRITEFILE_FLAG:
            html_content = page.content()
            with open("_output.html", "w") as file:
                file.write(html_content)
        
        browser.close()
    

if __name__ == "__main__":
    start_time = time.time()
    main()
    processing_time = time.time() - start_time
    print(f'処理時間(s）: {round(processing_time,1)}')
