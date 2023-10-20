import os,json,time
from settings import (
    DOMAIN_URL,
    PREFECTURES,
    DETAIL_DEV_FLAG,
    DETAIL_BATCH_SIZE,
    DETAILS_DIR,
    LISTS_DIR
)
INPUT_DIR = LISTS_DIR
divide_number = 100

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

def main():
    salon_lists = input_salon_lists()
    salon_lists_len = len(salon_lists)
    print(f'店舗数: {salon_lists_len}')
    salon_lists_divide = [salon_lists[i:i + divide_number] for i in range(0, salon_lists_len, divide_number)]

    for index,d_list in enumerate(salon_lists_divide):
        folder_name = f'./_async/async_n{index}'
        folder_name_salon_lists = f'{folder_name}/salon_lists'
        os.mkdir(folder_name)
        os.mkdir(folder_name_salon_lists)
        with open(f'{folder_name_salon_lists}/lists_n{index}.json', 'w') as file:
                json.dump(d_list, file, ensure_ascii=False, indent=4) 


if __name__ == "__main__":
    start_time = time.time()
    main()
    processing_time = time.time() - start_time
    print(f'処理時間(s）: {round(processing_time,1)}')
