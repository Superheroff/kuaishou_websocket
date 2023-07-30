# https://live.kuaishou.com/live_api/liveroom/websocketinfo?liveStreamId=2SNt9-_ZuKQ
# https://livev.m.chenzhongtech.com/wap/live/feed?liveStreamId=2SNt9-_ZuKQ

from playwright.sync_api import sync_playwright
import threading
import os
import time
import json
from google.protobuf.json_format import MessageToDict
from configparser import ConfigParser
import kuaishou_pb2


class kslive(object):
    def __init__(self):
        self.path = os.path.abspath('')
        self.chrome_path = r"\firefox-1419\firefox\firefox.exe"
        self.ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
        self.uri = 'https://live.kuaishou.com/u/'
        self.context = None
        self.browser = None
        self.page = None
        self.file_path = os.path.join(self.path, "config.ini")
        if os.path.exists(self.file_path):
            self.conn = ConfigParser()
            self.conn.read(self.file_path)

            if not self.conn.has_option('set', 'thread'):
                self.conn.set('set', 'thread', '2')
            if not self.conn.has_option('set', 'live_ids'):
                self.conn.set('set', 'live_ids', '')
            if not self.conn.has_option('set', 'phone'):
                self.conn.set('set', 'phone', '')

            self.conn.write(open(self.file_path, "w"))
            self.live_ids = self.conn.get('set', 'live_ids')
            self.thread = self.conn.getint('set', 'thread')
            self.phone = self.conn.get('set', 'phone')

    def find_file(self, find_path, file_type) -> list:
        """
        寻找文件
        :param find_path: 子路径
        :param file_type: 文件类型
        :return:
        """
        path = self.path + "\\" + find_path
        data_list = []
        for root, dirs, files in os.walk(path):
            if root != path:
                break
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.find(file_type) != -1:
                    data_list.append(file_path)
        return data_list

    def main(self, lid, semaphore):
        with semaphore:
            thread_name = threading.current_thread().name.split("-")[0]
            with sync_playwright() as p:
                self.browser = p.firefox.launch(headless=False)
                # executable_path=self.path + self.chrome_path
                cookie_list = self.find_file("cookie", "json")
                self.context = self.browser.new_context(storage_state=cookie_list[0], user_agent=self.ua)
                self.page = self.context.new_page()
                self.page.add_init_script("Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});")
                self.page.goto("https://live.kuaishou.com/")
                element = self.page.get_attribute('.no-login', "style")
                if not element:
                    self.page.locator('.login').click()
                    self.page.locator('li.tab-panel:nth-child(2) > h4:nth-child(1)').click()
                    self.page.locator(
                        'div.normal-login-item:nth-child(1) > div:nth-child(1) > input:nth-child(1)').fill(
                        self.phone)
                try:
                    self.page.wait_for_selector("#app > section > div.header-placeholder > header > div.header-main > "
                                                "div.right-part > div.user-info > div.tooltip-trigger > span",
                                                timeout=1000 * 60 * 2)
                    if not os.path.exists(self.path + "\\cookie"):
                        os.makedirs(self.path + "\\cookie")
                    self.context.storage_state(path=self.path + "\\cookie\\" + self.phone + ".json")
                    # 检测是否开播
                    selector = "html body div#app div.live-room div.detail div.player " \
                               "div.kwai-player.kwai-player-container.kwai-player-rotation-0 " \
                               "div.kwai-player-container-video div.kwai-player-plugins div.center-state div.state " \
                               "div.no-live-detail div.desc p.tip"  # 检测正在直播时下播的选择器
                    try:
                        msg = self.page.locator(selector).text_content(timeout=3000)
                        print("当前%s" % thread_name + "，" + msg)
                        self.context.close()
                        self.browser.close()

                    except Exception as e:
                        print("当前%s，[%s]正在直播" % (thread_name, lid))
                        self.page.goto(self.uri + lid)
                        self.page.on("websocket", self.web_sockets)
                        self.page.wait_for_selector(selector, timeout=86400000)
                        print("当前%s，[%s]的直播结束了" % (thread_name, lid))
                        self.context.close()
                        self.browser.close()

                except Exception:
                    print("登录失败")
                    self.context.close()
                    self.browser.close()

    def web_sockets(self, web_socket):
        urls = web_socket.url
        print(urls)
        if '/websocket' in urls:
            web_socket.on("close", self.websocket_close)
            web_socket.on("framereceived", self.handler)

    def websocket_close(self):
        self.context.close()
        self.browser.close()

    def handler(self, websocket):
        Message = kuaishou_pb2.SocketMessage()
        Message.ParseFromString(websocket)
        if Message.payloadType == 310:
            SCWebFeedPUsh = kuaishou_pb2.SCWebFeedPush()
            SCWebFeedPUsh.ParseFromString(Message.payload)
            obj = MessageToDict(SCWebFeedPUsh, preserving_proto_field_name=True)

            if obj.get('commentFeeds', ''):
                msg_list = obj.get('commentFeeds', '')
                for i in msg_list:
                    userName = i['user']['userName']
                    pid = i['user']['principalId']
                    content = i['content']
                    print("%s  -->  %s  -->  %s" % (userName, pid, content))
            if obj.get('giftFeeds', ''):
                msg_list = obj.get('giftFeeds', '')
                for i in msg_list:
                    userName = i['user']['userName']
                    pid = i['user']['principalId']
                    print("%s  -->  %s" % (userName, pid))
            if obj.get('likeFeeds', ''):
                msg_list = obj.get('likeFeeds', '')
                for i in msg_list:
                    userName = i['user']['userName']
                    pid = i['user']['principalId']
                    print("%s -->  %s" % (userName, pid))


class run(kslive):
    def __init__(self):
        super().__init__()
        self.ids_list = self.live_ids.split(",")

    def run_live(self):
        """
        主程序入口
        :return:
        """
        t_list = []
        # 允许的最大线程数
        if self.thread < 1:
            self.thread = 1
        elif self.thread > 8:
            self.thread = 8
            print("线程最大允许8，线程数最好设置cpu核心数")

        semaphore = threading.Semaphore(self.thread)
        # 用于记录数量
        n = 0
        if not self.live_ids:
            print("请导入网页直播id，多个以','间隔")
            return

        for i in self.ids_list:
            n += 1
            t = threading.Thread(target=kslive().main, args=(i, semaphore), name=f"线程：{n}-{i}")
            t.start()
            t_list.append(t)
        for i in t_list:
            i.join()


run().run_live()
