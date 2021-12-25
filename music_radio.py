# --*--coding：UTF-8 --*--
# 姓名：汪季轩
# 项目名称：
# 开发时间：2021年10月19日01:14:16

from os import getenv, mkdir, makedirs, remove, listdir
from sys import exit, argv
from time import sleep
from subprocess import call
from decimal import Decimal
from shutil import copyfile, rmtree
from requests import post, get
from os import path as pathq
from random import randint
from ast import literal_eval
from threading import Thread

import lxml
from bs4 import BeautifulSoup
from eyed3 import load
from jsonpath import jsonpath
from mutagen import File
from PIL import Image, ImageDraw, ImageFilter
from PyQt5.QtWidgets import QLabel, QListWidgetItem, QLineEdit, QComboBox, QMenu, QAction, QMainWindow, QWidget, \
    QGridLayout, QTabWidget, QListWidget, QPushButton, QProgressBar, QMessageBox, QApplication, QFileDialog, QStatusBar
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, QMutex, QRect, QPoint, Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QCursor
from qtawesome import icon
from pygame import mixer


SongName = []  # 搜集的歌曲名
typerr = ''  # 下载类型 boing正在播放或love我喜欢
list_confident = 'boing'  # 列表状态
num_m = 0  # 窗口控制标志
lrcd = []  # 歌词按行存储
path = ''  # 路径
number = 1  # index
play = 'shun'  # mode
stop = False
num = 0
voice = 0.5  # 音量
pause = False
music = []
urls = []
songs = []
type = 'kugou'  # source  type
name = ''  # input name
downloading = False
page = 5  # 搜索页数
id = []
proxies = {}  # 代理池
songed = []  # 已播歌曲
urled = []  # url
bo = ''  # 播放类型
pic = []  # 图片
picd = []   # 已存图片
qmut = QMutex()  # 线程访问顺序保护
lrcs = []   # 歌词
lrct = []   # 歌词
paing = False  # 爬取index
tryed = 0   # 尝试爬取次数
apdata = getenv("APPDATA")  # 请求环境变量 本机缓存APPDATA/Roaming
data = str(apdata) + '\music'  # 缓存地址
print(data)
to = ''  # 歌曲下载加载路径
time_num = 0  # 进度条数据
start = False
# ”我喜欢“：
loves = []
loveurls = []
lovepics = []
lovelrc = []
namem = ''
SongPath = []
filew = 1  # 文件夹temp变量
num = 0
asas = 1  # 文件夹temp变量
# 图片参数
picno = False
big = False
stopdown = False
# 创建缓存目录 临时文件
try:
    mkdir(data)
except:
    pass


# 进度条线程
class barThread(QThread):
    # 创建信号  控制GUI
    trigger = pyqtSignal(str)

    def __int__(self):
        # 初始化函数
        super(barThread, self).__init__()

    def run(self):
        # 循环更新circle
        circle = 1
        try:
            sleep(1)
            try:
                try:
                    # 进度条存储在time_num
                    global time_num
                    #　循环更新time_num
                    circle = 1
                    while circle < 2:
                        sleep(1)
                        if not downloading or not paing:
                            try:
                                timenumm = time_num * 10000
                                current = mixer.music.get_pos()  # 毫秒
                                current %= timenumm
                                assq = current / timenumm * 10000
                                assq = int(assq * 10)
                                if not assq > 10000:
                                    self.trigger.emit(str(assq))  # 显示进度条到GUI

                                else:
                                    assq = 10000
                                    self.trigger.emit(str(assq))  # 返回进度条数据

                            except:
                                try:
                                    if mixer.music.get_busy():  # 测试混音器是否正在使用
                                        print('进度条错误')
                                except:
                                    pass
                except:
                    pass

            except:
                pass
        except:
            pass


# 加载初始图片线程 待完善
class picThread(QThread):
    trigger = pyqtSignal(str)

    def __int__(self):
        super(picThread, self).__init__()

    def run(self):
        pass


# exe启动进程
class startThread(QThread):
    trigger = pyqtSignal(str)

    def __int__(self):
        super(startThread, self).__init__()

    def run(self):
        try:
            apdatas = getenv("APPDATA")
            filepaths = '{}/musicdata'.format(apdatas)
            global loves
            global lovepics
            global loveurls
            global lovelrc
            global voice

            # 读取数据
            try:
                # 读取声音大小
                with open(filepaths + "/voice", 'r', encoding='utf-8') as f:
                    a = f.read()
                    voice = float(a)
                self.trigger.emit(str('voicedone'))  # 呈现
            except:
                self.trigger.emit(str('voicedone'))
                pass
            # 读取“我喜欢”
            with open(filepaths + "/loves", 'r', encoding='utf-8') as f:
                a = f.read()
            strer = a
            loves = literal_eval(strer)
            # 读取“我喜欢”图片
            with open(filepaths + "/lovepics", 'r', encoding='utf-8') as f:
                a = f.read()
            strer = a
            lovepics = literal_eval(strer)
            # 读取“我喜欢”歌曲地址
            with open(filepaths + "/loveurls", 'r', encoding='utf-8') as f:
                a = f.read()
            strer = a
            loveurls = literal_eval(strer)
            # 读取“我喜欢”歌曲歌词
            with open(filepaths + "/lovelrc", 'r', encoding='utf-8') as f:
                a = f.read()
            strer = a
            lovelrc = literal_eval(strer)

            self.trigger.emit(str('login'))
            # 打印"我喜欢"列表
            print(loves)
            print('read loves finish')
        except:
            print('read loves error')
            pass
        # 读取数据结束


# 爬虫获取歌曲html
class PAThread(QThread):
    trigger = pyqtSignal(str)

    def __init__(self):
        super(PAThread, self).__init__()

    def run(self):
        # 线程锁 确保顺序
        qmut.lock()
        try:
            global paing
            global stop
            global lrcs
            global urls
            global songs
            global name
            global songid
            global proxies
            global pic
            global tryed
            paing = True

            print('搜索音频来源{}'.format(type))
            print('开始搜索')
            name = name
            # 请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.110.430.128 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest'
            }
            urls = []
            songs = []
            pic = []
            lrcs = []
            pages = 5

            for a in range(1, pages + 1):
                if not stop:
                    # 搜索来源 主要是http://music.9q4.cn/进行爬取
                    urlss = ['http://music.9q4.cn/', 'https://defcon.cn/dmusic/', 'http://www.xmsj.org/',
                            'http://music.laomao.me/']
                    print(tryed)
                    # 设置爬取网站来源
                    if tryed > 3:
                        tryed = 0
                        url = urlss[tryed]
                    else:
                        url = urlss[tryed]
                    print(urlss[tryed])

                    params = {'input': name,
                            'filter': 'name',
                            'type': type,
                            'page': a
                            }
                    # 爬虫核心
                    if not stop:
                        try:
                            # 获取json文件 jsonpath类似xpath 获取歌名，作者，地址，图片，歌词并保存
                            res = post(url, params, headers=headers, proxies=proxies)
                            html = res.json()
                            print(html)
                            for i in range(0, 10):
                                try:
                                    # 处理文件 解析数据
                                    title = jsonpath(html, '$..title')[i]
                                    author = jsonpath(html, '$..author')[i]
                                    url1 = jsonpath(html, '$..url')[i]  # 取下载网址
                                    pick = jsonpath(html, '$..pic')[i]  # 取图片
                                    lrc = jsonpath(html, '$..lrc')[i]
                                    print(title, author)
                                    lrcs.append(lrc)
                                    urls.append(url1)
                                    pic.append(pick)
                                    songs.append(str(title) + ' - ' + str(author))
                                except:
                                    pass
                        except:
                            stop = False
                            paing = False
                        self.trigger.emit(str('finish'))
                    else:
                        print('stop')
                        self.trigger.emit(str('finish'))
                else:
                    print('stop')
                    self.trigger.emit(str('clear'))
                    pass

            stop = False
            paing = False

        except:
            print('爬取歌曲出错')
            self.trigger.emit(str('unfinish'))
            stop = False
            paing = False
        qmut.unlock()

# 线程：分区下载全部
class downall(QThread):
    trigger = pyqtSignal(str)
    def __init__(self):
        super(downall, self).__init__()

    def run(self):
        global namem
        try:    # 我喜欢列表下载
            if typerr == 'love':
                list_name = loves
                url_name = loveurls
                # 搜索列表下载
            elif typerr == 'boing':
                list_name = songs
                url_name = urls
                namem = name

            if not list_name == []:
                for i in range(0, len(list_name)):
                    try:
                        # 下载爬虫
                        url1 = url_name[i]
                        path = str(data + '\{}.all临时文件'.format(i))
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.110.430.128 Safari/537.36',
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                        # 下载
                        with  get(url1, stream=True, headers=headers) as r, open(path, 'wb') as file:
                            total_size = int(r.headers['content-length'])
                            content_size = 0
                            for content in r.iter_content(chunk_size=1024):
                                file.write(content)
                                content_size  += len(content)
                                # 进度
                                plan = (content_size / total_size) * 100
                                develop = str(int(plan)) + str('%')
                                self.trigger.emit(str(develop))
                        # 分类设置文件夹路径
                        if typerr == 'love':
                            to = 'downloadmusic\love\{}.mp3'.format(loves[i])
                            try:
                                makedirs('downloadmusic\love', exist_ok=True)
                            except:
                                pass
                        elif typerr == 'boing':
                            to = 'downloadmusic/' + str(namem) + '/{}.mp3'.format(songs[i])
                            try:
                                makedirs('downloadmusic\{}'.format(namem), exist_ok=True)
                            except:
                                pass

                        try:
                            copyfile(path, to)
                        except:
                            pass

                    except:
                        print("下载错误")
                        pass
                self.trigger.emit(str('finish'))
                if typerr == 'boing':
                    cmd = 'explorer /select,{}'.format('downloadmusic\{}'.format(namem))  # 打开文件夹
                    print(cmd)
                    call(cmd)
                    sleep(4)
                elif typerr == 'love':
                    cmd = 'explorer /select,{}'.format('downloadmusic\{}'.format('love'))
                    print(cmd)
                    call(cmd)
                    sleep(4)
                self.trigger.emit(str('disappear'))
            else:
                pass
        except:
            print('error')
            pass


# 多线程下载爬取的待播放的url
class WorkThread(QThread):
    trigger = pyqtSignal(str)

    def __int__(self):
        super(WorkThread, self).__init__()

    def run(self):
        global to
        global number
        global path
        global downloading
        global pic
        global lrct
        global lrcd
        global picno
        global stopdown
        # 搜索框work
        if bo == 'boing':
            try:
                # 代理
                proxies = {
                    'http': 'http://124.72.109.183:8118',
                    ' Shttp': 'http://49.85.1.79:31666'

                }
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest'}

                # 处理图片
                try:
                    try:
                        try:
                            # 获取PAThread已得到的pic
                            aq = pic[num]
                            aqq = aq.split('/')

                        except:
                            pass
                        # 解析不同来源html图片数据
                        if type  == 'kugou' and len(aqq) - 1 == 6:
                            aqqe = str(aqq[0]) + str('//') + str(aqq[2]) + str('/') + str(aqq[3]) + str('/') + str(
                                '400') + str('/') + str(aqq[5]) + str('/') + str(aqq[6])
                            print(aqqe)
                        elif type == 'netease' and len(aqq) - 1 == 4:
                            aqn = aq.split('?')
                            b = '?param=500x500'
                            aqqe = (str(aqn[0]) + str(b))
                            print(aqqe)
                        else:
                            aqqe = pic[num]
                        req = get(aqqe)  # 得到图片url
                        # 写入（下载）图片
                        checkfile = open(str(data + '/ls1.png'), 'w+b')
                        for i in req.iter_content(100000):
                            checkfile.write(i)
                        checkfile.close()

                        lsfile = str(data + '/ls1.png')
                        safile = str(data + '/back.png')
                        draw(lsfile, safile)
                        picno = True
                    except:
                        print('图片下载错误')
                        picno = False
                        pass
                    url1 = urls[num]
                    print(url1)
                    number = number + 1
                    path = str(data + '\{}.临时文件'.format(number))
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.110.430.128 Safari/537.36',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                    # 下载歌曲
                    with get(url1, stream=True, headers=headers) as r, open(path, 'wb') as file:
                        total_size = int(r.headers['content-length'])
                        content_size = 0
                        for content in r.iter_content(chunk_size=1024):
                            if not stopdown:
                                file.write(content)
                                content_size += len(content)
                                plan = (content_size / total_size) * 100
                                develop = str(int(plan)) + str('%')
                                self.trigger.emit(str(develop))
                            else:
                                print('stopdown')
                                break
                            stopdown = False

                    to = 'downloadmusic\{}.mp3'.format(songs[num])
                    makedirs('downloadmusic', exist_ok=True)
                except:
                    pass
                # 获取歌词
                try:
                    if bo == 'boing':
                        lrct = []  # 总歌词列表
                        f = lrcs[num]  # 按行读取
                        lines = f.split('\n')
                        # 处理歌词 解析数据
                        if not lines == ['']:
                            for i in lines:
                                if not i == '':
                                    line1 = i.split('[')
                                    try:
                                        line2 = line1[1].split(']')
                                        if line2 == '':
                                            pass
                                        else:
                                            linew = line2[1]
                                            lrct.append(linew)
                                        self.trigger.emit(str('lrcfinish'))
                                    except:
                                        print('{}的歌词错误'.format(str(line1)))
                                else:
                                    pass
                        else:
                            self.trigger.emit(str('lrcnofinish'))
                            print('没有歌词')
                except:
                    print('歌词错误')

                try:
                    copyfile(path, to)
                except:
                    pass
                downloading = False
                self.trigger.emit(str('finish'))

            except:
                self.trigger.emit(str('nofinish'))
        #  最近播放work （类似boing）
        elif bo == 'boed':
            try:
                proxies = {
                    'http': 'http://124.72.109.183:8118',
                    'http': 'http://49.85.1.79:31666'

                }
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest'}
                try:
                    try:
                        try:
                            aq = picd[num]
                            aqq = aq.split('/')
                        except:
                            pass
                        if type == 'kugou' and len(aqq) - 1 == 6:
                            aqqe = str(aqq[0]) + str('//') + str(aqq[2]) + str('/') + str(aqq[3]) + str('/') + str(
                                '400') + str('/') + str(aqq[5]) + str('/') + str(aqq[6])
                            print(aqqe)
                        elif type == 'netease' and len(aqq) - 1 == 4:
                            aqn = aq.split('?')
                            b = '?param=500x500'
                            aqqe = (str(aqn[0]) + str(b))
                            print(aqqe)
                        else:
                            aqqe = picd[num]
                        req = get(aqqe)

                        checkfile = open(str(data + '/ls1.png'), 'w+b')
                        for i in req.iter_content(100000):
                            checkfile.write(i)
                        checkfile.close()

                        lsfile = str(data + '/ls1.png')
                        safile = str(data + '/back.png')
                        draw(lsfile, safile)
                        picno = True
                    except:
                        print('图片下载错误')
                        picno = False
                        pass

                    url1 = urled[num]
                    print(url1)
                    number = number + 1
                    path = str(data + '\{}.临时文件'.format(number))
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.110.430.128 Safari/537.36',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                    with get(url1, stream=True, headers=headers) as r, open(path, 'wb') as file:
                        total_size = int(r.headers['content-length'])
                        content_size = 0
                        for content in r.iter_content(chunk_size=1024):
                            if not stopdown:
                                file.write(content)
                                content_size += len(content)
                                plan = (content_size / total_size) * 100
                                develop = str(int(plan)) + str('%')
                                self.trigger.emit(str(develop))
                            else:
                                print ('down')
                                break
                            stopdown = False
                    to = 'downloadmusic\{}.mp3'.format(songed[num])
                    makedirs('downloadmusic', exist_ok=True)
                except:
                    self.trigger.emit(str('nofinish'))
                    pass

                try:
                    # boing已存储 只需解析歌词
                    lrct = []  # 总歌词列表
                    f = lrcd[num]  # 按行读取
                    lines = f.split('\n')
                    for i in lines:
                        line1 = i.split('[')
                        try:
                            line2 = line1[1].split(']')
                            if line2 == '':
                                pass
                            else:
                                linew = line2[1]
                                lrct.append(linew)
                            self.trigger.emit(str('lrcfinish'))
                        except:
                            print('歌词错误')

                except:
                    pass

                try:
                    copyfile(path, to)
                except:
                    pass
                downloading = False
                self.trigger.emit(str('finish'))

            except:
                self.trigger.emit(str('nofinish'))
        # 我喜欢work（类似）
        elif bo == 'love':
            try:
                proxies = {
                    'http': 'http://124.72.109.183:8118',
                    'http': 'http://49.85.1.79:31666'

                }
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest'}
                try:
                    try:
                        try:
                            aq = lovepics[num]
                            aqq = aq.split('/')
                        except:
                            pass
                        if type == 'kugou' and len(aqq) - 1 == 6:
                            aqqe = str(aqq[0]) + str('//') + str(aqq[2]) + str('/') + str(aqq[3]) + str('/') + str(
                                '400') + str('/') + str(aqq[5]) + str('/') + str(aqq[6])
                            print(aqqe)
                        elif type == 'netease' and len(aqq) - 1 == 4:
                            aqn = aq.split('?')
                            b = '?param=500x500'
                            aqqe = (str(aqn[0]) + str(b))
                            print(aqqe)
                        else:
                            aqqe = lovepics[num]
                        req = get(aqqe)

                        checkfile = open(str(data + '/ls1.png'), 'w+b')
                        for i in req.iter_content(100000):
                            checkfile.write(i)
                        checkfile.close()

                        lsfile = str(data + '/ls1.png')
                        safile = str(data + '/back.png')
                        draw(lsfile, safile)
                        picno = True
                    except:
                        print('图片错误')
                        picno = False
                        pass

                    url1 = loveurls[num]
                    print(url1)
                    number = number + 1
                    path = str(data + '\{}.临时文件'.format(number))
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.110.430.128 Safari/537.36',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                    with get(url1, stream=True, headers=headers) as r, open(path, 'wb') as file:
                        total_size = int(r.headers['content-length'])
                        content_size = 0
                        for content in r.iter_content(chunk_size=1024):
                            if not stopdown:
                                file.write(content)
                                content_size += len(content)
                                plan = (content_size / total_size) * 100
                                develop = str(int(plan)) + str('%')
                                self.trigger.emit(str(develop))
                            else:
                                print('down')
                                break
                            stopdown = False
                    to = 'downloadmusic\{}.mp3'.format(songed[num])
                    makedirs('downloadmusic', exist_ok=True)
                except:
                    self.trigger.emit(str('nofinish'))
                    pass

                try:
                    # boing已处理 只需解析歌词
                    lrct = []  # 总歌词列表
                    f = lovelrc[num]  # 按行读取
                    lines = f.split('\n')
                    for i in lines:
                        line1 = i.split('[')
                        try:
                            line2 = line1[1].split(']')
                            if line2 == '':
                                pass
                            else:
                                linew = line2[1]
                                lrct.append(linew)
                            self.trigger.emit(str('lrcfinish'))
                        except:
                            print('歌词错误')
                            pass
                except:
                    pass

                try:
                    copyfile(path, to)
                except:
                    pass
                downloading = False
                self.trigger.emit(str('finish'))

            except:
                self.trigger.emit(str('nofinish'))


# pyqt5 GUI界面布局
class MainUi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()  # 初始化就界面
        self.start()    # 启动

        try:
            # 设置界面左上角图标
            icon_path = pathq.join(pathq.dirname(__file__),  './logo.ico')
            icon = QIcon()
            icon.addPixmap(QPixmap(icon_path))
            self.setWindowIcon(icon)
        except:
            pass
        # 启动action线程
        t1 = Thread(target=self.action)
        t1.setDaemon(True)
        t1.start()

    def init_ui(self):
        global type
        self.setFixedSize(1025, 750)    # 设置固定大小界面
        self.setWindowTitle('music_radio')  # 设置标题
        self.main_widget = QWidget()  # 创建窗口主部件
        self.main_layout = QGridLayout()  # 创建主部件的网格布局
        self.main_widget.setLayout(self.main_layout)  # 设置窗口主部件布局为网格布局

        # 创建左侧栏控件与网格布局
        self.left_widget = QWidget()
        self.left_widget.setObjectName('left_widget')
        self.left_layout = QGridLayout()
        self.left_widget.setLayout(self.left_layout)
        # 创建右侧栏控件与网格布局
        self.right_widget = QWidget()
        self.right_widget.setObjectName('right_widget')
        self.right_layout = QGridLayout()
        self.right_widget.setLayout(self.right_layout)
        # 创建上侧栏控件与网格布局
        self.up_widget = QWidget()
        self.up_widget.setObjectName('up_widget')
        self.up_layout = QGridLayout()
        self.up_widget.setLayout(self.up_layout)
        # 创建下侧栏控件与网格布局
        self.down_widget = QWidget()
        self.down_widget.setObjectName('down_widget')
        self.down_layout = QGridLayout()
        self.down_widget.setLayout(self.down_layout)

        # 播放信息栏 文字与QSS样式
        self.label = QLabel(self)
        self.label.setText("暂无歌曲播放")
        self.label.setStyleSheet("color:black")
        self.label.setMaximumSize(310, 20)

        # 加载上下左右部件到主窗口
        self.main_layout.addWidget(self.up_widget, 0, 0, 1, 120)
        self.main_layout.addWidget(self.left_widget, 1, 0, 90, 25)
        self.main_layout.addWidget(self.right_widget, 1, 25, 90, 90)
        self.main_layout.addWidget(self.down_widget, 100, 0, 10, 115)

        # 播放信息部件加载到下部件
        self.down_layout.addWidget(self.label, 1, 0, 1, 1)
        self.setCentralWidget(self.main_widget)  # 设置窗口主部件为center

        # 右侧栏
        # 设置表格（在右侧栏） 搜索 最近播放 我喜欢 歌词 本地
        self.tabWidget = QTabWidget(self)
        self.tabWidget.setGeometry(QRect(33, 20, 716, 471))

        # 列表1 搜索
        self.tab = QWidget()
        self.tab.setObjectName("tab")
        self.tab_layout = QGridLayout()
        self.tab.setLayout(self.tab_layout)
        self.listwidget = QListWidget(self.tab)

        # 下载完毕提示标签
        self.label_disdownall = QLabel(self)
        self.label_disdownall.setText("")
        self.label_disdownall.setStyleSheet("color:white")
        self.tab_layout.addWidget(self.label_disdownall, 0, 1, 1, 1)
        # 下载全部标签
        self.button_1235 = QPushButton(icon('fa.download', color='black', font=24), "下载全部")
        self.button_1235.clicked.connect(self.downloadalls)
        self.button_1235.setStyleSheet(
            '''QPushButton{background:white;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.tab_layout.addWidget(self.button_1235, 0, 2, 1, 1)
        # 请处理表标签
        self.button_1236 = QPushButton(icon('fa.trash-o', color='black', font=24), "清空列表")
        self.button_1236.clicked.connect(self.dell)
        self.button_1236.setStyleSheet(
            '''QPushButton{background:white;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.tab_layout.addWidget(self.button_1236, 0, 3, 1, 1)
        # 搜索栏信号与槽连接
        self.listwidget.doubleClicked.connect(lambda: self.change_func(self.listwidget))
        self.listwidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listwidget.customContextMenuRequested[QPoint].connect(self.myListWidgetContext)
        self.listwidget.setObjectName("listWidget")
        self.tab_layout.addWidget(self.listwidget, 1, 0, 1, 4)
        self.tabWidget.addTab(self.tab, "     搜索     ")

        # 列表2 最近播放
        self.tab2 = QWidget()
        self.tab2.setObjectName("tab")
        self.tab2_layout = QGridLayout()
        self.tab2.setLayout(self.tab2_layout)
        self.listwidget2 = QListWidget(self.tab2)
        self.listwidget2.doubleClicked.connect(lambda: self.change_funcse(self.listwidget2))
        self.listwidget2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listwidget2.customContextMenuRequested[QPoint].connect(self.myListWidgetContext2)
        self.listwidget2.setObjectName("listWidget2")
        self.listwidget2.setContextMenuPolicy(3)
        self.tab2_layout.addWidget(self.listwidget2, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab2, "     最近播放     ")

        # 列表3 我喜欢
        self.tab3 = QWidget()
        self.tab3.setObjectName("tab")
        self.tab3_layout = QGridLayout()
        self.tab3.setLayout(self.tab3_layout)

        # 我喜欢 图片加载  error
        # self.label223 = QLabel(self)
        # pix_img = QPixmap(str(data + '/backdown.png'))
        # pix = pix_img.scaled(100, 100, Qt.KeepAspectRatio)
        # self.label223.setPixmap(pix)
        # self.tab3_layout.addWidget(self.label223, 0, 0, 1, 1)

        # 播放全部标签
        self.button_1237 = QPushButton(icon('fa.play', color='black', font=24), "播放全部")
        self.button_1237.clicked.connect(self.allplaylove)
        self.button_1237.setStyleSheet(
            '''QPushButton{background:white;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.tab3_layout.addWidget(self.button_1237, 0, 1, 1, 1)
        # 下载全部标签
        self.button_1235 = QPushButton(icon('fa.download', color='black', font=24), "下载全部")
        self.button_1235.clicked.connect(self.downloadalllove)
        self.button_1235.setStyleSheet(
            '''QPushButton{background:white;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.tab3_layout.addWidget(self.button_1235, 0, 2, 1, 1)
        # 清除列表标签
        self.button_1236 = QPushButton(icon('fa.trash-o', color='black', font=24), "清空列表")
        self.button_1236.clicked.connect(self.delove)
        self.button_1236.setStyleSheet(
            '''QPushButton{background:white;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.tab3_layout.addWidget(self.button_1236, 0, 3, 1, 1)

        self.listwidget3 = QListWidget(self.tab3)
        self.listwidget3.doubleClicked.connect(lambda: self.change_funclove(self.listwidget3))
        self.listwidget3.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listwidget3.customContextMenuRequested[QPoint].connect(self.myListWidgetContext3)
        self.listwidget3.setObjectName("listWidget3")
        self.tab3_layout.addWidget(self.listwidget3, 1, 0, 1, 4)
        self.tabWidget.addTab(self.tab3, "     我喜欢     ")

        # 列表4 歌词
        self.tab4 = QWidget()
        self.tab4.setObjectName("tab")
        self.tab4_layout = QGridLayout()
        self.tab4.setLayout(self.tab4_layout)
        self.listwidget4 = QListWidget(self.tab4)
        self.listwidget4.setObjectName("listWidget4")
        self.tab4_layout.addWidget(self.listwidget4, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab4, "     歌词     ")

        # 列表5 本地歌曲
        self.tab5 = QWidget()
        self.tab5.setObjectName("tab5")
        self.tab5_layout = QGridLayout()
        self.tab5.setLayout(self.tab5_layout)
        self.listwidget5 = QListWidget(self.tab5)
        self.listwidget5.doubleClicked.connect(lambda: self.change(self.listwidget5))
        self.listwidget5.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listwidget5.customContextMenuRequested[QPoint].connect(self.myListWidgetContext5)

        # 添加目录标签
        self.button_12351 = QPushButton(icon('fa.download', color='black', font=24), "添加目录")
        self.button_12351.clicked.connect(self.add)
        self.button_12351.setStyleSheet(
            '''QPushButton{background:white;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.tab5_layout.addWidget(self.button_12351, 0, 2, 1, 1)
        # 清空列表标签
        self.button_12361 = QPushButton(icon('fa.trash-o', color='black', font=24), "清空列表")
        self.button_12361.clicked.connect(self.dellocal)
        self.button_12361.setStyleSheet(
            '''QPushButton{background:white;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.tab5_layout.addWidget(self.button_12361, 0, 3, 1, 1)

        self.listwidget5.setObjectName("listWidget5")
        self.tab5_layout.addWidget(self.listwidget5, 1, 0, 1, 4)
        self.tabWidget.addTab(self.tab5, "     本地歌曲     ")

        # 将列表栏加入右侧栏
        self.right_layout.addWidget(self.tabWidget, 3, 0, 100, 90)

        # 左侧栏
        # 播放模式标签
        self.label2 = QLabel(self)
        self.label2.setText("顺序播放")
        self.label2.setStyleSheet("color:black")
        self.left_layout.addWidget(self.label2, 4, 0, 2, 1)

        # 单曲下载标签
        self.button_1234 = QPushButton(icon('fa.download', color='black', font=24), "")
        self.button_1234.clicked.connect(self.down)
        self.button_1234.setStyleSheet(
            '''QPushButton{background:white;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.left_layout.addWidget(self.button_1234, 4, 2, 2, 2)
        # 添加到我喜欢标签
        self.button_1234 = QPushButton(icon('fa.heart', color='black', font=24), "")
        self.button_1234.clicked.connect(self.lovesong)
        self.button_1234.setStyleSheet(
            '''QPushButton{background:white;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        self.left_layout.addWidget(self.button_1234, 4, 4, 2, 2)

        # 音量大小标签
        self.label3 = QLabel(self)
        self.label3.setText("")
        self.down_layout.addWidget(self.label3, 1, 3, 1, 1)

        # blank
        self.label7 = QLabel(self)
        self.label7.setText("")

        # 歌曲图片加载
        self.label5 = QLabel(self)
        pix_img = QPixmap(str(data + '/backdown.png'))
        pix = pix_img.scaled(300, 300, Qt.KeepAspectRatio)
        self.label5.setPixmap(pix)
        self.left_layout.addWidget(self.label5, 2, 0, 2, 8)

        # blank
        self.label6 = QLabel(self)
        self.label6.setText("")
        self.left_layout.addWidget(self.label6, 2, 0, 2, 2)

        # 音乐馆搜索标签
        self.label23 = QLabel(self)
        self.label23.setText("                 音乐馆搜索")
        self.up_layout.addWidget(self.label23, 0, 100, 1, 20)

        # 输入栏
        self.shuru = QLineEdit("")
        self.up_layout.addWidget(self.shuru, 0, 120, 1, 40)
        self.shuru.returnPressed.connect(self.correct)

        # 音频来源标签
        self.label23 = QLabel(self)
        self.label23.setText("     音频来源")
        self.up_layout.addWidget(self.label23, 0, 160, 1, 10)

        # blank
        self.label61 = QLabel(self)
        self.label61.setText("")
        self.up_layout.addWidget(self.label61, 0, 200, 1, 50)

        # 下拉菜单
        self.cb = QComboBox(self)
        self.cb.addItems(['酷狗', '网易云', 'qq', '酷我'])
        self.up_layout.addWidget(self.cb, 0, 180, 1, 30)
        self.cb.currentIndexChanged[int].connect(self.print)

        # 搜索按钮
        self.button_1 = QPushButton(icon('fa.search', color='black'), "")
        self.button_1.clicked.connect(self.correct)
        self.up_layout.addWidget(self.button_1, 0, 155, 1, 5)

        # 进度条线程设置
        self.right_process_bar = QProgressBar()  # 播放进度部件
        self.right_process_bar.setValue(49)
        self.right_process_bar.setFixedHeight(3)  # 设置进度条高度
        self.right_process_bar.setTextVisible(False)  # 不显示进度条文字
        self.right_process_bar.setRange(0, 10000)

        # 右侧栏播放控制组件
        self.right_playconsole_widget = QWidget()  # 播放控制部件
        self.right_playconsole_layout = QGridLayout()  # 播放控制部件网格布局层
        self.right_playconsole_widget.setLayout(self.right_playconsole_layout)

        # 上一首
        self.console_button_1 = QPushButton(icon('fa.backward', color='black'), "")
        self.console_button_1.clicked.connect(self.last)
        self.console_button_1.setStyleSheet(
            '''QPushButton{background:white;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        # 下一首
        self.console_button_2 = QPushButton(icon('fa.forward', color='black'), "")
        self.console_button_2.clicked.connect(self.nextion)
        self.console_button_2.setStyleSheet(
            '''QPushButton{background:white;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        # 暂停
        self.console_button_3 = QPushButton(icon('fa.pause', color='black', font=20), "")
        self.console_button_3.clicked.connect(self.pause)
        self.console_button_3.setStyleSheet(
            '''QPushButton{background:white;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        # 音量减
        self.console_button_4 = QPushButton(icon('fa.volume-down', color='black', font=20), "")
        self.console_button_4.clicked.connect(self.voicedown)
        self.console_button_4.setStyleSheet(
            '''QPushButton{background:white;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        # 音量加
        self.console_button_5 = QPushButton(icon('fa.volume-up', color='black', font=20), "")
        self.console_button_5.clicked.connect(self.voiceup)
        self.console_button_5.setStyleSheet(
            '''QPushButton{background:white;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')
        # 播放模式
        self.console_button_6 = QPushButton(icon('fa.align-center', color='black', font=20), "")
        self.console_button_6.clicked.connect(self.playmode)
        self.console_button_6.setStyleSheet(
            '''QPushButton{background:white;border-radius:5px;}QPushButton:hover{background:#3684C8;}''')

        # 暂停size增大
        self.console_button_3.setIconSize(QSize(30, 30))
        # 播放控制组件布局
        self.right_playconsole_layout.addWidget(self.console_button_4, 0, 0)
        self.right_playconsole_layout.addWidget(self.console_button_1, 0, 1)
        self.right_playconsole_layout.addWidget(self.console_button_3, 0, 2)
        self.right_playconsole_layout.addWidget(self.console_button_2, 0, 3)
        self.right_playconsole_layout.addWidget(self.console_button_5, 0, 4)
        self.right_playconsole_layout.addWidget(self.console_button_6, 0, 5)
        # 设置布局内部件居中显示
        self.right_playconsole_layout.setAlignment(Qt.AlignCenter)
        # 进度条布局
        self.down_layout.addWidget(self.right_process_bar, 0, 0, 1, 4)

        self.down_layout.addWidget(self.label7, 1, 2, 1, 1)  # blank
        # 播放控制栏布局
        self.down_layout.addWidget(self.right_playconsole_widget, 1, 0, 1, 4)
        # 设置窗口透明度
        self.setWindowOpacity(0.95)
        # 组件间间隙控制
        self.main_layout.setSpacing(0)


    # 本地播放
    # 页表显示后双击获取当前行歌曲名可本地播放
    def change(self, listwidget):
        global num
        global bo
        bo = 'local'
        num = int(listwidget.currentRow())
        print(num)
        # 设置标签的文本为音乐的名字
        f = str(SongName[num]).split('.mp3')
        f = str(f[0]).split('.flac')
        f = str(f[0]).split('.MP3')
        f = str(f[0]).split('.FLAC')
        f = str(f[0]).split('.wma')
        f = str(f[0]).split('.WMA')
        self.label.setText(f[0])
        print(listwidget.currentRow())
        self.bofanglocal()  # 本地播放

    def bofanglocal(self):
        try:
            global pause
            try:
                self.photo('local')
            except:
                pass
            self.console_button_3.setIcon(icon('fa.pause', color='#F76677', font=18))
            pause = False
            # 本地歌曲路径
            fill = SongPath[num]
            print(fill)
            # 加载本地歌曲进度条
            try:
                global time_num
                mp3 = str(SongPath[num])
                xx = load(mp3)
                time_num = xx.info.time_secs
                global start
                start = True
            except:
                print('进度条错误，播放失败')
            try:
                mixer.stop()
            except:
                pass
            try:
                # 载入音乐
                mixer.music.load(SongPath[num])
                mixer.music.play()  # 播放音乐
            except:
                print('MP3音频文件出现错误')

        except:
            sleep(0.1)
            print('system error')
            self.next()
            pass

    # 添加本地文件夹歌曲
    def add(self):
        try:
            global SongPath
            global SongName
            global num
            global filew
            global asas
            fileN = QFileDialog.getExistingDirectory(None, "选取文件夹", "")
            if not fileN == '':
                self.listwidget5.clear()  # 列表5清空
                filew = fileN + '/'
                asas = filew
                l1 = [name for name in listdir(fileN) if
                      name.endswith('.mp3') or name.endswith('.flac') or name.endswith('.wma') or name.endswith(
                          '.MP3') or name.endswith('.FLAC') or name.endswith('.WMA')]
                SongNameadd = l1
                SongPathadd = [filew + i for i in  SongNameadd]
                SongName = SongName + SongNameadd
                SongPath = SongPath + SongPathadd
                print(SongPath)
                # 将文件名添加到listWidget
                r = 0
                for i in SongName:
                    self.listwidget5.addItem(i)
                    self.listwidget5.item(r).setForeground(Qt.black)
                    r = r + 1
        except:
            filew = asas



    # 清空搜索栏列表全部歌曲
    def dell(self):
        self.delall('boing')

    # 下载搜索栏全部歌曲
    def downloadalls(self):
        self.downloadall('boing')

    # 清空本地列表全部歌曲
    def dellocal(self):
        self.delall('local')

    # 清空我喜欢列表全部歌曲
    def delove(self):
        self.delall('love')

    # 播放我喜欢全部歌曲
    def allplaylove(self):
        self.playall('love')

    # 下载我喜欢全部歌曲
    def downloadalllove(self):
        self.downloadall('love')

    # 删除清空方法: 我喜欢、搜索栏、本地栏清空
    def delall(self, typer):
        if typer == 'love':
            global loves
            global loveurls
            global lovelrc
            global lovepics
            loveurls = []
            lovelrc = []
            lovepics = []
            loves = []
            self.listwidget3.clear()
        elif typer == 'boing':
            print(typer)
            self.listwidget.clear()
            global songs
            global urls
            global lrcs
            global pic
            songs = []
            urls = []
            lrcs = []
            pic = []
        elif typer == 'local':
            print(typer)
            self.listwidget5.clear()
            global SongName
            global SongPath
            SongName = []
            SongPath = []

    # 播放全部歌曲方法：
    def playall(self, typer):
        global num
        global bo
        try:
            bo = typer
            num = 0
            self.bofang(bo, num)  # 调用播放音乐方法
        except:
            print('playall error')
            pass

    # 全部下载方法：
    def downloadall(self, typer):
        try:
            global typerr
            typerr = typer
            print(typer)
            print(typerr)
            self.work = downall()  # 创建全部下载线程
            self.work.start()
            self.work.trigger.connect(self.disdownall)
        except:
            print('默认图片下载错误')
            pass

    # 下载完毕槽
    def disdownall(self, czk):
        if czk == 'finish':
            self.label_disdownall.setText('下载完毕')

        elif czk == 'disappear':
            self.label_disdownall.setText('')
        else:
            self.label_disdownall.setText(czk)


    # 窗口控制 增加右键选项
    # 列表1 搜索
    def myListWidgetContext(self, point):
        global num_m
        try:
            num_m = int(self.listwidget.currentRow())
            print(num_m)
        except:
            pass
        if not num_m == -1:
            global list_confident
            list_confident = 'boing'
            # 右键表单action QMenu与menubar创建并连接信号与槽
            popMenu = QMenu()
            popMenu.addAction(QAction(u'添加到喜爱的歌', self, triggered=self.addItem))
            popMenu.addAction(QAction(u'从列表中删除', self, triggered=self.deItem))
            popMenu.exec_(QCursor.pos())

    # 列表2 最近播放
    def myListWidgetContext2(self, point):
        global num_m
        try:
            num_m = int(self.listwidget2.currentRow())
            print(num_m)
        except:
            pass
        if not num_m == -1:
            global list_confident
            list_confident = 'boed'
            # 右键表单action
            popMenu = QMenu()
            popMenu.addAction(QAction(u'添加到喜爱的歌', self, triggered=self.addItem))
            popMenu.addAction(QAction(u'从列表中删除', self, triggered=self.deItem))
            popMenu.exec_(QCursor.pos())

    # 列表3 我喜欢 （注：只有从列表中删除）
    def myListWidgetContext3(self, point):
        global num_m
        try:
            num_m = int(self.listwidget3.currentRow())
            print(num_m)
        except:
            pass
        if not num_m == -1:
            global list_confident
            list_confident = 'love'
            popMenu = QMenu()
            popMenu.addAction(QAction(u'从列表中删除', self, triggered=self.deItem))
            popMenu.exec_(QCursor.pos())

    # 列表4 歌词 无

    # 列表5 本地 无网络 无法加载到我喜欢
    def myListWidgetContext5(self):
        global num_m
        try:
            num_m = int(self.listwidget5.currentRow())
            print(num_m)
        except:
            pass
        if not num_m == -1:
            global list_confident
            list_confident = 'local'
            popMenu = QMenu()
            popMenu.addAction(QAction(u'从列表中删除', self, triggered=self.deItem))
            popMenu.exec_(QCursor.pos())


    # 添加我喜欢两种方式
    # 1.右键添加到我喜欢__方法（槽）
    def addItem(self):
        try:
            global loves
            global loveurls
            global lovepics
            global lovelrc
            # 从搜索栏添加
            if list_confident == 'boing':
                loves.append(songs[num_m])
                loveurls.append(urls[num_m])
                lovepics.append(pic[num_m])
                lovelrc.append(lrcs[num_m])
            # 从最近播放添加
            else:
                loves.append(songed[num_m])
                loveurls.append(urled[num_m])
                lovepics.append(picd[num_m])
                lovelrc.append(lrcd[num_m])
            # 显示我喜欢栏的图片 尚未完成
            self.work = picThread()
            self.work.start()
            self.work.trigger.connect(self.dispng)
            # 加载我喜欢图片 未完善
        except:
            pass
        r = 0
        self.listwidget3.clear()
        for i in loves:
            # 将文件名添加到listWidget
            self.listwidget3.addItem(i)
            self.listwidget3.item(r).setForeground(Qt.black)
            r = r + 1
        print('add of love songs done')
        print(loves)

    # 2.通过fa.heart按钮添加到我喜欢
    def lovesong(self):
        if bo == 'boing' or bo == 'boed':
            try:
                global loves
                global loveurls
                global lovepics
                global lovelrc
                if bo == 'boing':
                    loves.append(songs[num])
                    loveurls.append(urls[num])
                    lovepics.append(pic[num])
                    lovelrc.append(lrcs[num])
                elif bo == 'boed':
                    loves.append(songed[num])
                    loveurls.append(urled[num])
                    lovepics.append(picd[num])
                    lovelrc.append(lrcd[num])
                else:
                    pass
            except:
                pass
            # 加载我喜欢图片 未完善
            self.work = picThread()
            self.work.start()
            self.work.trigger.connect(self.dispng)
            # 加载我喜欢图片 未完善
            r = 0
            self.listwidget3.clear()
            for i in loves:
                # 将文件名添加到listWidget
                self.listwidget3.addItem(i)
                self.listwidget3.item(r).setForeground(Qt.black)
                r = r + 1
            print('add of love songs done')
            print(loves)
        else:
            pass

    # 从页面删除项 调用takeItem方法取得行参数 删除某一行
    def deItem(self):
        try:
            # 列表1
            if list_confident == 'boing':
                global songs
                global pic
                global lrcs
                global urls
                self.listwidget.removeItemWidget(self.listwidget.takeItem(num_m))
                del songs[num_m]
                del pic[num_m]
                del lrcs[num_m]
                del urls[num_m]
            # 列表2
            elif list_confident == 'boed':
                global songed
                global picd
                global lrcd
                global urled
                self.listwidget2.removeItemWidget(self.listwidget2.takeItem(num_m))
                del songed[num_m]
                del picd[num_m]
                del lrcd[num_m]
                del urled[num_m]
            # 列表3
            elif list_confident == 'love':
                global loves
                global lovepics
                global lovelrc
                global loveurls
                self.listwidget3.removeItemWidget(self.listwidget3.takeItem(num_m))
                del loves[num_m]
                del lovepics[num_m]
                del lovelrc[num_m]
                del loveurls[num_m]
                self.work = picThread()
                self.work.start()
                self.work.trigger.connect(self.dispng)
            # 列表5
            elif list_confident == 'local':
                global SongPath
                global SongName
                del SongPath[num_m]
                del SongName[num_m]
                self.listwidget5.removeItemWidget(self.listwidget5.takeItem(num_m))
        except:
            pass

    # 当前播放音乐下载
    def down(self):
        if bo == 'local':
            downpath = str(filew)
            downpath = downpath.replace('/', '\\')
            downpath = downpath + SongName[num]
            print(downpath)
            print('explorer /select,{}'.format(downpath))
            call('explorer /select,{}'.format(downpath))
        else:
            call('explorer /select,{}'.format(to))

    # 页数 默认5 pass
    def page(self):
        pass

    # 显示搜索来源
    def print(self, i):
        global type
        print(i)
        if i == 0:
            type = 'kugou'
        elif i == 1:
            type = 'netease'
        elif i == 2:
            type = 'qq'
        elif i == 3:
            type = 'kuwo'

    # 图片格式最大化
    def big(self):
        global big
        print('最大化：{}'.format(big))
        if not big:
            self.setWindowState(Qt.WindowMaximized)
            big = True
        elif big:
            self.setWindowState(Qt.WindowNoState)
            big = False

    # 关闭时对“我喜爱”文件的保存
    def close(self):
        close = True
        try:
            mixer.music.stop()
        except:
            pass
        try:
            rmtree(str(data))
        except Exception as e:
            pass
        filepath = '{}/musicdata'.format(apdata)
        try:
            mkdir(filepath)
        except:
            pass
        print(filepath)
        with open(filepath + "/loves", 'w', encoding='utf-8') as f:
            f.truncate(0)
            f.write(str(loves))
        with open(filepath + "/lovepics", 'w', encoding='utf-8') as f:
            f.truncate(0)
            f.write(str(lovepics))
        with open(filepath + "/loveurls", 'w', encoding='utf-8') as f:
            f.truncate(0)
            f.write(str(loveurls))
        with open(filepath + "/lovelrc", 'w', encoding='utf-8') as f:
            f.truncate(0)
            f.write(str(lovelrc))
        with open(filepath + "/voice", 'w', encoding='utf-8') as f:
            f.truncate(0)
            f.write(str(voice))
        try:
            rmtree(str(data))
        except Exception as e:
            pass
        exit()

    # 窗口最小化
    def mini(self):
        self.showMinimized()



    # 鼠标键盘事件操作 对QWidget进行改进与重写
    # 1.获取鼠标位置 按下
    def mousePressEvent(self, event):
        global big
        big = False
        self.setWindowState(Qt.WindowNoState)
        self.m_flag = True
        self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
        event.accept()

    # 2.更改窗口位置
    def mouseMoveEvent(self, QMouseEvent):
        global big
        big = False
        self.setWindowState(Qt.WindowNoState)
        self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
        QMouseEvent.accept()

    # 3.鼠标释放
    def mouseReleaseEvent(self, QMouseEvent):
        global big
        big = False
        self.setWindowState(Qt.WindowNoState)
        self.m_flag = False

    # 4.关闭 同close
    def closeEvent(self, event):
        close = True
        try:
            mixer.music.stop()
        except:
            pass
        try:
            rmtree(str(data))
        except Exception as e:
            pass
        filepath = '{}/musicdata'.format(apdata)
        try:
            mkdir(filepath)
        except:
            pass
        print(filepath)
        with open(filepath + "/loves", 'w', encoding='utf-8') as f:
            f.truncate(0)
            f.write(str(loves))
        with open(filepath + "/lovepics", 'w', encoding='utf-8') as f:
            f.truncate(0)
            f.write(str(lovepics))
        with open(filepath + "/loveurls", 'w', encoding='utf-8') as f:
            f.truncate(0)
            f.write(str(loveurls))
        with open(filepath + "/lovelrc", 'w', encoding='utf-8') as f:
            f.truncate(0)
            f.write(str(lovelrc))
        with open(filepath + "/voice", 'w', encoding='utf-8') as f:
            f.truncate(0)
            f.write(str(voice))
        exit()

    # 5.键盘事件重写 如enter
    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.modifiers() == Qt.ControlModifier and QKeyEvent.key() == Qt.Key_A:  # 键盘某个键被按下时调用
            print('surpise')



    # 功能
    # 1.启动工作线程，显示GUI初始界面
    def start(self):
        try:
            try:
                self.work = startThread()
                self.work.start()
                self.work.trigger.connect(self.dispng)
            except:
                print('默认图片下载错误')
                pass
            try:
                self.work22 = barThread()
                self.work22.start()
                self.work22.trigger.connect(self.disbar)
            except:
                print('')
        except:
            pass

    # 2.进度条赋值设置
    def disbar(self, apk):
        if apk == 'nofinish':
            print('bar获取失败')
        else:
            try:
                self.right_process_bar.setValue(int(apk))
            except:
                print('bar设置失败')

    # 3.登录加载图片设置与声音设置
    def dispng(self, a):
        # 1.如果是搜索爬取完毕后显示图片
        if a == 'finish':
            pix_img = QPixmap(str(data + '/backdown.png'))
            pix = pix_img.scaled(300, 300, Qt.KeepAspectRatio)
            self.label5.setPixmap(pix)
        # 2.如果是载入我喜欢图片
        elif a == 'login':
            r = 0
            self.listwidget3.clear()
            for i in loves:
                self.listwidget3.addItem(i)
                self.listwidget3.item(r).setForeground(Qt.black)
                r = r + 1
            pass
        # 声音更改完成赋值
        elif a == 'voicedone':
            try:
                mixer.init()
                mixer.music.set_volume(voice)
                k = Decimal(voice).quantize(Decimal('0.00'))
                self.label3.setText('音量：{}'.format(str(k * 100)))
            except:
                pass
        # 3.首次登录显示初始图片
        elif a == 'first':
            try:
                pix_img = QPixmap(str(data + '/first.png'))
                pix = pix_img.scaled(150, 150, Qt.KeepAspectRatio)
                self.label223.setPixmap(pix)
            except:
                pass
        # 4.非首次登录显示以保存图片
        elif a == 'nofirst':
            pix_img = QPixmap(str(data + '/backdown.png'))
            pix = pix_img.scaled(150, 150, Qt.KeepAspectRatio)
            self.label223.setPixmap(pix)
        else:
            print('图片下载错误')

    # 4.爬取内容显示
    # 输入内容
    def correct(self):
        global name
        # 获取输入内容
        seaname = self.shuru.text()
        name = seaname
        print(type)
        print(seaname)
        # 调用爬虫 进行搜索
        self.pa(seaname, type)
    # 调用PAThread类
    def pa(self, name, type, ):
        global tryed
        global paing
        global stop
        self.listwidget.clear()
        self.listwidget.addItem('搜索中')
        self.listwidget.item(0).setForeground(Qt.black)
        try:
            if paing:
                stop = True
                self.listwidget.clear()
                self.work2 = PAThread()
                self.work2.start()
                self.work2.trigger.connect(self.seafinish)
            else:
                self.work2 = PAThread()
                self.work2.start()
                self.work2.trigger.connect(self.seafinish)
        except:
            # 无网络 检查代理
            tryed = tryed + 1
            get_info('https://www.kuaidaili.com/free/inha')
            self.listwidget.addItem('貌似没网了呀`(*>﹏<*)′,再试一遍吧~')
            self.listwidget.item(0).setForeground(Qt.black)
    # pa爬取结果显示
    def seafinish(self, eds):
        global tryed
        try:
            if eds == 'finish':
                self.listwidget.clear()
                if songs == []:
                    self.listwidget.clear()
                    self.listwidget.addItem('歌曲搜索失败，请再试一下其他的软件选项,建议使用酷狗')
                    self.listwidget.item(0).setForeground(Qt.black)
                else:
                    r = 0
                    for i in songs:
                        # self.listwidget.addItem(i)#将文件名添加到listWidget

                        self.listwidget.addItem(i)
                        self.listwidget.item(r).setForeground(Qt.black)
                        r = r + 1
            elif eds == 'clear':
                self.listwidget.clear()
            elif eds == 'nothing':
                self.listwidget.clear()
                self.listwidget.addItem('你输入了个寂寞(*/ω＼*)')
                self.listwidget.item(0).setForeground(Qt.black)

            else:
                print('似乎没网了呀`(*>﹏<*)′')
                self.listwidget.clear()
                self.listwidget.addItem('似乎没网了呀`(*>﹏<*)′')
                self.listwidget.item(0).setForeground(Qt.black)
                print('tryed:{}'.format(tryed))
                tryed = tryed + 1
                get_info('https://www.kuaidaili.com/free/inha')
                print('tryed:{}'.format(tryed))
        except:
            print('完成了，但没有完全完成----列表错误')
            pass
    # blank
    def dis(self):
        pass
    # 本地图片写入并显示 因无本地图片 故=pass
    def photo(self, kind):
        try:
            if kind == 'local':
                audio = File(SongPath[num])
                mArtwork = audio.tags['APIC:'].data
                with open(str(data + '/ls.png'), 'wb') as img:
                    img.write(mArtwork)
            else:
                pass
            try:
                lsfile = str(data + '/ls.png')
                safile = str(data + '/back.png')
                draw(lsfile, safile)

                pix_img = QPixmap(str(data + '/back.png'))
                pix = pix_img.scaled(300, 300, Qt.KeepAspectRatio)
                self.label5.setPixmap(pix)
            except:
                print('图片处理错误')
                pix_img = QPixmap(str(data + '/ls.png'))
                pix = pix_img.scaled(300, 300, Qt.KeepAspectRatio)
                self.label5.setPixmap(pix)
        except:
            print('没有图片')
            try:
                pix_img = QPixmap(str(data + '/backdown.png'))
                pix = pix_img.scaled(300, 300, Qt.KeepAspectRatio)
                self.label5.setPixmap(pix)
            except:
                pass

    # 5.音乐播放模块
    def bofang(self, num, bo):
        print('尝试进行播放')
        try:
            import urllib
            global pause
            global songs
            global music
            global downloading
            downloading = True
            self.console_button_3.setIcon(icon('fa.pause', color='#F76677', font=18))
            pause = False
            try:
                mixer.stop()
            except:
                pass
            # mixer初始化 准备播放音乐
            mixer.init()
            # 计时器
            try:
                self.Timer = QTimer()
                self.Timer.start(500)
            except:
                pass
            # 寻找当前待播放音频
            try:
                self.label.setText('正在寻找文件...')
                # 爬取音频
                self.work = WorkThread()
                # 歌曲音频信息爬取完毕
                self.work.start()
                # 连接播放槽
                self.work.trigger.connect(self.display)
            except:
                print('无法播放，歌曲下载错误')
                downloading = False
                pass

        except:
            sleep(0.1)
            print('播放系统错误')

            pass

    # 将下载的音频通过mixer进行播放 并且更新相应的最近播放和歌词信息
    def display(self, sd):
        global pause
        global songed
        global urled
        global lrcd
        global time_num
        # 此处if会被多个线程同时调用判断 完成多线程并发执行work线程
        if sd == 'finish':
            try:
                # 当前播放歌曲标签文字显示 分为3种 搜索栏中、最近播放、我喜欢（注：本地音频不显示）
                if bo == 'boing':
                    self.label.setText(songs[num])
                elif bo == 'boed':
                    self.label.setText(songed[num])
                elif bo == 'love':
                    self.label.setText(loves[num])
                try:
                    # 加载图片
                    if not picno:
                        pix_img = QPixmap(str(data + '/backdown.png'))
                        pix = pix_img.scaled(300, 300, Qt.KeepAspectRatio)
                        self.label5.setPixmap(pix)
                    else:
                        pix_img = QPixmap(str(data + '/back.png'))
                        pix = pix_img.scaled(300, 300, Qt.KeepAspectRatio)
                        self.label5.setPixmap(pix)

                except:
                    pix_img = QPixmap(str(data + '/backdown.png'))
                    pix = pix_img.scaled(300, 300, Qt.KeepAspectRatio)
                    self.label5.setPixmap(pix)

                # 加载bofang方法调用后的work得到的临时文件即音频所有信息
                print(str(data + '\{}.临时文件'.format(number)))
                mixer.music.load(str(data + '\{}.临时文件'.format(number)))  # 载入音乐
                mixer.music.play()  # 播放
                self.console_button_3.setIcon(icon('fa.pause', color='#F76677', font=18))
                pause = False
                try:
                    mp3 = str(data + '\{}.临时文件'.format(number))
                    xx = load(mp3)
                    time_num = xx.info.time_secs
                    global start
                    start = True
                except:
                    print('MP3错误，播放失败')

                # 播放后进行更新 将已播放的音频载入到最近播放列表（数组）
                if bo == 'boing':
                    songed.append(songs[num])
                    urled.append(urls[num])
                    picd.append(pic[num])
                    lrcd.append(lrcs[num])
                    r = 0
                    self.listwidget2.clear()
                    for i in songed:
                    # 将文件名添加到listWidget
                        self.listwidget2.addItem(i)
                        self.listwidget2.item(r).setForeground(Qt.black)
                        r = r + 1
                else:
                    pass
                # 播放音乐
            except:
                pass
        elif sd == 'nofinish':
            self.label.setText('下载错误')
        # 歌词界面更新 注：由于是多线程 故在爬取完歌曲后会同时发送信号finish，lrcfinish等等多线程进行work
        elif sd == 'lrcfinish':
            r = 0
            self.listwidget4.clear()
            for i in lrct:
                # 将文件名添加到listWidget
                if not i == '\r':
                    self.listwidget4.addItem(i)
                    self.listwidget4.item(r).setForeground(Qt.black)
                    r = r + 1
                else:
                    pass
        # 如果无歌词
        elif sd == 'lrcnofinish':
            self.listwidget4.clear()
            self.listwidget4.addItem('纯音乐，请欣赏')
            self.listwidget4.item(0).setForeground(Qt.black)
        else:
            self.label.setText('加速下载中,已完成{}'.format(sd))


    # 6.播放模式切换与显示 顺序-》随机-》单曲-》顺序
    def playmode(self):
        global play
        try:
            if play == 'shun':
                play = 'sui'
                print('切换到随机播放')
                self.label2.setText("随机播放")
                try:
                    self.console_button_6.setIcon(icon('fa.random', color='black', font=20))
                    print('done')
                except:
                    print('none')
                    pass

            elif play == 'sui':
                play = 'always'
                print('切换到单曲循环')
                self.label2.setText("单曲循环")
                try:
                    self.console_button_6.setIcon(icon('fa.retweet', color='black', font=20))
                    print('done')
                except:
                    print('none')

            elif play == 'always':
                play = 'shun'
                print('切换到顺序播放')
                self.label2.setText("顺序播放")
                try:
                    self.console_button_6.setIcon(icon('fa.align-center', color='black', font=20))
                    print('done')
                except:
                    print('none')

        except:
            print('模式选择错误')
            pass

    # 7. 时刻自动检测歌曲是否已播放完毕 根据不同模式进行选择下一首歌 调用next（）、sui（）、或者本地加载并播放
    def action(self):
        global pause
        xun = 1
        while xun < 2:
            # print ('checking')

            try:
                sleep(1)
                if not mixer.music.get_busy() and pause == False and not downloading and start:
                    if play == 'shun':
                        print('自动下一首（循环播放）')
                        self.next()
                    elif play == 'sui':
                        print('自动下一首（随机播放）')
                        self.sui()
                    elif play == 'always':
                        print('自本一首（单曲循环）')
                        if not bo == 'local':
                            print('本一首（单曲循环）')
                            self.console_button_3.setIcon(icon('fa.pause', color='#F76677', font=18))

                            pause = False

                            mixer.music.load(data + '\{}.临时文件'.format(number))
                            mixer.music.play()
                        else:
                            print('本一首（单曲循环）')
                            self.console_button_3.setIcon(icon('fa.pause', color='#F76677', font=18))

                            pause = False

                            mixer.music.load(SongPath[num])
                            mixer.music.play()

            except:
                try:
                    pass
                except:
                    pass
                pass
        else:
            mixer.music.stop()

    # 8.手动下一首，点击下一首按钮后进行播放下一首歌曲 但由于模式有三种可能 故也分三种情况进行调用next（）、sui（）、或者本地  类似action
    def nextion(self):
        global pause

        try:

            if play == 'shun':
                print('下一首（循环播放）')
                self.next()
            elif play == 'sui':
                print('下一首（随机播放）')
                self.sui()
            elif play == 'always':
                if not bo == 'local':
                    print('本一首（单曲循环）')
                    self.console_button_3.setIcon(icon('fa.pause', color='#F76677', font=18))

                    pause = False

                    mixer.music.load(data + '\{}.临时文件'.format(number))
                    mixer.music.play()
                else:
                    print('本一首（单曲循环）')
                    self.console_button_3.setIcon(icon('fa.pause', color='#F76677', font=18))

                    pause = False

                    mixer.music.load(SongPath[num])
                    mixer.music.play()

        except:
            print('下一首错误')
            pass

    # 9.双击播放 四种情况：搜搜页面，最近播放页面，我喜欢页面，本地页面
    # 9.1. 最近播放
    def change_funcse(self, listwidget):
        global downloading
        global bo
        global stopdown
        global num
        bo = 'boed'
        if downloading:
            try:
                stopdown = True
                print('开始停止搜索')
                downloading = False
                try:
                    global num
                    self.listwidget4.clear()
                    item = QListWidgetItem(self.listwidget.currentItem())
                    print(item.text())
                    # print (item.flags())
                    num = int(listwidget.currentRow())
                    # self.label.setText(wenjianming)#设置标签的文本为音乐的名字
                    self.label.setText(songed[num])
                    print(listwidget.currentRow())
                    self.bofang(num, bo)
                except:
                    downloading = False
                    pass
            except:
                print('stoped downloading')
                downloading = False
                print('根本停不下来')
                pass
        else:
            try:

                self.listwidget4.clear()
                item = QListWidgetItem(self.listwidget.currentItem())
                print(item.text())
                # print (item.flags())
                num = int(listwidget.currentRow())
                # self.label.setText(wenjianming)#设置标签的文本为音乐的名字
                self.label.setText(songed[num])
                print(listwidget.currentRow())
                self.bofang(num, bo)
            except:
                downloading = False
                pass
    # 9.2. 搜索页播放
    def change_func(self, listwidget):
        global downloading
        global bo
        global num
        global stopdown
        bo = 'boing'
        if downloading:
            try:
                try:
                    # 获取当前点击歌曲item
                    item = QListWidgetItem(self.listwidget.currentItem())
                    print(item.text())
                    num = int(listwidget.currentRow())
                    # 设置标签的文本为音乐的名字
                    self.label.setText(songs[num])
                    print(listwidget.currentRow())
                    self.bofang(num, bo)
                except:
                    downloading = False
                    pass
            except:
                print('下载无法停止')
                pass
        else:
            try:
                # 获取当前点击歌曲
                item = QListWidgetItem(self.listwidget.currentItem())
                print(item.text())
                num = int(listwidget.currentRow())
                # 设置标签的文本为音乐的名字
                self.label.setText(songs[num])
                print(listwidget.currentRow())
                self.bofang(num, bo)
            except:
                downloading = False
                pass
    # 9.3. 我喜欢页面播放
    def change_funclove(self, listwidget):
        global downloading
        global bo
        global stopdown
        global num
        bo = 'love'
        if downloading:
            try:
                stopdown = True
                try:
                    global num
                    item = QListWidgetItem(self.listwidget.currentItem())
                    print(item.text())
                    num = int(listwidget.currentRow())
                    # 设置标签的文本为音乐的名字
                    self.label.setText(loves[num])
                    print(listwidget.currentRow())
                    self.bofang(num, bo)
                except:
                    downloading = False
                    pass
            except:
                print('下载无法停止')
                pass
        else:
            try:

                item = QListWidgetItem(self.listwidget.currentItem())
                print(item.text())
                num = int(listwidget.currentRow())
                # 设置标签的文本为音乐的名字
                self.label.setText(loves[num])
                print(listwidget.currentRow())
                self.bofang(num, bo)
            except:
                downloading = False
                pass
    # 9.4. 本地播放 见change方法

    # 10.暂停/继续模块
    def pause(self):
        global pause
        # 继续->暂停
        if pause:
            try:
                mixer.music.unpause()
            except:
                pass
            # 更改图标
            self.console_button_3.setIcon(icon('fa.pause', color='black', font=18))
            pause = False
        else:
            # 暂停->继续
            try:
                mixer.music.pause()
            except:
                pass
            # 更改图标
            self.console_button_3.setIcon(icon('fa.play', color='#F76677', font=18))
            pause = True

    # 11.音量控制与显示更新
    def voiceup(self):
        try:
            print('音量加大')
            global voice
            voice += 0.1
            if voice > 1:
                voice = 1
            # 由mixer进行音量控制
            mixer.music.set_volume(voice)
            k = Decimal(voice).quantize(Decimal('0.00'))
            self.label3.setText('音量：{}'.format(str(k * 100)))
        except:
            pass

    def voicedown(self):
        try:
            print('音量减少')
            global voice
            voice -= 0.1
            if voice < 0:
                voice = 0
            mixer.music.set_volume(voice)
            k = Decimal(voice).quantize(Decimal('0.00'))
            self.label3.setText('音量：{}'.format(str(k * 100)))
        except:
            pass

    # 12.随机播放下一首（改变索引）  跟据当前列表页面（搜索、最近播放、我喜欢、本地）选取下一首歌曲，因各个列表存储歌曲资源不一样
    def sui(self):
        global num
        global songs
        if bo == 'boing':
            q = int(len(songs) - 1)
            num = int(randint(1, q))
        elif bo == 'love':
            q = int(len(loves) - 1)
            num = int(randint(1, q))
        elif bo == 'boed':
            q = int(len(songed) - 1)
            num = int(randint(0, q))
        elif bo == 'local':
            q = int(len(SongPath) - 1)
            num = int(randint(0, q))
        try:
            print('随机播放下一首')
            mixer.init()
            self.Timer = QTimer()
            self.Timer.start(500)
            # self.Timer.timeout.connect(self.timercontorl)#时间函数，与下面的进度条和时间显示有关
            if bo == 'boing':
                self.label.setText(songs[num])
                self.bofang(num, bo)
            elif bo == 'love':
                self.label.setText(loves[num])
                self.bofang(num, bo)
            elif bo == 'boed':
                self.label.setText(songed[num])
                self.bofang(num, bo)
            elif bo == 'local':
                self.label.setText(SongName[num])
                self.bofanglocal()  # 播放音乐

        except:
            pass
    # 12.顺序播放下一首（改变索引）  跟据当前列表页面（搜索、最近播放、我喜欢、本地）选取下一首歌曲，因各个列表存储歌曲资源不一样
    def next(self):
        print('顺序下一首')
        global num
        global songs
        print(bo)
        # 先更新num索引歌曲
        if bo == 'boing':
            if num == len(songs) - 1:
                print('冇')
                num = 0
            else:
                num = num + 1
        elif bo == 'love':
            if num == len(loves) - 1:
                print('冇')
                num = 0
            else:
                num = num + 1
        elif bo == 'boed':
            if num == len(songed) - 1:
                print('冇')
                num = 0
            else:
                num = num + 1
        elif bo == 'local':
            if num == len(SongName) - 1:
                print('冇')
                num = 0
            else:
                num = num + 1
        # 再进行播放
        try:
            if bo == 'boing':
                self.label.setText(songs[num])
                self.bofang(num, bo)
            elif bo == 'love':
                self.label.setText(loves[num])
                self.bofang(num, bo)
            elif bo == 'boed':
                self.label.setText(songed[num])
                self.bofang(num, bo)
            elif bo == 'local':
                self.label.setText(SongName[num])
                self.bofanglocal()
        except:
            print('下一首错误')
            pass
    # 13.单曲循环
    def always(self):
        try:
            # 本地单曲循环
            if bo == 'local':
                self.bofanglocal()
            # 当前歌曲单曲循环
            else:
                global pause
                pause = False
                self.console_button_6.setIcon(icon('fa.retweet', color='black', font=18))
                mixer.music.load(data + '\{}.临时文件'.format(number))
                mixer.music.play()

        except:
            pass
    # 14.上一首（改变索引）
    def last(self):
        global num
        global songs
        if bo == 'boing':
            if num == 0:
                print('冇')
                num = len(songs) - 1
            else:
                num = num - 1
        elif bo == 'love':
            if num == 0:
                print('冇')
                num = len(loves) - 1
            else:
                num = num - 1
        elif bo == 'boed':
            if num == 0:
                print('冇')
                num = len(songed) - 1
            else:
                num = num - 1
        elif bo == 'local':
            if num == 0:
                print('冇')
                num = len(SongName) - 1
            else:
                num = num - 1
        try:
            if bo == 'boing':
                self.label.setText(songs[num])
                self.bofang(num, bo)
            elif bo == 'love':
                self.label.setText(loves[num])
                self.bofang(num, bo)
            elif bo == 'boed':
                self.label.setText(songed[num])
                self.bofang(num, bo)
            elif bo == 'local':
                self.bofanglocal()


        except:
            pass




# 爬取图片圆形展示
def crop_max_square(pil_img): \
        return crop_center(pil_img, min(pil_img.size), min(pil_img.size))


def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def mask_circle_transparent(pil_img, blur_radius, offset=0):
    offset = blur_radius * 2 + offset
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

    result = pil_img.copy()
    result.putalpha(mask)
    return result


def draw(lsfile, safile):
    markImg = Image.open(lsfile)
    thumb_width = 600

    im_square = crop_max_square(markImg).resize((thumb_width, thumb_width), Image.LANCZOS)
    im_thumb = mask_circle_transparent(im_square, 0)
    im_thumb.save(safile)
    remove(lsfile)



# 主程序
def main():
    # 创建Qt对象
    app = QApplication(argv)
    gui = MainUi()
    gui.show()
    exit(app.exec_())


# 爬取错误，代理检测
def get_info(url):
    print('开始获取代理IP地址...')
    print('尝试次数{}'.format(tryed))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/491.10.2623.122 Safari/537.36'
    }
    web_data = get(url, headers=headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ranks = soup.select('#list > table > tbody > tr:nth-child({}) > td:nth-child(1)'.format(str(tryed)))
    titles = soup.select('#list > table > tbody > tr:nth-child({}) > td:nth-child(2)'.format(str(tryed)))
    times = soup.select('#list > table > tbody > tr:nth-child({}) > td:nth-child(6)'.format(str(tryed)))
    for rank, title, time in zip(ranks, titles, times):
        data = {
            'IP': rank.get_text(),
            'duan': title.get_text(),
            'time': time.get_text()
        }
        q = str('http://' + str(rank.get_text()) + '/' + str(title.get_text()))
        proxies = {
            'http': q
        }
        print('代理IP地址：{}'.format(proxies))


if __name__ == '__main__':
    main()

