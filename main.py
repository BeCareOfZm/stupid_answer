# -*- coding:utf8 -*-
try:
    import Image
except ImportError:
    from PIL import Image
import os
import requests
import webbrowser
from aip import AipOcr
import configparser


conf = configparser.ConfigParser()
conf.read("./settings.conf")

APP_ID = conf.get("ocr", "app_id")
API_KEY = conf.get("ocr", "api_key")
SECRET_KEY = conf.get("ocr", "secret_key")
rail_top = conf.get("rail", "rail_top")
cs_mac_rail_top = conf.get("rail", "cs_mac_rail_top")

google_url = conf.get("search_url", "google_url")
baidu_url = conf.get("search_url", "baidu_url")
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


# 二进制读取图片文件
def get_file_content(file_path):
    with open(file_path, 'rb') as fp:
        return fp.read()


def mac_screen_cut(rail):
    command = "screencapture -R {} test.png".format(rail)
    os.system(command)


def get_text_line():
    image = get_file_content("test.png")
    res = client.basicGeneral(image)
    text_line = []
    for word in res.get("words_result"):
        strs = word.get("words")
        strs = strs.replace("A", "")
        strs = strs.replace("B", "")
        strs = strs.replace("C", "")
        strs = strs.replace(" ", "")
        strs = strs.replace("\n", "")
        text_line.append(strs)
    return text_line

def main():
    text_line = get_text_line()
    if not text_line:
        return
    questions = []

    if len(text_line) > 4:
        questions.append(''.join(text_line[:2]))
        for text in text_line[2:]:
            if "《" in text:
                strs1 = text.replace("《", "")
                strs1 = strs1.replace("》", "")
                questions.append(strs1)
            questions.append(text)
    else:
        questions.append(text_line[0])
        for text in text_line[1:]:
            if "《" in text:
                strs1 = text.replace("《", "")
                strs1 = strs1.replace("》", "")
                questions.append(strs1)
            questions.append(text)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"}
    res = requests.get(url=baidu_url.format(questions[0]), headers=headers)
    print(questions)
    for q in questions[1:]:
        print(u"答案{}: {}个".format(q, res.text.count(q)))


    url = baidu_url.format(questions[0])

    os.system("open {}".format(url))
if __name__ == "__main__":
    mac_screen_cut(cs_mac_rail_top)
    main()