import json

domain_url = 'https://zexy.net/wedding/'
list_url_part = '/clientList/'
with open('todofuken.json', 'r', encoding='utf-8') as file:
        dic_todofuken = json.load(file)

with open("tyosa.txt", "w") as f:

    for key, value in dic_todofuken.items():   
        target_url = f'{domain_url}{value}{list_url_part}'
        line = f'{key}: {target_url}'

        f.write(f"{line}\n")  # \n は改行を意味します

        