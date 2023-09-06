from playwright.sync_api import sync_playwright
import time
import json
# target_url = "https://www.amazon.co.jp/s?k=%E3%83%91%E3%82%BD%E3%82%B3%E3%83%B3%E3%83%87%E3%82%B9%E3%82%AF&crid=1J3LGN400GBUT&sprefix=%E3%83%91%E3%82%BD%E3%82%B3%E3%83%B3%2Caps%2C205&ref=nb_sb_ss_ts-doa-p_1_4"
# target_url = "https://www.amazon.co.jp/s?k=%E3%82%B2%E3%83%BC%E3%83%9F%E3%83%B3%E3%82%B0%E3%83%81%E3%82%A7%E3%82%A2&i=kitchen&crid=153E7KC2NS5XJ&sprefix=g%2Ckitchen%2C161&ref=nb_sb_ss_ts-doa-p_1_1"
target_url = "https://www.amazon.co.jp/s?k=%E3%83%9F%E3%83%8B%E3%83%91%E3%82%BD%E3%82%B3%E3%83%B3&crid=2O01P0LNAHWA0&sprefix=%E3%81%BF%E3%81%AB%2Caps%2C170&ref=nb_sb_ss_ts-doa-p_2_2"

dev_writefile_flag = True

start_time = time.time()
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    # browser = p.chromium.launch()
    global page  # グローバル変数を使うことを宣言
    page = browser.new_page()
    page.goto(target_url)  # ここに対象のURLを入力してください
    
    page.press('body', 'End')
    page.keyboard.press('PageDown')
    time.sleep(1)
    

    page.wait_for_load_state() 
    sectionCards = page.query_selector_all('.a-section.a-spacing-base')
    titles = []
    for index,card in enumerate(sectionCards):
        title_element = card.query_selector('.a-size-base-plus.a-color-base.a-text-normal')
        if title_element :
            title = title_element.inner_text()
            titles.append(title)
        if index == 3:
            print(card.inner_text())
        

    print(f'商品カード数: {len(sectionCards)}')
    print(f'タイトル数: {len(titles)}')
    if dev_writefile_flag:

        html_content = page.content()
        print(len(html_content))
        with open("output.html", "w") as file:
            file.write(html_content)
        with open("titles.json", "w", encoding="utf-8") as file:
            json.dump(titles, file, ensure_ascii=False, indent=4)

        # with open('titles.csv', 'w', newline='', encoding='utf-8-sig') as f:
        #     writer = csv.writer(f)
        #     for row in titles:
        #         writer.writerow(row)

    browser.close()


processing_time = time.time() - start_time
print(f'処理時間(s）: {round(processing_time,1)}')
