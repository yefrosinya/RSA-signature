import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from src.crypto.rsa_algorithm import RSAAlgorithm
from src.crypto.hash_calculator import HashCalculator
from src.utils.file_manager import FileManager
from src.utils.math_utils import MathUtils

class RSASignatureGUI:
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Цифровая подпись RSA")
        self.root.geometry("670x400")
        
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(lambda: self.root.attributes('-topmost', False))
        
        try:
            self.root.tk.call('wm', 'attributes', '.', '-topmost', True)
            self.root.tk.call('wm', 'attributes', '.', '-topmost', False)
        except:
            pass
        
        self.rsa: Optional[RSAAlgorithm] = None
        self.hash_calculator: Optional[HashCalculator] = None
        
        self.p = tk.StringVar()
        self.q = tk.StringVar()
        self.r = tk.StringVar()
        self.rEuler = tk.StringVar()
        self.e = tk.StringVar()
        self.d = tk.StringVar()
        self.h = tk.StringVar()
        self.S = tk.StringVar()
        
        self.selected_file: Optional[str] = None
        self.save_format = tk.StringVar()
        self.enabled = tk.IntVar()
        
        self.plaintext_bytes: Optional[bytes] = None
        self.sig_bytes: Optional[bytes] = None
        self.hash_message: Optional[list] = None
        
        self.create_widgets()
        
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.root.deiconify()
        self.root.focus_force()
        
        self.root.update()
        self.root.state('normal')
    
    def create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True)
        
        params_frame = ttk.Frame(notebook)
        notebook.add(params_frame, text="Параметры")
        self.setup_params_tab(params_frame)
        
        signature_frame = ttk.Frame(notebook)
        notebook.add(signature_frame, text="Подпись")
        self.setup_signature_tab(signature_frame)
        
        check_frame = ttk.Frame(notebook)
        notebook.add(check_frame, text="Проверка")
        self.setup_check_tab(check_frame)
    
    def setup_params_tab(self, frame: ttk.Frame):
        
        def validate_number_input(new_value: str) -> bool:
            return new_value.isdigit() or new_value == ""
        
        def show_tooltip(widget: tk.Widget, text: str) -> tk.Toplevel:
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{widget.winfo_rootx()}+{widget.winfo_rooty() + widget.winfo_height()}")
            label = ttk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1)
            label.pack()
            return tooltip
        
        vcmd = (frame.register(validate_number_input), '%P')
        
        ttk.Label(frame, text="Введите простое число p:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        p_entry = ttk.Entry(frame, textvariable=self.p, validate="key", validatecommand=vcmd)
        p_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Проверить на простоту",
                  command=lambda: self.check_prime(self.p.get())).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(frame, text="Введите простое число q:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        q_entry = ttk.Entry(frame, textvariable=self.q, validate="key", validatecommand=vcmd)
        q_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Проверить на простоту",
                  command=lambda: self.check_prime(self.q.get())).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Button(frame, text="Посчитать r", command=self.calculate_r).grid(row=2, column=1, padx=5, pady=5)
        
        self.r_label = ttk.Label(frame, text="")
        self.r_label.grid(row=3, column=0, padx=5, pady=5, sticky='w')
        
        ttk.Label(frame, text="Введите e:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        e_entry = ttk.Entry(frame, textvariable=self.e, validate="key", validatecommand=vcmd)
        e_entry.grid(row=4, column=1, padx=5, pady=5)
        
        e_tooltip = None
        def enter_e(event):
            nonlocal e_tooltip
            e_tooltip = show_tooltip(e_entry, "1 < e < φ(r), НОД(e, φ(r)) = 1")
        def leave_e(event):
            nonlocal e_tooltip
            if e_tooltip:
                e_tooltip.destroy()
        e_entry.bind("<Enter>", enter_e)
        e_entry.bind("<Leave>", leave_e)
        
        ttk.Button(frame, text="Посчитать d", command=self.calculate_d).grid(row=4, column=2, padx=5, pady=5)
        
        d_checkbutton = ttk.Checkbutton(frame, text="Показать d", variable=self.enabled)
        d_checkbutton.grid(row=5, column=2, padx=5, pady=5)
        
        self.d_label = ttk.Label(frame, text="")
        self.d_label.grid(row=5, column=1, padx=5, pady=5, sticky='w')
    
    def setup_signature_tab(self, frame: ttk.Frame):
        
        ttk.Label(frame, text="Файл:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Button(frame, text="Выбрать файл", command=lambda: self.select_file(0)).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(frame, text="Подписать", command=self.sign_file).grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Label(frame, text="Исходный текст:").grid(row=4, column=0, padx=2, pady=5, sticky='w')
        ttk.Label(frame, text="Хэш-сообщение:").grid(row=4, column=2, padx=2, pady=5, sticky='w')
        
        texts_frame = tk.Frame(frame)
        texts_frame.grid(row=5, column=0, columnspan=6, padx=5, pady=5, sticky="ew")
        
        plain_frame = tk.Frame(texts_frame)
        plain_frame.pack(side="left", fill="both", expand=True)
        
        plain_scroll = tk.Scrollbar(plain_frame, orient="vertical")
        self.plain_text = tk.Text(plain_frame, height=10, width=40, state='disabled', yscrollcommand=plain_scroll.set)
        plain_scroll.config(command=self.plain_text.yview)
        
        self.plain_text.pack(side="left", fill="both", expand=True)
        plain_scroll.pack(side="right", fill="y")
        
        hash_frame = tk.Frame(texts_frame)
        hash_frame.pack(side="right", fill="both", expand=True)
        
        hash_scroll = tk.Scrollbar(hash_frame, orient="vertical")
        self.hash_text = tk.Text(hash_frame, height=10, width=40, state='disabled',
                                yscrollcommand=hash_scroll.set)
        hash_scroll.config(command=self.hash_text.yview)
        
        self.hash_text.pack(side="left", fill="both", expand=True)
        hash_scroll.pack(side="right", fill="y")
        
        self.result_label = ttk.Label(frame, text="")
        self.result_label.grid(row=6, column=0, padx=5, pady=5, sticky='w')
        
        save_frame = tk.Frame(frame)
        save_frame.grid(row=7, column=0, columnspan=3, pady=10)
        
        ttk.Label(save_frame, text="Сохранить как:").pack(side="left", padx=5)
        
        format_combobox = ttk.Combobox(save_frame, textvariable=self.save_format, values=["txt"],
                                      state='readonly', width=8)
        format_combobox.current(0)
        format_combobox.pack(side="left", padx=5)
        
        ttk.Button(save_frame, text="Сохранить", command=self.save_signed).pack(side="left", padx=5)
    
    def setup_check_tab(self, frame: ttk.Frame):
        
        ttk.Label(frame, text="Файл:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Button(frame, text="Выбрать файл", command=lambda: self.select_file(1)).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(frame, text="Проверить", command=self.check_file).grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Label(frame, text="Сообщение:").grid(row=4, column=0, padx=2, pady=5, sticky='w')
        ttk.Label(frame, text="Проверка:").grid(row=4, column=2, padx=2, pady=5, sticky='w')
        
        texts_frame_sign = tk.Frame(frame)
        texts_frame_sign.grid(row=5, column=0, columnspan=6, padx=5, pady=5, sticky="ew")
        
        plain_frame_sign = tk.Frame(texts_frame_sign)
        plain_frame_sign.pack(side="left", fill="both", expand=True)
        
        plain_scroll_sign = tk.Scrollbar(plain_frame_sign, orient="vertical")
        self.plain_text_sign = tk.Text(plain_frame_sign, height=10, width=40, state='disabled', 
                                      yscrollcommand=plain_scroll_sign.set)
        plain_scroll_sign.config(command=self.plain_text_sign.yview)
        
        self.plain_text_sign.pack(side="left", fill="both", expand=True)
        plain_scroll_sign.pack(side="right", fill="y")
        
        result_frame_sign = tk.Frame(texts_frame_sign)
        result_frame_sign.pack(side="right", fill="both", expand=True)
        
        result_scroll_sign = tk.Scrollbar(result_frame_sign, orient="vertical")
        self.result_text_sign = tk.Text(result_frame_sign, height=10, width=40, state='disabled',
                                       yscrollcommand=result_scroll_sign.set)
        result_scroll_sign.config(command=self.result_text_sign.yview)
        
        self.result_text_sign.pack(side="left", fill="both", expand=True)
        result_scroll_sign.pack(side="right", fill="y")
        
        self.result_label_sign = ttk.Label(frame, text="")
        self.result_label_sign.grid(row=6, column=0, padx=5, pady=5, sticky='w')
    
    def check_prime(self, param_str: str):
        
        try:
            param = int(param_str)
            if param < 3:
                messagebox.showwarning("Ошибка", "Введите число больше 2.")
                return
            if MathUtils.is_prime(param):
                messagebox.showinfo("Проверка на простоту", f"{param} — простое число.")
            else:
                messagebox.showwarning("Проверка на простоту", f"{param} — не является простым.")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное целое число.")
    
    def calculate_r(self):
        
        try:
            p = int(self.p.get())
            q = int(self.q.get())
            r = p * q
            reuler = (p - 1) * (q - 1)
            self.r_label.config(text=f"r = {r}; φ(r) = {reuler}")
            self.r.set(r)
            self.rEuler.set(reuler)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные значения p и q")
    
    def calculate_d(self):
        
        try:
            e = int(self.e.get())
            euler = int(self.rEuler.get())
            
            if e <= 1:
                messagebox.showwarning("Ошибка", "e должно быть больше 1")
                self.e.set("")
            elif e >= euler:
                messagebox.showwarning("Ошибка", "e должно быть меньше φ(r)")
                self.e.set("")
            elif MathUtils.greatest_common_divisor(e, euler) != 1:
                messagebox.showwarning("Ошибка", "НОД(e, φ(r)) != 1")
                self.e.set("")
            else:
                d = MathUtils.mod_inverse(e, euler)
                self.d.set(str(d))
                if self.enabled.get() == 1:
                    self.d_label.config(text=f"d = {d}")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def select_file(self, where: int):
        
        filepath = filedialog.askopenfilename(title="Выбрать файл")
        if not filepath:
            return
        
        self.selected_file = filepath
        
        if where == 0:
            text_widget = self.plain_text
        else:
            text_widget = self.plain_text_sign
        
        text_widget.configure(state='normal')
        text_widget.delete("1.0", tk.END)
        
        try:
            content = FileManager.read_file_bytes(filepath)
            display_content = FileManager.format_file_content_for_display(content)
            text_widget.insert(tk.END, display_content)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")
        finally:
            text_widget.configure(state='disabled')
    
    def sign_file(self):
        
        if not self.selected_file:
            messagebox.showwarning("Ошибка", "Выберите файл для подписи")
            return
        
        try:

            if not all([self.p.get(), self.q.get(), self.e.get(), self.d.get()]):
                messagebox.showwarning("Ошибка", "Сначала задайте все параметры RSA")
                return
            
            p_val = int(self.p.get())
            q_val = int(self.q.get())
            e_val = int(self.e.get())
            
            self.rsa = RSAAlgorithm(p_val, q_val)
            self.rsa.generate_key_pair(e_val)
            
            self.plaintext_bytes = FileManager.read_file_bytes(self.selected_file)
            
            self.hash_calculator = HashCalculator(self.rsa.n)
            
            h, self.hash_message = self.hash_calculator.calculate_hash(self.plaintext_bytes)
            
            signature = self.rsa.sign(h)
            self.S = signature
            
            self.sig_bytes = signature.to_bytes((self.rsa.n.bit_length() + 7) // 8, 'big')
            
            self.h.set(str(h))
            self.result_label.config(text=f"h(M) = {h}; S = {signature}")
            
            self.hash_text.configure(state='normal')
            self.hash_text.delete("1.0", tk.END)
            self.hash_text.insert(tk.END, " ".join(map(str, self.hash_message)))
            self.hash_text.configure(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка подписи: {e}")
    
    def save_signed(self):
        
        if not hasattr(self, 'plaintext_bytes') or not hasattr(self, 'sig_bytes'):
            messagebox.showwarning("Ошибка", "Сначала подпишите файл.")
            return
        
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Signed files", "*.txt")]
        )
        if not path:
            return
        
        try:
            FileManager.save_signed_file(self.selected_file, path, self.S)
            messagebox.showinfo("Успех", "Файл сохранён с подписью!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
    
    def check_file(self):
        
        if not self.selected_file:
            messagebox.showwarning("Ошибка", "Выберите файл для проверки")
            return
        
        try:

            if not all([self.p.get(), self.q.get(), self.d.get()]):
                messagebox.showwarning("Ошибка", "Сначала задайте все параметры RSA")
                return
            
            original_data, signature = FileManager.parse_signed_file(self.selected_file)
            
            p_val = int(self.p.get())
            q_val = int(self.q.get())
            d_val = int(self.d.get())
            
            self.rsa = RSAAlgorithm(p_val, q_val)
            self.rsa.d = d_val  # Устанавливаем закрытый ключ для проверки
            
            self.hash_calculator = HashCalculator(self.rsa.n)
            h, result_hash = self.hash_calculator.calculate_hash_from_string(original_data)
            
            decrypted_hash = self.rsa.decrypt(signature)
            
            self.result_text_sign.configure(state='normal')
            self.result_text_sign.delete("1.0", tk.END)
            self.result_text_sign.insert(tk.END, " ".join(map(str, result_hash)))
            self.result_text_sign.configure(state='disabled')
            
            if h == decrypted_hash:
                messagebox.showinfo("Успех", "Подпись верна!")
                self.result_label_sign.config(text=f"h(M) = {h}; Проверено: {decrypted_hash}")
            else:
                messagebox.showerror("Ошибка", f"Неверная подпись! Хеш: {h} ≠ расшифровано: {decrypted_hash}")
                self.result_label_sign.config(text=f"Хеш: {h} ≠ расшифровано: {decrypted_hash}")
        
        except Exception as e:
            messagebox.showerror("Ошибка проверки", str(e))
