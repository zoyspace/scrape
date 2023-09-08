import json
import csv

# JSONデータを読み込む
with open('cards.json', 'r') as f:
    json_data = json.load(f)

# JSONデータを表示

# CSVファイルに書き込む
with open('cards.csv', 'w', newline='') as f:
    csv_writer = csv.writer(f)

    # ヘッダーを書き込む
    header = json_data['sectionCards'][0].keys()
    csv_writer.writerow(header)

    # 各行のデータを書き込む
    for row in json_data['sectionCards']:
        csv_writer.writerow(row.values())
print('処理が完了しました。')
