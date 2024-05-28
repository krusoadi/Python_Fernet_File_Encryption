import threading
from FileCrypto import FileCrypto
import ttkbootstrap as ttk
from tkinter.filedialog import askopenfilename
from os.path import dirname


class App(ttk.Window):
    def __init__(self, theme: str = "darkly") -> None:
        super().__init__(themename=theme)

        self.title("MyPc")
        self.geometry('1500x1500')
        self.file = None

        self.button = ttk.Button(style="success", text="Encrypt", command=self.encrypt_file)
        self.button.pack()

        self.button = ttk.Button(style="danger", text="Decrypt", command=self.decrypt_file)
        self.button.pack()

        self.progress = ttk.DoubleVar(self, 0)
        self.progressBar = ttk.Progressbar(master=self, variable=self.progress, maximum=10, style="success", length=400)
        self.progressBar.pack()

    def set_file_name(self):
        Filename = askopenfilename()
        Keyfile = dirname(Filename) + "/fernet.key"

        self.file = FileCrypto(Filename, Keyfile)

    def update_progress(self):
        self.progress.set((self.file.progress / self.file.progressMax) * 100)
        if self.file.progress < self.file.progressMax:
            self.after(500, self.update_progress)

    def encrypt_file(self):
        self.progress.set(0)
        self.set_file_name()

        threading.Thread(target=self.file.encrypt, args=(100,), daemon=True).start()
        self.after(500, self.update_progress)

    def decrypt_file(self):
        self.progress.set(0)
        self.set_file_name()

        threading.Thread(target=self.file.decrypt, args=("final.txt",), daemon=True).start()
        self.after(500, self.update_progress)


app = App()

app.mainloop()
