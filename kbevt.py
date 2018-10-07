# -*- coding:utf-8 -*-

import platform
import collections
import win32api
import win32con

# alpha and num
KB_VK_A = 65
KB_VK_B = 66
KB_VK_C = 67
KB_VK_D = 68
KB_VK_E = 69
KB_VK_F = 70
KB_VK_G = 71
KB_VK_H = 72
KB_VK_I = 73
KB_VK_J = 74
KB_VK_K = 75
KB_VK_L = 76
KB_VK_M = 77
KB_VK_N = 78
KB_VK_O = 79
KB_VK_P = 80
KB_VK_Q = 81
KB_VK_R = 82
KB_VK_S = 83
KB_VK_T = 84
KB_VK_U = 85
KB_VK_V = 86
KB_VK_W = 87
KB_VK_X = 88
KB_VK_Y = 89
KB_VK_Z = 90
KB_VK_0 = 48
KB_VK_1 = 49
KB_VK_2 = 50
KB_VK_3 = 51
KB_VK_4 = 52
KB_VK_5 = 53
KB_VK_6 = 54
KB_VK_7 = 55
KB_VK_8 = 56
KB_VK_9 = 57

# numpad
KB_VK_NUMPAD_0 = 96
KB_VK_NUMPAD_1 = 97
KB_VK_NUMPAD_2 = 98
KB_VK_NUMPAD_3 = 99
KB_VK_NUMPAD_4 = 100
KB_VK_NUMPAD_5 = 101
KB_VK_NUMPAD_6 = 102
KB_VK_NUMPAD_7 = 103
KB_VK_NUMPAD_8 = 104
KB_VK_NUMPAD_9 = 105
KB_VK_NUMPAD_MUL = 106
KB_VK_NUMPAD_PLUS = 107
KB_VK_NUMPAD_ENTER = 108
KB_VK_NUMPAD_MINUS = 109
KB_VK_NUMPAD_DOT = 110
KB_VK_NUMPAD_DIV = 111

# Func
KB_VK_F1 = 112
KB_VK_F2 = 113
KB_VK_F3 = 114
KB_VK_F4 = 115
KB_VK_F5 = 116
KB_VK_F6 = 117
KB_VK_F7 = 118
KB_VK_F8 = 119
KB_VK_F9 = 120
KB_VK_F10 = 121
KB_VK_F11 = 122
KB_VK_F12 = 123

# Other
KB_VK_LBUTTON = 1  # mouse left button
KB_VK_RBUTTON = 2
KB_VK_MBUTTON = 4
KB_VK_BACKSPACE = 8
KB_VK_TAB = 9
KB_VK_CLEAR = 12
KB_VK_ENTER = 13
KB_VK_SHIFT = 16
KB_VK_CONTROL = 17
KB_VK_ALT = 18
KB_VK_CAPS_LOCK = 20
KB_VK_ESC = 27
KB_VK_SPACE = 32
KB_VK_PAGE_UP = 33
KB_VK_PAGE_DOWN = 34
KB_VK_END = 35
KB_VK_HOME = 36
KB_VK_LEFT_ARROW = 37
KB_VK_UP_ARROW = 38
KB_VK_RIGHT_ARROW = 39
KB_VK_DOWN_ARROW = 40
KB_VK_INSERT = 45
KB_VK_DELETE = 46
KB_VK_HELP = 47
KB_VK_NUM_LOCK = 144

# extra
KB_VK_LWIN = 91
KB_VK_RWIN = 92
KB_VK_APPS = 93  # windows key??
KB_VK_SCROLL = 145
KB_VK_LSHIFT = 160
KB_VK_RSHIFT = 161
KB_VK_LCONTROL = 162
KB_VK_RCONTROL = 163

KB_VK_VOK_MUTE = 173
KB_VK_VOL_DOWN = 174
KB_VK_VOL_UP = 175


if "windows" != platform.system().lower():
    raise RuntimeError("Not supported platform, only Windows allow")


def winapi_key_up(vk_code):
    return win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)


def winapi_key_down(vk_code):
    return win32api.keybd_event(vk_code, 0, 0, 0)


def winapi_serial_key_down(*args):
    for each in args:
        winapi_key_down(each)


def winapi_serial_key_up(*args):
    for each in args:
        winapi_key_up(each)


def winapi_serial_key_input(*args):
    dq = collections.deque()
    for each in args:
        winapi_key_down(each)
        dq.appendleft(each)
    for each in dq:
        winapi_key_up(each)


if __name__ == '__main__':

    print("Hello")
    winapi_serial_key_input(KB_VK_LCONTROL, KB_VK_LSHIFT, KB_VK_ESC)
