import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os
import threading
import time
from datetime import datetime
from pin_func import collecting_links_to_pin, collecting_links_to_img, download_img
import sys
from io import StringIO

ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")  

class CaptureOutput:
    def __init__(self, log_callback):
        self.log_callback = log_callback
        self.output = StringIO()

    def __enter__(self):
        sys.stdout = self.output
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = sys.__stdout__
        output = self.output.getvalue().strip()
        if output:
            for line in output.split("\n"):
                self.log_callback(line.strip())
        self.output.close()

class ParserApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PinParse")
        self.geometry("1280x720") 
        self.minsize(600, 500) 
        self.resizable(True, True)  
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Pin\nParse",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 20))

        self.theme_label = ctk.CTkLabel(self.sidebar_frame, text="Тема:", font=ctk.CTkFont(size=14))
        self.theme_label.grid(row=1, column=0, padx=20, pady=(10, 5))
        self.theme_menu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Dark", "Light", "System"],
            command=self.change_theme,
            fg_color="#3B8ED0",
            button_color="#2B6CA3",
            button_hover_color="#1F4C73"
        )
        self.theme_menu.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(10, weight=1)  

        self.label_query = ctk.CTkLabel(
            self.main_frame,
            text="Запрос:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.label_query.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        self.entry_query = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Введите запрос для парсинга",
            width=400,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14)
        )
        self.entry_query.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.label_count = ctk.CTkLabel(
            self.main_frame,
            text="Количество:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.label_count.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        self.entry_count = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Введите количество (число)",
            width=400,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14)
        )
        self.entry_count.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.label_path = ctk.CTkLabel(
            self.main_frame,
            text="Место сохранения:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.label_path.grid(row=4, column=0, padx=20, pady=(10, 5), sticky="w")
        self.path_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.path_frame.grid(row=5, column=0, padx=20, pady=5, sticky="ew")
        self.path_frame.grid_columnconfigure(0, weight=1)
        self.entry_path = ctk.CTkEntry(
            self.path_frame,
            placeholder_text="Выберите папку для сохранения",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14)
        )
        self.entry_path.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.button_browse = ctk.CTkButton(
            self.path_frame,
            text="Обзор",
            width=100,
            height=40,
            corner_radius=10,
            command=self.browse_folder,
            fg_color="#3B8ED0",
            hover_color="#2B6CA3"
        )
        self.button_browse.grid(row=0, column=1)

        self.button_run = ctk.CTkButton(
            self.main_frame,
            text="Запустить",
            command=self.start_parser_thread,
            fg_color="#28A745",
            hover_color="#218838",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.button_run.grid(row=6, column=0, padx=20, pady=20, sticky="ew")

        self.label_progress = ctk.CTkLabel(
            self.main_frame,
            text="Прогресс:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.label_progress.grid(row=7, column=0, padx=20, pady=(10, 5), sticky="w")
        self.progress_bar = ctk.CTkProgressBar(
            self.main_frame,
            width=400,
            height=20,
            corner_radius=10
        )
        self.progress_bar.grid(row=8, column=0, padx=20, pady=5, sticky="ew")
        self.progress_bar.set(0)  

        self.label_logs = ctk.CTkLabel(
            self.main_frame,
            text="Логи:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.label_logs.grid(row=9, column=0, padx=20, pady=(10, 5), sticky="w")
        self.log_textbox = ctk.CTkTextbox(
            self.main_frame,
            height=200,  
            corner_radius=10,
            font=ctk.CTkFont(size=14)
        )
        self.log_textbox.grid(row=10, column=0, padx=20, pady=(5, 20), sticky="nsew")
        self.log_textbox.configure(state="disabled") 

        self.is_running = False

    def browse_folder(self):
        folder_path = filedialog.askdirectory(title="Выберите папку для сохранения")
        if folder_path:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, folder_path)

    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see(tk.END)
        self.update()

    def change_theme(self, theme):
        ctk.set_appearance_mode(theme)
        self.log_message(f"Тема изменена на {theme}")

    def start_parser_thread(self):
        if self.is_running:
            tk.messagebox.showwarning("Предупреждение", "Парсер уже запущен!")
            return
        self.is_running = True
        self.button_run.configure(state="disabled", text="Выполняется...")
        self.progress_bar.set(0)  
        threading.Thread(target=self.run_parser, daemon=True).start()

    def run_parser(self):
        query = self.entry_query.get()
        count = self.entry_count.get()
        path = self.entry_path.get()

        if not query:
            tk.messagebox.showerror("Ошибка", "Введите запрос!")
            self.log_message("Ошибка: Пустой запрос")
            self.is_running = False
            self.button_run.configure(state="normal", text="Запустить")
            return
        if not count.isdigit():
            tk.messagebox.showerror("Ошибка", "Количество должно быть числом!")
            self.log_message("Ошибка: Количество не является числом")
            self.is_running = False
            self.button_run.configure(state="normal", text="Запустить")
            return
        if not os.path.isdir(path):
            tk.messagebox.showerror("Ошибка", "Укажите действительную папку для сохранения!")
            self.log_message("Ошибка: Недействительный путь")
            self.is_running = False
            self.button_run.configure(state="normal", text="Запустить")
            return

        self.log_message(f"Запуск парсера: Запрос='{query}', Количество={count}, Путь={path}")

        try:
            self.log_message("Сбор ссылок на пины...")
            with CaptureOutput(self.log_message):
                collecting_links_to_pin(query, int(count))
            self.log_message("Сбор ссылок на пины завершен")
            self.progress_bar.set(0.333)
            time.sleep(1) 

            self.log_message("Сбор ссылок на изображения...")
            with CaptureOutput(self.log_message):
                collecting_links_to_img()
            self.log_message("Сбор ссылок на изображения завершен")
            self.progress_bar.set(0.666)  
            time.sleep(1) 

            self.log_message("Загрузка изображений...")
            with CaptureOutput(self.log_message):
                download_img(path)
            self.log_message("Загрузка изображений завершена")
            self.progress_bar.set(1.0)  

            self.log_message("Парсер успешно завершил работу")
            tk.messagebox.showinfo("Успех", "Парсинг успешно завершен!")

        except Exception as e:
            self.log_message(f"Ошибка: {str(e)}")
            tk.messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

        finally:
            self.is_running = False
            self.button_run.configure(state="normal", text="Запустить")
            self.progress_bar.set(0) 

if __name__ == "__main__":
    app = ParserApp()
    app.mainloop()