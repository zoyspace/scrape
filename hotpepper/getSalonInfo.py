from playwright.sync_api import sync_playwright
import time
import json
import os
import re
DEV_FLAG = True
result_dir = './temp_salon_datas'

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


def extract_data_from_page(page):
    salon_data = {}
    name_element = page.query_selector('.sprtHeaderInner')
    salon_data['店舗名'] = name_element.query_selector(
        '.detailTitle').inner_text()
    salon_data['店舗名かな'] = name_element.query_selector('p.fs10').inner_text()
    salon_data['パンくず'] = page.query_selector('.pankuzu').inner_text()
    slide_image_element = page.query_selector_all('.slnHeaderSliderPoint li')
    salon_data['トップ画像数'] = len(slide_image_element)
    salon_data['キャッチコピー'] = page.query_selector('.shopCatchCopy').inner_text()

    rows = page.query_selector_all("table.slnDataTbl tr")
    for row in rows:
        th_elements = row.query_selector_all("th")
        td_elements = row.query_selector_all("td")

        if th_elements and td_elements:
            for th, td in zip(th_elements, td_elements):
                th_text = th.inner_text()
                td_text = td.inner_text()
                salon_data[th_text] = td_text
    phone_element = page.query_selector('.slnTel')

    # print(f"{th_text}: {td_text}")

    return salon_data


def convert_tel_url(url):
    last_slash_index = url.rfind('/')
    return url[:last_slash_index+1] + 'tel'


def get_tel(page):
    tel_element = page.query_selector(
        '#mainContents > table > tbody > tr > td')
    tel_text = tel_element.inner_text().rstrip()
    return tel_text


def main():
    with open('urls.json', 'r', encoding='utf-8') as f:
        salon_list = json.load(f)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        salon_datas = []
        salon_id = 0
        outfile_num,resume_num = get_last_id()
        print(f'再開店舗ID: {resume_num}')
        
        for index1, salons in enumerate(salon_list):
            print(f'{salons["prefecture"]}のお店情報を取得開始')

            prefecture = salons['prefecture']
            for index2, salon in enumerate(salons['card_urls']):
                salon_id += 1
                if salon_id <= resume_num:
                    continue # スキップ
                target_url = salon['url']
                page.goto(target_url)
                page.wait_for_load_state()
                # 関数
                salon_data = extract_data_from_page(page)
                salon_data['id'] = salon_id
                salon_data['都道府県'] = prefecture
                salon_data['サロンのurl'] = target_url
                salon_data['list_id'] = salon['id']
                target_url = convert_tel_url(target_url)
                page.goto(target_url)
                page.wait_for_load_state()
                salon_data['電話番号'] = get_tel(page)
                salon_datas.append(salon_data)
                # print(f'{salon["id"]}店舗目を取得中')

                if (salon_id) % 9 == 0:
                    print(f'{salon_id}店舗目を取得中')
                    outfile_num += 1
                    with open(f'{result_dir}/salon_datas_{str(outfile_num)}.json', "w") as file:
                        json.dump(salon_datas, file,
                                  ensure_ascii=False, indent=4)
                    salon_datas = []
                    # if outfile_num == 3 :break
                # if index2 == 2 and DEV_FLAG:break
            # if index1 == 2 and DEV_FLAG:break
        outfile_num += 1
        with open(f'{result_dir}/salon_datas_{str(outfile_num)}.json', "w") as file:
            json.dump(salon_datas, file,ensure_ascii=False, indent=4)
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
