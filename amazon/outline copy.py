from playwright.sync_api import sync_playwright
import time
import json
target_url = "https://www.amazon.co.jp/s?k=%E3%83%91%E3%82%BD%E3%82%B3%E3%83%B3&__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&crid=FEA5GHQFBMH9&sprefix=%E3%83%91%E3%82%BD%E3%82%B3%E3%83%B3%2Caps%2C246&ref=nb_sb_noss_1"  # 760

prefix_url = "https://www.youtube.com"
repalce_url = "/watch?v="
max_number = 100
dev_writefile_flag = True
out = {"channel_info": [
    target_url, prefix_url
], "videos": []}


def handle_response():
    gridCards = page.query_selector_all(
        '#dismissible.style-scope.ytd-rich-grid-media')

    for index, card in enumerate(gridCards):
        workArea = {'id': index+1}

        title_element = card.query_selector('#video-title')
        title_text = title_element.inner_text()
        workArea['title'] = title_text

        link_element = card.query_selector('#video-title-link')
        workArea['video_url'] = link_element.get_attribute("href")
        workArea['video_id'] = workArea['video_url'].replace("/watch?v=", "")

        meta_element = card.query_selector('#metadata-line')
        views_date_elements = meta_element.query_selector_all("span")
        workArea['views'] = views_date_elements[0].inner_text()
        workArea['release_date'] = views_date_elements[1].inner_text()

        img_element = card.query_selector('yt-image > img')
        image_url = img_element.get_attribute("src")
        if image_url == None:
            print(f"{index+1}番目のサムネイル画像が読み込まれていません。画面スクロールのタイミングを改善して下さい。")
        workArea['thumbnail_url'] = image_url

        time_element = card.query_selector('#time-status')
        workArea['duration'] = time_element.inner_text()
        out['videos'].append(workArea)
        if index+1 >= max_number:
            break

start_time = time.time()
with sync_playwright() as p:
    browser = p.chromium.launch()
    global page  # グローバル変数を使うことを宣言


    page = browser.new_page()

    page.goto(target_url)  # ここに対象のURLを入力してください

    i = 0
    pre_count = 0
    after_count = 0
    while True:
        pre_count = after_count
        i += 1
        print(f'{i}回目スクロール')
        
        page.press('body', 'End')
        time.sleep(1)
        page.keyboard.press('PageDown')
        time.sleep(1)
        
        page.wait_for_load_state() 
        work_gridCards = page.query_selector_all(
            '#dismissible.style-scope.ytd-rich-grid-media')
        after_count = len(work_gridCards)
        print(f'表示動画数: {after_count}')

        if after_count >= max_number : 
            page.press('body', 'End')
            time.sleep(1)
            page.keyboard.press('PageDown')
            time.sleep(1)
            print(f'max_number:{max_number} に達しました。処理を終了します。')
            break
        if pre_count == after_count:break
        
    print(f'最終表示動画数: {after_count}')
    # handle_response()
    if dev_writefile_flag:
        html_content = page.content()
        with open("output.html", "w") as file:
            file.write(html_content)
        browser.close()


with open("data.json", "w", encoding="utf-8") as file:
    json.dump(out, file, ensure_ascii=False, indent=4)
print(f'動画数: {len(out["videos"])}')
processing_time = time.time() - start_time
print(f'処理時間(s）: {round(processing_time,1)}')
