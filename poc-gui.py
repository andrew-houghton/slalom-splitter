import vlc
import tkinter

import ctypes
try:
    x11 = ctypes.cdll.LoadLibrary('libX11.so')
    x11.XInitThreads()
except:
    print("Warning: failed to XInitThreads()")

root = tkinter.Tk()

frame = tkinter.Frame(root, width=1920, height=1080)
frame.pack()

display = tkinter.Frame(frame, bd=5)
display.place(relwidth=1, relheight=1)

Instance = vlc.Instance()
player = Instance.media_player_new()
Media = Instance.media_new('clips/2022-12-12 Bradys slalom/GH010708.MP4')
player.set_xwindow(display.winfo_id())
player.set_media(Media)
player.play()


def keydown(e):
    print('down', e.char, player.get_time())
root.bind("<KeyPress>", keydown)

root.mainloop()