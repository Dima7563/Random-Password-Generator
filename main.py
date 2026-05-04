import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
import string

# Файл для хранения истории
HISTORY_FILE = "password_history.json"


class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # Загрузка истории
        self.history = self.load_history()

        # Переменные для настроек
        self.length_var = tk.IntVar(value=12)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)

        # Создание интерфейса
        self.create_widgets()

        # Обновление таблицы истории
        self.refresh_history_table()

    def create_widgets(self):
        # Рамка настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # Ползунок длины
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.length_scale = tk.Scale(
            settings_frame, from_=4, to=32, orient="horizontal",
            variable=self.length_var, length=200, command=self.on_length_change
        )
        self.length_scale.grid(row=0, column=1, padx=5, pady=5)
        self.length_entry = ttk.Entry(settings_frame, width=5, justify="center")
        self.length_entry.insert(0, "12")
        self.length_entry.bind("<Return>", self.on_length_entry)
        self.length_entry.grid(row=0, column=2, padx=5, pady=5)

        # Чекбоксы
        self.digits_cb = ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits)
        self.digits_cb.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.letters_cb = ttk.Checkbutton(settings_frame, text="Буквы (A-Z, a-z)", variable=self.use_letters)
        self.letters_cb.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self.symbols_cb = ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$%^&*()_+=-[]{}|;:,.<>?/~)", variable=self.use_symbols)
        self.symbols_cb.grid(row=1, column=2, sticky="w", padx=5, pady=2)

        # Кнопка генерации
        self.generate_btn = ttk.Button(settings_frame, text="Сгенерировать пароль", command=self.generate_password)
        self.generate_btn.grid(row=2, column=0, columnspan=3, pady=10)

        # Отображение сгенерированного пароля
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(settings_frame, textvariable=self.password_var, font=("Courier", 12), width=40)
        self.password_entry.grid(row=3, column=0, columnspan=3, pady=5)

        # Кнопка копирования
        self.copy_btn = ttk.Button(settings_frame, text="Копировать в буфер", command=self.copy_to_clipboard)
        self.copy_btn.grid(row=4, column=0, columnspan=3, pady=5)

        # Рамка истории
        history_frame = ttk.LabelFrame(self.root, text="История паролей", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Таблица истории (колонки: пароль, длина, дата/время)
        columns = ("password", "length", "timestamp")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)
        self.history_tree.heading("password", text="Пароль")
        self.history_tree.heading("length", text="Длина")
        self.history_tree.heading("timestamp", text="Дата/время")
        self.history_tree.column("password", width=250)
        self.history_tree.column("length", width=60)
        self.history_tree.column("timestamp", width=150)

        scroll_y = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scroll_y.set)
        self.history_tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Кнопки управления историей
        btn_frame = ttk.Frame(history_frame)
        btn_frame.pack(pady=5)
        self.save_btn = ttk.Button(btn_frame, text="Сохранить историю в JSON", command=self.save_history_to_file)
        self.save_btn.pack(side="left", padx=5)
        self.load_btn = ttk.Button(btn_frame, text="Загрузить историю из JSON", command=self.load_history_from_file)
        self.load_btn.pack(side="left", padx=5)
        self.clear_btn = ttk.Button(btn_frame, text="Очистить историю", command=self.clear_history)
        self.clear_btn.pack(side="left", padx=5)

        # Статусная строка
        self.status_label = ttk.Label(self.root, text="Готов", relief="sunken", anchor="w")
        self.status_label.pack(fill="x", padx=10, pady=5)

    # Обработчики длины
    def on_length_change(self, value):
        self.length_entry.delete(0, tk.END)
        self.length_entry.insert(0, str(int(float(value))))

    def on_length_entry(self, event):
        try:
            new_len = int(self.length_entry.get())
            if new_len < 4:
                new_len = 4
            elif new_len > 32:
                new_len = 32
            self.length_var.set(new_len)
            self.length_scale.set(new_len)
            self.length_entry.delete(0, tk.END)
            self.length_entry.insert(0, str(new_len))
        except ValueError:
            current = self.length_var.get()
            self.length_entry.delete(0, tk.END)
            self.length_entry.insert(0, str(current))

    # Генерация пароля
    def generate_password(self):
        length = self.length_var.get()
        chars = ""
        if self.use_letters.get():
            chars += string.ascii_letters
        if self.use_digits.get():
            chars += string.digits
        if self.use_symbols.get():
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?/~"

        if not chars:
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return

        # Генерация с использованием random (как требуется в задании)
        password_chars = [random.choice(chars) for _ in range(length)]
        # Для улучшения случайности перемешаем
        random.shuffle(password_chars)
        password = "".join(password_chars)

        self.password_var.set(password)
        self.status_label.config(text="Пароль сгенерирован")

        # Добавление в историю
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({
            "password": password,
            "length": length,
            "timestamp": timestamp
        })
        self.save_history_to_file()  # автоматическое сохранение
        self.refresh_history_table()

    def copy_to_clipboard(self):
        pwd = self.password_var.get()
        if not pwd:
            self.status_label.config(text="Нечего копировать")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(pwd)
        self.root.update()
        self.status_label.config(text="Пароль скопирован в буфер обмена")
        self.root.after(2000, lambda: self.status_label.config(text="Готов"))

    # Работа с историей
    def refresh_history_table(self):
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        for entry in reversed(self.history):  # показываем последние сверху
            self.history_tree.insert("", tk.END, values=(entry["password"], entry["length"], entry["timestamp"]))

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_history_to_file(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
            self.status_label.config(text="История сохранена")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

    def load_history_from_file(self):
        if not os.path.exists(HISTORY_FILE):
            messagebox.showwarning("Загрузка", "Файл истории не найден.")
            return
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                self.history = json.load(f)
            self.refresh_history_table()
            self.status_label.config(text="История загружена")
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Вы действительно хотите очистить всю историю?"):
            self.history = []
            self.save_history_to_file()
            self.refresh_history_table()
            self.status_label.config(text="История очищена")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()