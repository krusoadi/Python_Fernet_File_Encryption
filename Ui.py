import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from FileCrypto import FileCrypto
from tkinter.filedialog import askopenfilename
from os.path import dirname
import threading


class App(ttk.Window):
    def __init__(self, theme: str = "darkly") -> None:
        super().__init__(themename=theme)
        self.width = 500
        self.height = 600
        self.geometry(f'{self.height}x{self.width}')
        self.title("MyPc")

        self.welcome_frame = WelcomeFrame(self, self.width, self.height)
        self.main_frame = None


class WelcomeFrame(ttk.Frame):
    def __init__(self, master: App, width, height, **kwargs) -> None:
        super().__init__(master, width=width, height=height, **kwargs)
        self.pack(fill=BOTH, expand=YES)

        self.master = master

        self.welcome_text = "MyCryptor"
        self.button = ttk.Button(self, text="Let's Start!", style="info", command=self._start)
        self.main_text = ttk.Label(self, text=self.welcome_text, justify="center", font=('Helvetica', 48, 'bold'))

        ttk.Frame(self).pack(side=TOP, fill=BOTH, expand=YES)  # Top spacer

        self.main_text.pack(anchor="center", pady=10)
        self.button.pack(anchor="center", pady=10)

        ttk.Frame(self).pack(side=BOTTOM, fill=BOTH, expand=YES)  # Bottom spacer

    def _start(self) -> None:
        self.destroy()

    def destroy(self) -> None:
        super().destroy()
        self.master.main_frame = MainFrame(master=self.master, height=self.master.height, width=self.master.width)


class MainFrame(ttk.Frame):
    def __init__(self, master, height, width, **kwargs) -> None:
        super().__init__(master=master, height=height, width=width, **kwargs)
        self.pack(fill=BOTH, expand=YES)
        self.text = "What would you like to do today?"

        self.label = ttk.Label(self, text=self.text, font=('Helvetica', 24, 'bold'))
        self.buttons = ButtonFrame(self)

        ttk.Frame(self).pack(side=TOP, fill=BOTH, expand=YES)  # Top spacer

        self.label.pack(anchor="center", pady=20)  # Label for self.text
        self.buttons.pack(anchor="center", pady=10)  # Label for the two button (encrypt, and decrypt)

        ttk.Frame(self).pack(side=BOTTOM, fill=BOTH, expand=YES)  # Bottom spacer


class ButtonFrame(ttk.Frame):
    def __init__(self, master: MainFrame, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.master = master

        self.encrypt_button = ttk.Button(self, text="Encrypt", command=self._encrypt_button)
        self.decrypt_button = ttk.Button(self, text="Decrypt", command=self._decrypt_button)

        self.encrypt_button.grid(row=0, column=0, padx=10)
        self.decrypt_button.grid(row=0, column=1, padx=10)

    def _encrypt_button(self) -> None:
        self.master.destroy()
        self.master.master.test = EncryptPage(self.master.master)  # TODO delete testing

    def _decrypt_button(self) -> None:
        self.master.destroy()


class WorkPage(ttk.Frame):
    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.progress = ttk.DoubleVar(self, 0)
        self.progressBar = ttk.Progressbar(master=self, variable=self.progress, maximum=10, style="success", length=400)

        self.file_path = ttk.StringVar(self, "", "file_path")
        self.key_path = ttk.StringVar(self, "", "key_path")

        self.file: FileCrypto | None = None

    def update_progress(self):
        self.progress.set((self.file.progress / self.file.progressMax) * 100)
        if self.file.progress < self.file.progressMax:
            self.after(500, self.update_progress)


class EncryptPage(WorkPage):  # TODO reading unit
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill=BOTH, expand=YES)
        self.text = ("Please select the file you would like to encrypt, and the keyfile and the encrypted file\n "
                     "will be generated to that folder")

        self.label = ttk.Label(self, text=self.text, font=('Helvetica', 12, 'bold'))
        self.file_manage = EncryptFileEntry(self)
        self.ready_button = ttk.Button(self, text="Encrypt", command=self._encrypt, style="success")

        self.bottom_space = ttk.Frame(self)  # Bottom spacer

        ttk.Frame(self).pack(side=TOP, fill=BOTH, expand=YES)  # Top spacer

        self.label.pack(anchor="center", pady=10)
        self.file_manage.pack(anchor="center", pady=10)
        self.ready_button.pack(anchor="center", pady=10)

        self.bottom_space.pack(side=BOTTOM, fill=BOTH, expand=YES)  # Bottom Spacer pack

    def _encrypt(self):
        self.file = FileCrypto(self.file_manage.get_file_path(), self.file_manage.get_key_path())
        self.file_manage.destroy()
        self.progress.set(0)

        self.bottom_space.destroy()
        self.progressBar.pack()
        ttk.Frame(self).pack(side=BOTTOM, fill=BOTH, expand=YES)  # Bottom spacer

        threading.Thread(target=self.file.encrypt, args=(100,), daemon=True).start()
        self.after(500, self.update_progress)


class EntryWithBrowse(ttk.Frame):
    def __init__(self, master: EncryptPage, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        self.file_path = ttk.StringVar(self, "", "entry")

        self.entry = ttk.Entry(self, textvariable=self.file_path, width=75)
        self.browse_button = ttk.Button(self, text="Browse", command=self._on_press, style="info")

        self.entry.grid(row=0, column=0, padx=10)
        self.browse_button.grid(row=0, column=1, padx=10)

    def _search_for_file(self):
        self.file_path.set(askopenfilename())

    def _on_press(self):
        self._search_for_file()

    def get_file_path(self):
        return self.file_path.get()


class EncryptFileEntry(EntryWithBrowse):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.key_path = ttk.StringVar(self, "", "key_path")

    def _on_press(self):
        super()._on_press()
        self.key_path.set(dirname(self.file_path.get()) + "/secret.key")

    def get_key_path(self):
        return self.key_path.get()


app = App()
app.mainloop()
