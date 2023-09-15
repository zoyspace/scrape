from playwright.sync_api import sync_playwright
import time, json,os,re
from tqdm import tqdm
from datetime import datetime
from settings import (
    DOMAIN_URL,
    PREFECTURES,
    DETAIL_DEV_FLAG,
    DETAIL_BATCH_SIZE,
    DETAILS_DIR,
    LISTS_DIR
)
RESULT_DIR = DETAILS_DIR
INPUT_DIR = LISTS_DIR

def input_salon_lists():
    file_names = os.listdir(INPUT_DIR)
    if len(file_names) == 0:
        print('店舗一覧ファイルがありません')
        exit()
    sorted_file_names = sorted(file_names)
    salon_lists = []
    for file_name in sorted_file_names:
        with open(f'{INPUT_DIR}/{file_name}', 'r', encoding='utf-8') as f:
            salon_list = json.load(f)
        salon_lists.extend(salon_list)
    
    return salon_lists

def get_last_id():
    if not os.path.exists(RESULT_DIR):
        os.mkdir(RESULT_DIR)
    file_names = os.listdir(RESULT_DIR)
    if len(file_names) == 0:
        return 0,0
    sorted_file_names = sorted(file_names)
    last_file_name = sorted_file_names[-1]
    print(f'最後のファイル名: {last_file_name}')
    match_num = re.search(r"\d+", last_file_name) # 文字列から数値を抽出
    outfile_num = int(match_num.group(0)) # 数値に変換
    with open(f'{RESULT_DIR}/{last_file_name}', 'r', encoding='utf-8') as f:
        last_json_detail = json.load(f)
    last_salon_detail = last_json_detail[-1]
    last_salon_id = last_salon_detail['id']
    return outfile_num,last_salon_id

def extract_detail_from_page(page,salon_detail):
    name_element = page.query_selector('.sprtHeaderInner')
    salon_detail['店舗名'] = name_element.query_selector(
        '.detailTitle').inner_text()
    salon_detail['店舗名かな'] = name_element.query_selector('p.fs10').inner_text()
    salon_detail['パンくず'] = page.query_selector('.pankuzu').inner_text()
    slide_image_element = page.query_selector_all('.slnHeaderSliderPoint li')
    salon_detail['トップ画像数'] = len(slide_image_element)
    salon_detail['キャッチコピー'] = page.query_selector('.shopCatchCopy').inner_text()

    rows = page.query_selector_all("table.slnDataTbl tr")
    for row in rows:
        th_elements = row.query_selector_all("th")
        td_elements = row.query_selector_all("td")

        if th_elements and td_elements:
            for th, td in zip(th_elements, td_elements):
                th_text = th.inner_text()
                td_text = td.inner_text()
                salon_detail[th_text] = td_text
    return salon_detail

def convert_tel_url(url):
    last_slash_index = url.rfind('/')
    return url[:last_slash_index+1] + 'tel'

def get_tel(page):
    tel_element = page.query_selector(
        '#mainContents > table > tbody > tr > td')
    if tel_element:
        tel_text = tel_element.inner_text().rstrip()
    else:
        tel_text = 'なし'
    return tel_text

def save_salon_detail(salon_details, outfile_num):
    outfile_num += 1
    outfile_name = f'{RESULT_DIR}/details_{str(outfile_num).zfill(6)}.json' 
    with open(outfile_name, "w") as file:
        json.dump(salon_details, file, ensure_ascii=False, indent=4)
    print(f'{outfile_name}に保存しました')
    return outfile_num

def main():
    try:
        salon_lists = input_salon_lists()
        salon_id = 0
    
        with sync_playwright() as p:
            browser = p.chromium.launch()
            # browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            salon_details = []
            outfile_num,resume_num = get_last_id()
            print(f'開始ID: {resume_num+1}')

            for salon in tqdm(salon_lists):
                    salon_id += 1
                    if salon_id <= resume_num :
                        continue # スキップ
                    salon_detail = {}
                    prefecture = salon['prefecture']
                    target_url = salon['url']
                    page.goto(target_url)
                    page.wait_for_load_state()
                    current_datetime = datetime.now()

                    salon_detail['id'] = salon_id
                    salon_detail['list_id'] = salon['id']
                    salon_detail['データ取得日時'] = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                    salon_detail['都道府県'] = prefecture
                    salon_detail['サロンのurl'] = target_url
                    # 関数
                    salon_detail = extract_detail_from_page(page,salon_detail)
                    target_url_tel = convert_tel_url(target_url)
                    page.goto(target_url_tel)
                    page.wait_for_load_state()
                    salon_detail['電話番号'] = get_tel(page)
                    salon_details.append(salon_detail)

                    # print(f'{salon["id"]}店舗目を取得中')
                    if (salon_id) % DETAIL_BATCH_SIZE == 0:
                        outfile_num = save_salon_detail(salon_details, outfile_num)

                        print(f'{salon_id}店舗まで取得')
                        salon_details = []
                    # if outfile_num == 3 :break
                # if index2 == 2 and DETAIL_DEV_FLAG:break
                # if index1 == 2 and DETAIL_DEV_FLAG:break
            if len(salon_details) > 0:
                outfile_num = save_salon_detail(salon_details, outfile_num)
            if DETAIL_DEV_FLAG:
                html_content = page.content()
                with open("_output.html", "w") as file:
                    file.write(html_content)

            browser.close()
        print(f'{salon_id}店舗まで取得完了')
    except KeyboardInterrupt:  # 追加: Ctrl+Cが押された場合の処理
        print("Ctrl+Cが押されました。プログラムを終了します。")
        exit(0)


if __name__ == "__main__":
    start_time = time.time()
    main()
    processing_time = time.time() - start_time
    print(f'処理時間(s）: {round(processing_time,1)}')
