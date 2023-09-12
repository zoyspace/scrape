from playwright.sync_api import sync_playwright
import time, datetime
import json
from urllib.parse import unquote

domain_url = 'https://beauty.hotpepper.jp/'
prefectures = {"神奈川県":"pre14",'東京都':"pre13"}

search_keyword = 'パソコン'

dev_writefile_flag = True
next_page_flag = True
max_page = 1
out = {}



dt_now = datetime.datetime.now()
start_time = time.time()
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    # browser = p.chromium.launch()
    target_url = domain_url + prefectures["神奈川県"] 
    print(f'current_url: {target_url}')
    page = browser.new_page()
    page.goto(target_url)
    page.wait_for_load_state()
    
    cards = page.query_selector_all('.slnCassetteList  .slnCassetteHeader')
    print(len(cards))
    urls = []
    for index, card in enumerate(cards):
        name_element = card.query_selector('.slnName')
        url_text = card.query_selector('.slnName a').get_attribute('href')
        urls.append(url_text)

    #　店舗ページに移動
    page.goto(urls[0])
    print(page.url)
    page.wait_for_load_state()
    # テーブルの各行を取得
    rows = page.query_selector_all("table.slnDataTbl tr")
    for row in rows:
        th_elements = row.query_selector_all("th")
        td_elements = row.query_selector_all("td")

        if th_elements and td_elements:
            for th, td in zip(th_elements, td_elements):
                th_text = th.inner_text()
                td_text = td.inner_text()
                print(f"/")
                print(f"{th_text}: {td_text}")

    if dev_writefile_flag:
            html_content = page.content()
            print(len(html_content))
            with open("_output.html", "w") as file:
                file.write(html_content)
    browser.close()
# with open("cards.json", "w", encoding="utf-8") as file:
#     json.dump(out, file, ensure_ascii=False, indent=4)
processing_time = time.time() - start_time
print(f'処理時間(s）: {round(processing_time,1)}')
