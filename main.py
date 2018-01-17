# -*- coding:utf8 -*-
from utils import baidu_url, rail_top, cs_mac_rail_top
from utils import screen_cut, get_text_line, get_questions, deal_questions, get_answer, open_webboswer


class StupidAnswer(object):

    def __init__(self):
        self.rail = rail_top
        self.project = 0
        self.url = baidu_url
        self.open_type = 0
        self.source = 0

    def top_meet(self, rail, source, url, open_type):
        screen_cut(rail)
        text_line = get_text_line()
        print(text_line)
        if not text_line:
            print("未发现题目")
            return
        questions = get_questions(text_line)
        questions = deal_questions(questions, source=source)
        get_answer(questions, url=url)
        open_webboswer(questions[0], open_type=open_type)

    # 百万超人
    def billon_super_man(self, rail, source, url, open_type):
        screen_cut(cs_mac_rail_top)
        text_line = get_text_line()
        print(text_line)
        if not text_line:
            print("未发现题目")
            return
        questions = get_questions(text_line)
        questions = deal_questions(questions, source=source)
        get_answer(questions, url=url)
        open_webboswer(questions[0], open_type=open_type)

    # 主要含函数
    def run(self, rail=None, source=None, url=None, open_type=None):
        if rail is None:
            rail = self.rail
        if source is None:
            source = self.source
        if url is None:
            url = self.url
        if open_type is None:
            open_type = self.open_type

        if source == 0:
            self.top_meet(rail, source, url, open_type)
        elif source == 1:
            self.billon_super_man(rail, source, url, open_type)


if __name__ == "__main__":
    answer = StupidAnswer()
    answer.run()
