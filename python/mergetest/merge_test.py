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
# print(GetDimensions())

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
# print(GetDisplaysInfo())

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
# ScreenshotAllDisplays().show()

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
# ScreenshotDisplay(1).show()

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
        builder=pyocr.builders.WordBoxBuilder(tesseract_layout=3), # WordBoxBuilder LineBoxBuilder
    )
    return wordBox

if __name__ == "__main__":
    ocrTools = GetOcrTools()
    displaysInfo = GetDisplaysInfo()
    sc = ScreenshotDisplay(1,displaysInfo)
    sc_draw = ImageDraw.Draw(sc)
    wordBoxes = GetWordBoxes(sc, *ocrTools)
    array_box = np.array([t.position for t in wordBoxes])
    for xyxy in array_box:
        sc_draw.rectangle(
            xyxy.ravel().tolist(), outline=(0, 255, 0), width=3
        )
    sc.show()
    print()