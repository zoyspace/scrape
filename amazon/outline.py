from playwright.sync_api import sync_playwright
import time, datetime
import json
from urllib.parse import unquote

# target_url = 'https://www.amazon.co.jp/s?k=iphone%E3%82%B1%E3%83%BC%E3%82%B9&__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&crid=WZP8S0OOZKXK&sprefix=iphone%E3%82%B1%E3%83%BC%E3%82%B9%2Caps%2C171&ref=nb_sb_noss_1'
amazon_url = 'https://www.amazon.co.jp'

search_keyword = 'パソコン'

dev_writefile_flag = True
next_page_flag = True
max_page = 2
out = {}


def fully_decode(str_uri):
    prev_uri = ''
    while str_uri != prev_uri:
        prev_uri = str_uri
        str_uri = unquote(str_uri)
    return str_uri

dt_now = datetime.datetime.now()
start_time = time.time()
with sync_playwright() as p:
    # browser = p.chromium.launch(headless=False)
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(amazon_url)
    page.wait_for_load_state()
    page.fill('input#twotabsearchtextbox', search_keyword)
    page.press('input#twotabsearchtextbox', 'Enter')
    page.wait_for_load_state()
    target_url = page.url
    print(f'current_url: {target_url}')
    out['keyWord'] = search_keyword
    out['startDate'] = dt_now.strftime('%Y年%m月%d日 %H:%M:%S')
    out['targetUrls'] = []
    out['sectionCards'] = []
    loop_num = 0
    while next_page_flag:
        out['targetUrls'].append(target_url)
        page.goto(target_url)
        # page.press('body', 'End')
        page.keyboard.press('PageDown')
        time.sleep(3)
        page.wait_for_load_state()
        hit_count_element = page.query_selector(
            '.a-section.a-spacing-small.a-spacing-top-small').inner_text()
        print(hit_count_element)
        sectionCards = page.query_selector_all('.a-section.a-spacing-base')
        for index, card in enumerate(sectionCards):
            loop_num += 1
            indexPlus1 = index+1
            idd = f'{str(loop_num)}_{len(out["targetUrls"])}_{str(indexPlus1)}'
            # print(indexPlus1)
            temp_card = {'id': idd, 'imageUrl': '', 'sponsored': False, 'title': '', 'stars': '', 'ratingsCount': '',
                         'salesText': '', 'price': '', 'pre_price': '', 'coupon_text': '', 'prime': False, 'url': ''}
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
                temp_card['stars'] = aria_label_elements[0].get_attribute(
                    'aria-label')
                temp_card['ratingsCount'] = aria_label_elements[1].get_attribute(
                    'aria-label')
            else:
                print('評価なし')
            # sales
            sales_element = card.query_selector(
                '[data-a-badge-color="sx-lightning-deal-red"].a-badge-label > .a-badge-label-inner.a-text-ellipsis')
            if sales_element:
                sales_text = sales_element.inner_text()
                temp_card['salesText'] = sales_text
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
            
                temp_card['coupon_text'] = coupon_text
            # prime
            prime_element = card.query_selector(
                '[role="img"][aria-label="Amazon プライム"]')
            if prime_element:
                temp_card['prime'] = True
            # url
            url_element = card.query_selector(
                'a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
            if url_element:
                url_txt = url_element.get_attribute('href')
                if url_txt:
                    if 'url=' in url_txt:
                        split_str = url_txt.split('url=')[1]
                    else:
                        split_str = url_txt
                    decoded_string = fully_decode(split_str)
                    temp_card['url'] = amazon_url + decoded_string

            out['sectionCards'].append(temp_card)
        print(f'商品カード数: {len(sectionCards)}')

        # ページネーション
        pagination_element = page.query_selector('span.s-pagination-strip')
        # 現在のページ
        current_page_element = pagination_element.query_selector(
            '.s-pagination-selected')
        current_page = current_page_element.inner_text()
        print(f'current_page_number: {current_page}')
        # 次ページ
        next_page_element = pagination_element.query_selector(
            '.s-pagination-item.s-pagination-next')
        if next_page_element.get_attribute('href'):
            target_url = amazon_url + \
                next_page_element.get_attribute('href')
            next_page_flag = True
        else:
            target_url = ''
            next_page_flag = False
        print(f'nextPage: {target_url}')
        if dev_writefile_flag:
            html_content = page.content()
            print(len(html_content))
            with open("_output.html", "w") as file:
                file.write(html_content)
        if int(current_page) >= max_page:
            next_page_flag = False
            print(f'max_page:{max_page} に達しました。処理を終了します。')
            break
    browser.close()
with open("cards.json", "w", encoding="utf-8") as file:
    json.dump(out, file, ensure_ascii=False, indent=4)
processing_time = time.time() - start_time
print(f'処理時間(s）: {round(processing_time,1)}')
