from playwright.sync_api import sync_playwright
import time
import json
# target_url = "https://www.amazon.co.jp/s?k=%E3%83%91%E3%82%BD%E3%82%B3%E3%83%B3%E3%83%87%E3%82%B9%E3%82%AF&crid=1J3LGN400GBUT&sprefix=%E3%83%91%E3%82%BD%E3%82%B3%E3%83%B3%2Caps%2C205&ref=nb_sb_ss_ts-doa-p_1_4"
# target_url = "https://www.amazon.co.jp/s?k=%E3%82%B2%E3%83%BC%E3%83%9F%E3%83%B3%E3%82%B0%E3%83%81%E3%82%A7%E3%82%A2&i=kitchen&crid=153E7KC2NS5XJ&sprefix=g%2Ckitchen%2C161&ref=nb_sb_ss_ts-doa-p_1_1"
target_url = "https://www.amazon.co.jp/s?k=%E3%83%9F%E3%83%8B%E3%83%91%E3%82%BD%E3%82%B3%E3%83%B3&crid=2O01P0LNAHWA0&sprefix=%E3%81%BF%E3%81%AB%2Caps%2C170&ref=nb_sb_ss_ts-doa-p_2_2"

dev_writefile_flag = True
out = {}

start_time = time.time()
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    # browser = p.chromium.launch()
    global page  # グローバル変数を使うことを宣言
    page = browser.new_page()
    page.goto(target_url)  # ここに対象のURLを入力してください

    # page.press('body', 'End')
    page.keyboard.press('PageDown')
    time.sleep(13)

    page.wait_for_load_state()
    sectionCards = page.query_selector_all('.a-section.a-spacing-base')

    out['sectionCards'] = []
    for index, card in enumerate(sectionCards):
        print(index+1)
        temp_card = {'id': index+1,'recommended':False ,'imageUrl': '','sponsored': False,'title': '','stars': '', 'ratingsCount': '',
                      'sales':'','price': '', 'pre_price': ''}
        # recommended
        recommended_element = card.query_selector('[data-a-badge-color="sx-gulfstream"].a-badge-label > .a-badge-label-inner.a-text-ellipsis')    
        if recommended_element:
            recommended_text = recommended_element.inner_text()
            print(recommended_text)
            if recommended_text == 'Amazonおすすめ':
                temp_card['recommended'] = True

        # imageUrl
        image_element = card.query_selector('img.s-image')
        if image_element:
            temp_card['imageUrl'] = image_element.get_attribute('src')

        # sponsored
        sponsored_element = card.query_selector('.puis-label-popover-default > .a-color-secondary')
        if sponsored_element:
            sponsored_text = sponsored_element.inner_text()
            if sponsored_text == 'スポンサー':
                temp_card['sponsored'] = True
        
        # title
        title_element = card.query_selector(
            '.a-size-base-plus.a-color-base.a-text-normal')
        if title_element:
            title = title_element.inner_text()
            temp_card['title'] = title
        # stars
        # stars_element = card.query_selector('.a-size-base[class^="puis-"][class$="-text"]') # 先頭、末尾の文字列で検索
        stars_element = card.query_selector('.a-icon-alt') 
        if stars_element:            
            temp_card['stars'] = stars_element.inner_text()

        # ratingsCount
        ratingsCount_element = card.query_selector('.a-size-base.s-underline-text')
        if ratingsCount_element:
            ratingsCount_text = ratingsCount_element.inner_text()
            temp_card['ratingsCount'] = ratingsCount_text
        # timesale
        timesale_element = card.query_selector('[data-a-badge-color="sx-lightning-deal-red"].a-badge-label > .a-badge-label-inner.a-text-ellipsis')
        if timesale_element:
            timesale_text = timesale_element.inner_text()
            temp_card['sales'] = timesale_text
        # if index == 3:
        #     print(card.inner_text())
        out['sectionCards'].append(temp_card)

    print(f'商品カード数: {len(sectionCards)}')
    print(f'タイトル数: {len(out["sectionCards"])}')
    if dev_writefile_flag:

        html_content = page.content()
        print(len(html_content))
        with open("output.html", "w") as file:
            file.write(html_content)
        with open("cards.json", "w", encoding="utf-8") as file:
            json.dump(out, file, ensure_ascii=False, indent=4)

        # with open('titles.csv', 'w', newline='', encoding='utf-8-sig') as f:
        #     writer = csv.writer(f)
        #     for row in titles:
        #         writer.writerow(row)

    browser.close()


processing_time = time.time() - start_time
print(f'処理時間(s）: {round(processing_time,1)}')
