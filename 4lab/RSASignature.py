import tkinter as tk
from inspect import signature
from tkinter import filedialog, messagebox, ttk
import RSAAlgorithm

class RSASignature:
    def __init__(self, root):
        self.save_format = None
        self.root = root
        self.root.title("Цифровая подпись RSA")
        self.root.geometry("670x370")

        self.p = tk.StringVar()
        self.q = tk.StringVar()
        self.r = tk.StringVar()
        self.rEuler = tk.StringVar()
        self.e = tk.StringVar()
        self.d = tk.StringVar()
        self.File = None
        self.h =tk.StringVar()
        self.S = tk.StringVar()

        self.createWidgets()

    def createWidgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True)
        paramsFrame = ttk.Frame(notebook)
        notebook.add(paramsFrame, text="Параметры")
        self.setupParamsTab(paramsFrame)
        signatureFrame = ttk.Frame(notebook)
        notebook.add(signatureFrame, text="Подпись")
        self.setupSignatureTab(signatureFrame)

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
        dCheckbutton.grid(row=5, column=2, padx=5, pady=5)

        self.DLabel = ttk.Label(frame, text="")
        self.DLabel.grid(row=5, column=1, padx=5, pady=5, sticky='w')

    def setupSignatureTab(self, frame):
        ttk.Label(frame, text="Файл:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Button(frame, text="Выбрать файл", command=self.selectEncryptFile).grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(frame, text="Подписать", command=self.signFile).grid(row=3, column=0, columnspan=3, pady=10)

        ttk.Label(frame, text="Исходный текст:").grid(row=4, column=0, padx=2, pady=5, sticky='w')
        ttk.Label(frame, text="Хэш-сообщение:").grid(row=4, column=2, padx=2, pady=5, sticky='w')

        textsFrame = tk.Frame(frame)
        textsFrame.grid(row=5, column=0, columnspan=6, padx=5, pady=5, sticky="ew")

        plainFrame = tk.Frame(textsFrame)
        plainFrame.pack(side="left", fill="both", expand=True)

        plainScroll = tk.Scrollbar(plainFrame, orient="vertical")
        self.plainText = tk.Text(plainFrame, height=10, width=40, state='disabled', yscrollcommand=plainScroll.set)
        plainScroll.config(command=self.plainText.yview)

        self.plainText.pack(side="left", fill="both", expand=True)
        plainScroll.pack(side="right", fill="y")

        hashFrame = tk.Frame(textsFrame)
        hashFrame.pack(side="right", fill="both", expand=True)

        hashScroll = tk.Scrollbar(hashFrame, orient="vertical")
        self.hashText = tk.Text(hashFrame, height=10, width=40, state='disabled',
                                   yscrollcommand=hashScroll.set)
        hashScroll.config(command=self.hashText.yview)

        self.hashText.pack(side="left", fill="both", expand=True)
        hashScroll.pack(side="right", fill="y")

        self.ResultLabel = ttk.Label(frame, text="")
        self.ResultLabel.grid(row=6, column=0, padx=5, pady=5, sticky='w')

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
            reuler = (p - 1) * (q - 1)
            self.RLabel.config(text=f"r = {r}; φ(r) = {reuler}")
            self.r.set(r)
            self.rEuler.set(reuler)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные значения p и q")

    def calculateD(self):
        e = int(self.e.get())
        euler = int(self.rEuler.get())
        if 1 > e:
            messagebox.showwarning("Ошибка", "e должно быть больше 1 < φ(r)")
            self.e.set("")
        elif e > euler:
            messagebox.showwarning("Ошибка", "e должно быть меньше φ(r)")
            self.e.set("")
        elif RSAAlgorithm.greatestCommonDivisor(e, euler) != 1:
            messagebox.showwarning("Ошибка", "НОД(e, φ(r)) = 1")
            self.e.set("")
        else:
            d = RSAAlgorithm.modinv(e, euler)
            self.d.set(str(d))
            if self.enabled.get() == 1:
                self.DLabel.config(text=f"d = {d}")

    def selectEncryptFile(self):
        filepath = filedialog.askopenfilename(title="Выбрать файл")
        if not filepath:
            return

        self.File = filepath
        self.plainText.configure(state='normal')
        self.plainText.delete("1.0", tk.END)

        try:
            with open(filepath, 'rb') as f:
                content = f.read()

                if len(content) > 10240:
                    first_part = ' '.join(map(str, content[:150]))
                    last_part = ' '.join(map(str, content[-150:]))
                    display_content = f"{first_part}\n...\n{last_part}"
                    self.plainText.insert(tk.END,
                                          f"Файл слишком большой. Показаны первые и последние 150 байт:\n{display_content}")
                else:
                    self.plainText.insert(tk.END, ' '.join(map(str, content)))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")
        finally:
            self.plainText.configure(state='disabled')


    def signFile(self):
        if not self.File:
            return

        try:
            with open(self.File, 'rb') as f:
                plaintext = f.read()

            n = int(self.p.get()) * int(self.q.get())
            h = 100
            hashMessage = []
            for byte in plaintext:
                result = pow(h + byte, 2, n)
                h  = result
                hashMessage.append(result)
            self.h.set(h)
            self.S = str(pow(h, int(self.d.get()), int(self.r.get())))
            self.ResultLabel.config(text=f"h(M) = {h}; S = {self.S}")
            self.hashText.configure(state='normal')
            self.hashText.delete("1.0", tk.END)
            self.hashText.insert(tk.END, " ".join(map(str, hashMessage)))
            self.hashText.configure(state='disabled')
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = RSASignature(root)
    root.mainloop()