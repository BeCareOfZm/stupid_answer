import configparser
from aip import AipOcr
import os, re
import requests, webbrowser
import getopt
try:
    import win32api
    import win32con
    import win32gui
    import win32ui
except:
    pass

try:
    import Image
except ImportError:
    from PIL import Image

NUM_RE = r"^\d+"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"}

# 获取配置信息
conf = configparser.ConfigParser()
conf.read("./settings.conf")

APPID = conf.get("ocr", "app_id")
APIKEY = conf.get("ocr", "api_key")
SECRETKEY = conf.get("ocr", "secret_key")
rail_top = conf.get("rail", "rail_top")
cs_mac_rail_top = conf.get("rail", "cs_mac_rail_top")
rail_billon = conf.get("rail", "rail_billon")

google_url = conf.get("search_url", "google_url")
baidu_url = conf.get("search_url", "baidu_url")

# 设置百度ai客户端
client = AipOcr(APPID, APIKEY, SECRETKEY)


# 读取图片二进制文件
def get_file_content(file_path):
    with open(file_path, 'rb') as fp:
        return fp.read()


# mac按比例截图
def screen_cut(rail, screen_type=1):
    if screen_type:
        command = "screencapture -R {} test.png".format(rail)
        os.system(command)
    else:
        try:
            screen_index = 0
            hwnd_d_c = win32gui.GetWindowDC(screen_index)
            mfc_d_c = win32ui.CreateDCFromHandle(hwnd_d_c)
            save_d_c = mfc_d_c.CreateCompatibleDC()
            save_bit_map = win32ui.CreateBitmap()
            MoniterDev = win32api.EnumDisplayMonitors(None, None)

            # 我针对自己手机的屏幕大小以及显示题目的位置重新对其设置
            w = 370
            h = 210
            save_bit_map.CreateCompatibleBitmap(mfc_d_c, w, h)
            save_d_c.SelectObject(save_bit_map)
            # here的正下方（20，140）是截图的起点坐标来定位截图位置，这些根据个人情况调整
            save_d_c.BitBlt((0, 0), (w, h), mfc_d_c, (40, 140), win32con.SRCCOPY)

            save_bit_map.SaveBitmapFile(save_d_c, 'test.png')
        except:
            print("mac系统无法支持win32")


# 获取文本列表去除不必要的东西
def get_text_line():
    image = get_file_content("test.png")
    res = client.basicGeneral(image)
    text_line = []
    for word in res.get("words_result"):
        strs = word.get("words")
        text_line.append(strs)
    return text_line


# 生成问题列表
def get_questions(text_line):
    questions = []
    if len(text_line) > 4:
        questions.append(''.join(text_line[:2]))
        text_line = text_line[2:]
    else:
        questions.append(text_line[0])
        text_line = text_line[1:]

    for text in text_line:
        questions.append(text)
    if len(questions) == 2:
        q = questions[1]
        questions.extend(list(q))
    return questions


# 百万富翁去掉选项的题号
def billon_superman_text(strs):
    if "A." == strs[:2].upper():
        strs = strs.lstrip("A.")
    elif "B." == strs[:2].upper():
        strs = strs.lstrip("B.")
    elif "C." == strs[:2].upper():
        strs = strs.lstrip("C.")
    return strs


# 删除题号
def del_question_id(strs):
    res = re.match(NUM_RE, strs)
    if res:
        length = len(res.group())
        if length > 2:
            return strs
        if len(strs) > length and strs[length] == '.':
            strs = strs[length+1:]
        else:
            strs = strs[length:]
    return strs


# 处理不必要的文本
def deal_questions(questions, source=0):
    """
    source: 0: 冲顶大会 1: 百万英雄
    """
    questions_list = []
    for i, q in enumerate(questions):
        strs = q.replace(" ", "")
        strs = strs.replace("\n", "")
        if i == 0:
            strs = del_question_id(strs)
        if source == 1:
            strs = billon_superman_text(strs)
        if "《" in strs:
                deal_strs = strs.replace("《", "")
                deal_strs = deal_strs.replace("》", "")
                questions_list.append(deal_strs)
        questions_list.append(strs)
    return questions_list


def deep_search(q, text):
    print("答案: {}".format(q))
    if len(q) == 2:
        for t in q:
            print("答案:{} --> {}个".format(t, text.count(t)))
    if len(q) > 2:
        if '的' in q:
            qs = q.split("的")
            for t in qs:
                print("答案:{} --> {}个".format(t, text.count(t)))
        if '·' in q:
            qs = q.split("·")
            for t in qs:
                print("答案:{} --> {}个".format(t, text.count(t)))


# 获取答案列表
def get_answer(questions, url=baidu_url):
    res = requests.get(url=url.format(questions[0]), headers=HEADERS)
    print(questions)
    status = 0
    for q in questions[1:]:
        num = res.text.count(q)
        print("答案:{} --> {}个".format(q, num))
        if num:
            status = 1
    if not status:
        for q in questions[1:]:
            deep_search(q, res.text)


# 打开url
def open_webboswer(question, open_type=0):
    url = baidu_url.format(question)
    if open_type:
        webbrowser.open(url)
    else:
        os.system("open {}".format(url))


