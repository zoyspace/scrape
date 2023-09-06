from detail import YouTubeScraperDetail
import json

max_number = 50

out_detail_list = []
out_error_videoid = []
out_filename = "details.json"


def append_to_file_json(filename, dicdata):
    with open(filename, mode='a', encoding="utf-8") as file:
        file.write(json.dumps(dicdata, ensure_ascii=False, indent=4))
def append_to_file(filename,data):
    with open(filename, mode='a', encoding="utf-8") as file:
        file.write( data)


# basic コード
# video_id = "moyoZaL2YtQ"
# scraper = YouTubeScraperDetail(video_id)
# scraper.scrape()
# josnファイルからvideo_idを取得
# with open("data_re.json", "r", encoding="utf-8") as file:
with open("data.json", "r", encoding="utf-8") as file:
    videos_id_list = json.load(file)
    length_videos_id_list = len(videos_id_list["videos"])
    print(f'video数: {length_videos_id_list}')
    with open(out_filename, "w", encoding="utf-8") as file:
        file.write('[\n')
    for index, videos in enumerate(videos_id_list["videos"]):
        print('----------------------------------')
        print(f'index:{index} 処理開始')
        video_id = videos["video_id"]
        scraper = YouTubeScraperDetail(index, video_id)
        response_detail, res_error_flag = scraper.scrape()
        out_detail_list.append(response_detail)
        append_to_file_json(out_filename, response_detail)
        if res_error_flag:
            out_error_videoid.append(video_id)
        if index+1 >= max_number:
            print(f'max_number:{max_number} に達しました。処理を終了します。')
            break
        if index+1 != length_videos_id_list:
            append_to_file(out_filename,',\n')

# print(f'out_detail_list: {out_detail_list}')
print(f'out_detail_list: {len(out_detail_list)}コ取得しました。')
print(f'out_error_videoid: {out_error_videoid}')
# with open("details_re.json", "w", encoding="utf-8") as file:
append_to_file(out_filename, '\n]')


# with open("details.json", "w", encoding="utf-8") as file:
#     json.dump(out_detail_list, file, ensure_ascii=False, indent=4)


# async def main():
#     data = "This is some sample data to be written to the file."
#     await write_to_file('sample.txt', data)
#     print(f"Data written to sample.txt")
