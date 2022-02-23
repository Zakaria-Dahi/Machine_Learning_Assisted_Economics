import json


if __name__ == '__main__':

    json_file = open('series.json', encoding='utf-8')
    data = json.load(json_file)
    json_file.close()
    with open("URL_analysis2_reduced.txt", encoding='utf-8') as new_data:
        Lines = new_data.readlines()
        code = 0
        for l in Lines:
            try:
                code = int(l)
                continue
            except:
                data.append({"text": l.strip(), "code": code, "name": l.strip()})
    with open('series.json', 'w',  encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=False)