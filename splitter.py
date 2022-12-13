import tkinter
import tkinter.filedialog
from pathlib import Path
import vlc
import ctypes


try:
    x11 = ctypes.cdll.LoadLibrary('libX11.so')
    x11.XInitThreads()
except:
    print("Warning: failed to XInitThreads()")


class SlalomSplitter(object):
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("Slalom Splitter")

        self.vlc = vlc.Instance()
        self.player = self.vlc.media_player_new()

        self.filenames = []
        self.previous_selection = None

        self.title = tkinter.Label(self.root, text="Slalom Splitter", font=('Arial 18'))
        self.title.grid(row=1, column=2, columnspan=4)

        self.publish_button = tkinter.Button(self.root, text="Publish", command=self.publish_clicked, state="disabled")
        self.publish_button.grid(row=3, column=1)

        self.add_files_button = tkinter.Button(self.root, text="Select Files", command=self.add_files_clicked)
        self.add_files_button.grid(row=1, column=1)

        self.files_listbox = tkinter.Listbox(self.root, width=35, selectmode="SINGLE")
        self.files_listbox.grid(row=2, column=1)
        self.files_listbox.bind('<<ListboxSelect>>', self.video_selected)

        self.video_frame = tkinter.Frame(self.root, width=1280, height=720, bg="white")
        self.video_frame.grid(row=2, column=2, columnspan=4)

        self.play_pause_button = tkinter.Button(self.root, text="Play Video", command=self.play_pause, state="disabled")
        self.play_pause_button.grid(row=3, column=2)

        self.gate_button = tkinter.Button(self.root, text="Gate\n(s)", command=self.gate_clicked, state="disabled")
        self.gate_button.grid(row=3, column=3)

        self.touch_button = tkinter.Button(self.root, text="Touch +2s\n(d)", command=self.touch_clicked, state="disabled")
        self.touch_button.grid(row=3, column=4)

        self.miss_button = tkinter.Button(self.root, text="Miss +50s\n(f)", command=self.miss_clicked, state="disabled")
        self.miss_button.grid(row=3, column=5)

        self.keybinds = {
            "s": (self.gate_clicked, self.gate_button),
            "d": (self.touch_clicked, self.touch_button),
            "f": (self.miss_clicked, self.miss_button),
        }

        self.run_complete = tkinter.Button(self.root, text="Run Complete", command=self.run_complete_clicked, state="disabled")
        self.run_complete.grid(row=3, column=6)

        self.splits_display = tkinter.Text(self.root, width=20, state="disabled")
        self.splits_display.grid(row=2, column=6)

        self.root.bind("<KeyPress>", self.keydown)
        self.add_padding()
        self.root.resizable(False, False)
        self.root.mainloop()

    def add_files_clicked(self):
        files = tkinter.filedialog.askopenfilenames()
        self.filenames = [Path(f) for f in files]

        self.files_listbox.delete(0, 'end')

        for file in self.filenames:
            self.files_listbox.insert(0, f"{file.stem} - No splits")

        if self.filenames:
            self.files_listbox.activate(0)
        self.add_files_button["state"] = "disabled"

    def video_selected(self, e):
        selection = self.files_listbox.curselection()
        if not selection or self.previous_selection == selection:
            return
        self.previous_selection = selection

        file = self.filenames[selection[0]]
        self.media = self.vlc.media_new(file)
        self.player.set_xwindow(self.video_frame.winfo_id())
        self.player.set_media(self.media)

        self.play_pause_button["state"] = "active"

    def publish_clicked(self):
        print("publish_clicked")

    def play_pause(self):
        if self.player.is_playing():
            self.play_pause_button["text"] = "Play Video"
            self.player.set_pause(1)
            self.gate_button["state"] = "disabled"
            self.touch_button["state"] = "disabled"
            self.miss_button["state"] = "disabled"
        else:
            self.play_pause_button["text"] = "Pause Video"
            self.player.play()
            self.gate_button["state"] = "active"
            self.touch_button["state"] = "active"
            self.miss_button["state"] = "active"
            self.run_complete["state"] = "active"

    def gate_clicked(self):
        print("gate_clicked")

    def touch_clicked(self):
        print("touch_clicked")

    def miss_clicked(self):
        print("miss_clicked")

    def run_complete_clicked(self):
        print("run_complete_clicked")

    def keydown(self, e):
        # Setup keybindings
        if e.char in self.keybinds:
            func, button = self.keybinds[e.char]
            if button["state"] == "active":
                func()

    def add_padding(self, padx='3m', pady='3m'):
        nc, nr = self.root.grid_size()
        for i in range(nc):
            self.root.grid_columnconfigure(i, pad=padx)
        for i in range(nr):
            self.root.grid_rowconfigure(i, pad=pady)


if __name__ == '__main__':
    splitter = SlalomSplitter()
