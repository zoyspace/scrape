import os,json
import pandas as pd
import openpyxl
import time
# from settings import (
#    DETAILS_DIR
# )
DETAILS_DIR = 'detail'

def main():
    INPUT_DIR=DETAILS_DIR
    file_names = os.listdir(INPUT_DIR)
    excel_file_name = 'hall_datas.xlsx'
    if len(file_names) == 0:
        print(f'{INPUT_DIR}に店舗ファイルがありません')
        exit()
    sorted_file_names = sorted(file_names)
    json_data = []
    for file_name in sorted_file_names:
        with open(f'{INPUT_DIR}/{file_name}', 'r', encoding='utf-8') as f:
            salon_list = json.load(f)
        json_data.extend(salon_list)
    
    # 辞書型リストをpandas DataFrameに変換
    df = pd.DataFrame(json_data)
    
    # DataFrameをExcelファイルに保存
    df.to_excel(excel_file_name, index=False)
    print(f'{excel_file_name}(Excelファイル)を作成した')


if __name__ == "__main__":
    start_time = time.time()
    main()
    processing_time = time.time() - start_time
    print(f'処理時間(s）: {round(processing_time,1)}')




