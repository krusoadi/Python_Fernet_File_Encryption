import threading
from FileCrypto import FileCrypto
import ttkbootstrap as ttk
from tkinter.filedialog import askopenfilename


File = FileCrypto("asd.txt")
root = ttk.Window(themename="darkly")

def update_progress():
    progress.set((File.progress/File.progressMax)*100)
    if File.progress < File.progressMax:
        root.after(500, update_progress)  # update every 500ms

def encrypt_file():
    threading.Thread(target=File.encrypt, args=(10000,), daemon=True).start()
    root.after(500, update_progress)  # Schedule the first progress update

progress = ttk.DoubleVar(root, 0)
progbar = ttk.Progressbar(master=root, variable=progress, maximum=100, style="success")
progbar.pack()

button = ttk.Button(style="success", text="Press", command=encrypt_file)
button.pack()

root.mainloop()