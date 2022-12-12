import tkinter

root = tkinter.Tk()
root.title("Slalom Splitter")


title = tkinter.Label(root, text="Slalom Splitter", font=('Arial 18'))
title.grid(row=1, column=2, columnspan=4)

def add_files_clicked():
    pass
add_files_button = tkinter.Button(root, text="Select Files", command=add_files_clicked)
add_files_button.grid(row=1, column=1)

files_listbox = tkinter.Listbox(root, width=35)
files_listbox.grid(row=2, column=1)
files_listbox.insert(1, "Clip1.mp4 - No splits")
files_listbox.insert(1, "Clip2.mp4 - 2:43 - 14 gates")

video_frame = tkinter.Frame(root, width=1280, height=720, bg="white")
video_frame.grid(row=2, column=2, columnspan=4)


def publish_clicked():
    print("publish_clicked")
publish_button = tkinter.Button(root, text="Publish", command=publish_clicked, state="disabled")
publish_button.grid(row=3, column=1)

def start_clicked():
    print("start_clicked")
start_button = tkinter.Button(root, text="Start Video", command=start_clicked, state="disabled")
start_button.grid(row=3, column=2)

def gate_clicked():
    print("gate_clicked")
gate_button = tkinter.Button(root, text="Gate\ns", command=gate_clicked, state="disabled")
gate_button.grid(row=3, column=3)

def touch_clicked():
    print("touch_clicked")
touch_button = tkinter.Button(root, text="Touch +2s\nd", command=touch_clicked, state="disabled")
touch_button.grid(row=3, column=4)

def miss_clicked():
    print("miss_clicked")
miss_button = tkinter.Button(root, text="Miss +50s\nf", command=miss_clicked, state="disabled")
miss_button.grid(row=3, column=5)

def run_complete_clicked():
    print("run_complete_clicked")
run_complete = tkinter.Button(root, text="Run Complete", command=run_complete_clicked, state="disabled")
run_complete.grid(row=3, column=6)

splits_display = tkinter.Text(root, width=20, state="disabled")
splits_display.grid(row=2, column=6)

# Setup keybindings
def keydown(e):
    keybinds = {
        "s": gate_clicked,
        "d": touch_clicked,
        "f": miss_clicked,
    }
    if e.char in keybinds:
        keybinds[e.char]()
root.bind("<KeyPress>", keydown)



def add_padding(container, padx='3m', pady='3m'):
    nc, nr = container.grid_size()
    for i in range(nc):
        container.grid_columnconfigure(i, pad=padx)
    for i in range(nr):
        container.grid_rowconfigure(i, pad=pady)
add_padding(root)


root.resizable(False, False)
root.mainloop()