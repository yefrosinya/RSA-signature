import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import RSAAlgorithm

class RSASignature:
    def __init__(self, root):
        self.save_format = None
        self.root = root
        self.root.title("Цифровая подпись RSA")
        self.root.geometry("730x400")

        self.p = tk.StringVar()
        self.q = tk.StringVar()
        self.r = tk.StringVar()
        self.rEuler = tk.StringVar()
        self.e = tk.StringVar()
        self.d = tk.StringVar()

        self.x = tk.StringVar()
        self.y = tk.StringVar()
        self.publicKey = tk.StringVar()
        self.k = tk.StringVar()
        self.eFile = None
        self.dFile = None

        self.createWidgets()

    def createWidgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True)
        paramsFrame = ttk.Frame(notebook)
        notebook.add(paramsFrame, text="Параметры")
        self.setupParamsTab(paramsFrame)
        encryptFrame = ttk.Frame(notebook)
        #notebook.add(encryptFrame, text="Шифрование")
        #self.setupEncryptTab(encryptFrame)
        decryptFrame = ttk.Frame(notebook)
        #notebook.add(decryptFrame, text="Дешифрование")
        #self.setupDecryptTab(decryptFrame)

    def setupParamsTab(self, frame):
        def validate_number_input(new_value):
            return new_value.isdigit() or new_value == ""

        def showTooltip(widget, text):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{widget.winfo_rootx()}+{widget.winfo_rooty() + widget.winfo_height()}")
            label = ttk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1)
            label.pack()
            return tooltip

        vcmd = (frame.register(validate_number_input), '%P')

        ttk.Label(frame, text="Введите простое число p:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        pEntry = ttk.Entry(frame, textvariable=self.p, validate="key", validatecommand=vcmd)
        pEntry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Проверить на простоту",
                  command=lambda: self.checkPrime(self.p.get())).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(frame, text="Введите простое число q:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        qEntry = ttk.Entry(frame, textvariable=self.q, validate="key", validatecommand=vcmd)
        qEntry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Проверить на простоту",
                  command=lambda: self.checkPrime(self.q.get())).grid(row=1, column=2, padx=5, pady=5)

        ttk.Button(frame, text="Посчитать r", command=self.calculateR).grid(row=2, column=1, padx=5, pady=5)

        self.RLabel = ttk.Label(frame, text="")
        self.RLabel.grid(row=3, column=0, padx=5, pady=5, sticky='w')

        ttk.Label(frame, text="Введите e:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        eEntry = ttk.Entry(frame, textvariable=self.e, validate="key", validatecommand=vcmd)
        eEntry.grid(row=4, column=1, padx=5, pady=5)
        eTooltip = None
        def enterE(event):
            nonlocal eTooltip
            eTooltip = showTooltip(eEntry, "1 < e < φ(r), НОД(e, φ(r)) = 1")
        def leaveE(event):
            nonlocal eTooltip
            if eTooltip:
                eTooltip.destroy()
        eEntry.bind("<Enter>", enterE)
        eEntry.bind("<Leave>", leaveE)

        ttk.Button(frame, text="Посчитать d", command=self.calculateD).grid(row=4, column=2, padx=5, pady=5)

        self.enabled = tk.IntVar()

        dCheckbutton = ttk.Checkbutton(frame, text="Показать d", variable=self.enabled)
        dCheckbutton.grid(row=4, column=3, padx=5, pady=5)

        self.DLabel = ttk.Label(frame, text="")
        self.DLabel.grid(row=5, column=1, padx=5, pady=5, sticky='w')

    def checkPrime(self, param_str):
        try:
            param = int(param_str)
            if param < 3:
                messagebox.showwarning("Ошибка", "Введите число больше 2.")
                return
            if RSAAlgorithm.isPrime(param):
                messagebox.showinfo("Проверка на простоту", f"{param} — простое число.")
            else:
                messagebox.showwarning("Проверка на простоту", f"{param} — не является простым.")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное целое число.")

    def calculateR(self):
        try:
            p = int(self.p.get())
            q = int(self.q.get())
            r = p * q
            rEuler = (p - 1) * (q - 1)
            self.RLabel.config(text=f"r = {r}; φ(r) = {rEuler}")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные значения p и q")

    def calculateD(self):
        d = RSAAlgorithm.modinv(int(self.e.get()), int(self.rEuler.get()))
        self.d = d
        if self.enabled.get() == 1:
            self.DLabel.config(text=f"d = {d}")
        return None



if __name__ == "__main__":
    root = tk.Tk()
    app = RSASignature(root)
    root.mainloop()