#!/usr/bin/python3
# -*- coding: utf-8 -*-


import pyautogui

if __name__ == '__main__':

    # screenWidth, screenHeight = pyautogui.size()
    # pyautogui.moveTo(screenWidth / 2, screenHeight / 2)

    # pyautogui.keyDown("shift")
    pyautogui.keyDown("command")
    pyautogui.press("tab", interval=0.25)
    pyautogui.keyUp("command")

    pyautogui.typewrite('Hello world!', interval=0.25)
