import ctypes
import json
import sys
import tkinter
import tkinter.filedialog
from pathlib import Path

import vlc

try:
    x11 = ctypes.cdll.LoadLibrary("libX11.so")
    x11.XInitThreads()
except:
    print("Warning: failed to XInitThreads()")


class SlalomSplitter(object):
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("Slalom Splitter")

        self.vlc = vlc.Instance()
        self.player = self.vlc.media_player_new()

        self.splits = {}

        self.filenames = []
        self.previous_selection = None

        self.title = tkinter.Label(self.root, text="Slalom Splitter", font=("Arial 18"))
        self.title.grid(row=1, column=2, columnspan=4)

        self.add_files_button = tkinter.Button(
            self.root, text="Select Files", command=self.add_files_clicked
        )
        self.add_files_button.grid(row=1, column=1)

        self.files_listbox = tkinter.Listbox(self.root, width=35, selectmode="SINGLE")
        self.files_listbox.grid(row=2, column=1)
        self.files_listbox.bind("<<ListboxSelect>>", self.video_selected)

        self.video_frame = tkinter.Frame(self.root, width=1280, height=720, bg="white")
        self.video_frame.grid(row=2, column=2, columnspan=4)

        self.play_pause_button = tkinter.Button(
            self.root, text="Play Video", command=self.play_pause, state="disabled"
        )
        self.play_pause_button.grid(row=3, column=2)

        self.gate_button = tkinter.Button(
            self.root, text="Gate\n(s)", command=self.gate_clicked, state="disabled"
        )
        self.gate_button.grid(row=3, column=3)

        self.touch_button = tkinter.Button(
            self.root,
            text="Touch +2s\n(d)",
            command=self.touch_clicked,
            state="disabled",
        )
        self.touch_button.grid(row=3, column=4)

        self.miss_button = tkinter.Button(
            self.root,
            text="Miss +50s\n(f)",
            command=self.miss_clicked,
            state="disabled",
        )
        self.miss_button.grid(row=3, column=5)

        self.keybinds = {
            "s": (self.gate_clicked, self.gate_button),
            "d": (self.touch_clicked, self.touch_button),
            "f": (self.miss_clicked, self.miss_button),
        }

        self.run_complete_button = tkinter.Button(
            self.root, text="Run Complete", command=self.run_complete, state="disabled"
        )
        self.run_complete_button.grid(row=3, column=6)

        self.splits_display = tkinter.Text(self.root, width=20, height=40)
        self.splits_display.grid(row=2, column=6)

        self.root.bind("<KeyPress>", self.keydown)
        self.add_padding()
        self.root.resizable(False, False)
        self.root.mainloop()

    def add_files_clicked(self):
        files = tkinter.filedialog.askopenfilenames()
        self.filenames = [Path(f) for f in files]

        self.files_listbox.delete(0, "end")

        for file in self.filenames:
            self.files_listbox.insert(0, f"{file.stem} - No splits")

        if self.filenames:
            self.files_listbox.activate(0)
        self.add_files_button["state"] = "disabled"

    def get_selected_file(self):
        selection = self.files_listbox.curselection()
        if not selection or self.previous_selection == selection:
            return
        self.previous_selection = selection
        return self.filenames[selection[0]]

    def video_selected(self, e):
        file = self.get_selected_file()
        self.media = self.vlc.media_new(file)
        self.player.set_xwindow(self.video_frame.winfo_id())
        self.player.set_media(self.media)

        self.play_pause_button["state"] = "active"

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
            self.run_complete_button["state"] = "active"

    def store_gate(self, mode, time):
        text = self.splits_display.get("1.0", "end").strip()

        added_text = None
        if text:
            lines = text.split("\n")
            next_gate_number = len(lines) + 1

            previous_gate_time = float(lines[-1].split(" - ")[1].replace("s", ""))
            if time - previous_gate_time < 0.3:
                return

            added_text = f"{next_gate_number: <2} - {str(round(time, 1)) + 's': <6}{f' - +{mode}s' if mode else ''}\n"
        else:
            added_text = f"1  - {time:.1f}s{f' - +{mode}s' if mode else ''}\n"

        self.splits_display.insert("end", added_text)

    def gate_clicked(self):
        self.store_gate(0, self.player.get_time() / 1000)

    def touch_clicked(self):
        self.store_gate(2, self.player.get_time() / 1000)

    def miss_clicked(self):
        self.store_gate(50, self.player.get_time() / 1000)

    def run_complete(self):
        file = self.filenames[self.previous_selection[0]]
        print("run_complete", file)
        self.splits[str(file)] = self.splits_display.get("1.0", "end").strip()
        self.splits_display.delete("1.0", "end")
        self.player.stop()

        # When complete
        if len(self.splits) == len(self.filenames):
            print(json.dumps(self.splits))
            with open(Path(sys.argv[1]), "w") as handle:
                json.dump(self.splits, handle, indent=2)
                self.root.destroy()

    def keydown(self, e):
        # Setup keybindings
        if e.char in self.keybinds:
            func, button = self.keybinds[e.char]
            if button["state"] == "active":
                func()

    def add_padding(self, padx="3m", pady="3m"):
        nc, nr = self.root.grid_size()
        for i in range(nc):
            self.root.grid_columnconfigure(i, pad=padx)
        for i in range(nr):
            self.root.grid_rowconfigure(i, pad=pady)


if __name__ == "__main__":
    assert sys.argv[
        1
    ], "A destination json file path as second arg is required. eg. python splitter.py splits.json"
    splitter = SlalomSplitter()
