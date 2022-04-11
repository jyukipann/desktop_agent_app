from PIL import Image
from PIL import ImageDraw
from PIL import ImageGrab
import sys
import time
import numpy as np
import pyocr
pyocr.tesseract.TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import pyautogui as pg
import win32con
import win32api
import win32gui
import win32ui
import pywintypes
import socket
from multiprocessing import Process
import asyncio
import json
import pyautogui

def alttab(n= 1):
    pg.keyDown('alt')
    for _ in range(n):
        pg.keyDown('tab')
        pg.keyUp('tab')
    pg.keyUp('alt')

def GetDimensions():
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    return (left, top, width, height)

def GetDisplaysInfo(idRange=6):
    displays = []
    displayMonitors = win32api.EnumDisplayMonitors(None, None)
    displayMonitors_length = len(displayMonitors)
    for i in range(idRange):
        device = win32api.EnumDisplayDevices(None, i);
        try:
            devmode = win32api.EnumDisplaySettingsEx(device.DeviceName,win32con.ENUM_CURRENT_SETTINGS);
            displays.append(devmode)
        except pywintypes.error as e:
            continue
        if displayMonitors_length <= len(displays):
            break
    return displays

def ScreenshotAllDisplays():
    hdesktop = win32gui.GetDesktopWindow()
    left, top, width, height = GetDimensions()

    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)
    mem_dc = img_dc.CreateCompatibleDC()

    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(img_dc, width, height)
    mem_dc.SelectObject(screenshot)
    mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)
    bmpinfo = screenshot.GetInfo()
    bmpstr = screenshot.GetBitmapBits(True)
    image = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1
    )
    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())
    return image

def ScreenshotDisplay(DisplayId=0, displaysInfo=GetDisplaysInfo()):
    hdesktop = win32gui.GetDesktopWindow()
    dInfo = displaysInfo[DisplayId]
    left, top = dInfo.Position_x, dInfo.Position_y
    width, height = dInfo.PelsWidth, dInfo.PelsHeight

    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)
    mem_dc = img_dc.CreateCompatibleDC()

    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(img_dc, width, height)
    mem_dc.SelectObject(screenshot)
    mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)
    bmpinfo = screenshot.GetInfo()
    bmpstr = screenshot.GetBitmapBits(True)
    image = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1
    )
    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())
    return image

def GetOcrTools():
    tools = pyocr.get_available_tools()
    tool = tools[0]
    langs = tool.get_available_languages()
    builder = pyocr.builders.WordBoxBuilder(tesseract_layout=3)
    return tool, langs, builder

def GetWordBoxes(image, tool, langs, builder):
    wordBox = tool.image_to_string(
        image,
        lang="script/Japanese" if "script/Japanese" in langs else "eng",
        builder=builder, # WordBoxBuilder LineBoxBuilder
    )
    return wordBox

class Receiver:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = 62000
        self.ip = "127.0.0.1"
        self.addr = (self.ip,self.port)
        self.socket.bind(self.addr)
        self.socket.getblocking()
        self.is_waiting = False
        self.bytes, self.src_addr = None, None
        self.received_data = None
        self.loop = None
        self.onReceive = []

    async def receive(self):
        self.bytes, self.src_addr = self.socket.recvfrom(4092)
        str_data = self.bytes.decode("utf-8")
        return json.loads(str_data)

    def wait_recive(self):
        self.is_waiting = True
        self.loop = asyncio.get_event_loop()
        while(self.is_waiting):
            self.received_data = self.loop.run_until_complete(self.receive())
            for f,args in self.onReceive:
                f(self.received_data, **args)
            print(f"received : {self.received_data}")

    def stop_waiting(self):
        self.is_waiting = False
        if(self.loop is not None):
            self.loop.close()
        self.socket.close()

class Sender:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = 62000
        self.ip = "127.0.0.1"
        self.addr = (self.ip,self.port)
        self.data = {}

    def send(self):
        json_data = json.dumps(self.data)
        self.socket.sendto(json_data.encode("utf-8"), self.addr)

    def close(self):
        self.socket.close()

def GetDataToSend(region, displayId, displaysInfo, tool, langs, builder):
    image = ScreenshotDisplay(displayId, displaysInfo)
    image = image.crop(region) # region=(left,upper,right,lower)
    wordBoxes = GetWordBoxes(image, tool, langs, builder)
    wordBoxes = np.array([t.position for t in wordBoxes])
    dataDict = {"displayId":displayId, "wordBoxes":wordBoxes}
    return json.dumps(dataDict).encode("utf-8")

def receivedDataToSendData(receivedData, displaysInfo, tool, langs, builder):
    displayId = receivedData["displayId"]
    region = receivedData["region"]
    return GetDataToSend(region, displayId, displaysInfo, tool, langs, builder)

if __name__ == "__main__":
    # print(pyautogui.position()) # クリックは複数画面環境下でも可能っぽい。
    """ udpで送信するデータについて
    JSON形式文字列をバイト変換して送信
    中のデータ形式はdictで、以下のデータが必要になるはず
    * displayId
    * ocr結果(足場の座標(ディスプレイ座標系))
    * 
    """

    """ udpで受信するデータについて
    JSON形式文字列をバイト変換して受信
    中のデータ形式はdictで、以下のデータが必要になるはず
    * displayId
    * キャラ座標(ディスプレイ座標系)
    * ocrする範囲(ディスプレイ座標系)
    """
    ocrTools = GetOcrTools()
    displaysInfo = GetDisplaysInfo()
    receiver = Receiver()
    sender = Sender()
    waitReceive = Process(target=receiver.wait_recive)
    waitReceive.daemon = True
    waitReceive.start()





