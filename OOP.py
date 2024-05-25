import threading
from FileCrypto import FileCrypto
import ttkbootstrap as ttk
from tkinter.filedialog import askopenfilename
from os.path import dirname


class App(ttk.Window):
    def __init__(self, themename:str ="darkly") -> None:
        super().__init__(themename=themename)
        
        self.title("MyPc")
        self.geometry('1500x1500')
        self.file = None
    
        self.button = ttk.Button(style="success", text="Encrypt", command=self.encrypt_file)
        self.button.pack()

        self.button = ttk.Button(style="danger", text="Decrypt", command=self.decrypt_file)
        self.button.pack()

        self.progress = ttk.DoubleVar(self, 0)
        self.progressBar =ttk.Progressbar(master=self, variable=self.progress, maximum=10, style="success", length=400)
        self.progressBar.pack()

    
                
    def setFileName(self):
        Filename = askopenfilename()
        Keyfile = dirname(Filename) + "/secret.key"
        
        self.file = FileCrypto(Filename, Keyfile)
    
    def update_progress(self):
        self.progress.set((self.file.progress/self.file.progressMax)*100)
        if self.file.progress < self.file.progressMax:
            self.after(500, self.update_progress)  # update every 500ms

    def encrypt_file(self):
        self.progress.set(0)
        self.setFileName()
        
        threading.Thread(target=self.file.encrypt, args=(100,), daemon=True).start()
        self.after(500, self.update_progress)  # Schedule the first progress update
        
    def decrypt_file(self):
        self.progress.set(0)
        self.setFileName()
        
        threading.Thread(target=self.file.decrypt, args=("final.txt",), daemon=True).start()
        self.after(500, self.update_progress)  # Schedule the first progress update
        

app = App()

app.mainloop()