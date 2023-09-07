from playwright.sync_api import sync_playwright
import time
import json
# target_url = 'https://www.amazon.co.jp/s?k=iphone%E3%82%B1%E3%83%BC%E3%82%B9&__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&crid=WZP8S0OOZKXK&sprefix=iphone%E3%82%B1%E3%83%BC%E3%82%B9%2Caps%2C171&ref=nb_sb_noss_1'
amazon_url = 'https://www.amazon.co.jp'
search_keyword = 'iphoneケース'

dev_writefile_flag = True
out = {}

start_time = time.time()
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    # browser = p.chromium.launch()
    # global page  # グローバル変数を使うことを宣言
    page = browser.new_page()
    page.goto(amazon_url)  
    page.wait_for_load_state()
    page.fill('input#twotabsearchtextbox', search_keyword)
    page.press('input#twotabsearchtextbox', 'Enter')
    page.wait_for_load_state()
    print(page.url)
    # page.press('body', 'End')
    page.keyboard.press('PageDown')
    time.sleep(3)

    page.wait_for_load_state()
    hit_count_element = page.query_selector('.a-section.a-spacing-small.a-spacing-top-small').inner_text()
    print(hit_count_element)
    sectionCards = page.query_selector_all('.a-section.a-spacing-base')

    out['sectionCards'] = []
    for index, card in enumerate(sectionCards):
        indexPlus1 = index+1
        print(indexPlus1)
        temp_card = {'id': indexPlus1, 'recommended': False, 'imageUrl': '', 'sponsored': False, 'title': '', 'stars': '', 'ratingsCount': '',
                     'sales': '', 'price': '', 'pre_price': '', 'coupon': False, 'coupon_text': '','prime': False}
        # recommended
        recommended_element = card.query_selector(
            '[data-a-badge-color="sx-gulfstream"].a-badge-label > .a-badge-label-inner.a-text-ellipsis')
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
        sponsored_element = card.query_selector(
            '.puis-label-popover-default > .a-color-secondary')
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
        # ratingsCount 
        # 2.8K+となる場合、￥1,450\n￥1,450価格になる場合があるので、属性の値を取得する
        aria_label_elements = card.query_selector_all(
            '.a-row.a-size-small > span[aria-label]')
        if aria_label_elements:
            temp_card['stars'] = aria_label_elements[0].get_attribute('aria-label')
            temp_card['ratingsCount'] = aria_label_elements[1].get_attribute('aria-label')
        else:print('評価なし')
        # sales
        sales_element = card.query_selector(
            '[data-a-badge-color="sx-lightning-deal-red"].a-badge-label > .a-badge-label-inner.a-text-ellipsis')
        if sales_element:
            sales_text = sales_element.inner_text()
            temp_card['sales'] = sales_text
        # price
        price_element = card.query_selector('.a-price-whole')
        if price_element:
            price_text = price_element.inner_text()
            temp_card['price'] = price_text
        # pre_price
        pre_price_element = card.query_selector(
            '.a-price.a-text-price[data-a-strike="true"] > .a-offscreen')
        if pre_price_element:
            pre_price_text = pre_price_element.inner_text()
            temp_card['pre_price'] = pre_price_text
        # coupon
        coupon_element = card.query_selector(
            '.s-coupon-unclipped')
        if coupon_element:
            coupon_text = coupon_element.inner_text()
            temp_card['coupon'] = True
            temp_card['coupon_text'] = coupon_text
        # prime
        prime_element = card.query_selector(
            '[role="img"][aria-label="Amazon プライム"]')
        if prime_element:
            temp_card['prime'] = True
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

        # with open('titles.csv', 'w', newline='', encoding='utf-8-sig') as f:
        #     writer = csv.writer(f)
        #     for row in titles:
        #         writer.writerow(row)

    browser.close()

with open("cards.json", "w", encoding="utf-8") as file:
    json.dump(out, file, ensure_ascii=False, indent=4)

processing_time = time.time() - start_time
print(f'処理時間(s）: {round(processing_time,1)}')
