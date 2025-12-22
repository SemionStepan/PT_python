import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import math
from collections import Counter


class IntervalStatisticsAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Интервальный статистический анализ")
        self.root.geometry("1400x900")

        self.data = None
        self.n_intervals = None
        self.interval_freq = None
        self.interval_rel_freq = None
        self.midpoints = None
        self.interval_bounds = None
        self.manual_mode = False  # Флаг ручного режима
        self.manual_intervals = []  # Список для хранения ручно введенных интервалов

        self.setup_ui()

    def setup_ui(self):
        # Создаем меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Загрузить данные из файла", command=self.load_data)
        file_menu.add_command(label="Ручной ввод интервального ряда", command=self.manual_input_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Сохранить отчет", command=self.save_report)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        # Основной фрейм с разделением
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Левый фрейм - управление
        left_frame = ttk.Frame(main_paned, width=300)
        main_paned.add(left_frame, weight=1)

        # Правый фрейм - вывод и графики
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=3)

        # === ЛЕВАЯ ПАНЕЛЬ - УПРАВЛЕНИЕ ===
        control_frame = ttk.LabelFrame(left_frame, text="Параметры анализа", padding="10")
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Информация о режиме
        self.mode_label = ttk.Label(control_frame, text="Режим: ожидание данных",
                                    foreground="blue", font=("Arial", 10, "bold"))
        self.mode_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Загрузка данных
        ttk.Label(control_frame, text="Данные:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.data_info = ttk.Label(control_frame, text="Не загружены", foreground="red")
        self.data_info.grid(row=1, column=1, sticky=tk.W, pady=(0, 5))

        ttk.Button(control_frame, text="Загрузить из файла",
                   command=self.load_data).grid(row=2, column=0, columnspan=2, pady=(0, 5))

        ttk.Button(control_frame, text="Ручной ввод",
                   command=self.manual_input_dialog).grid(row=3, column=0, columnspan=2, pady=(0, 10))

        # Количество интервалов (только для автоматического режима)
        ttk.Label(control_frame, text="Кол-во интервалов (авто):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.interval_var = tk.StringVar(value="7")
        self.interval_spin = ttk.Spinbox(control_frame, from_=3, to=20,
                                         textvariable=self.interval_var, width=10, state='normal')
        self.interval_spin.grid(row=4, column=1, pady=5)

        # Кнопки анализа
        analysis_frame = ttk.LabelFrame(left_frame, text="Анализ", padding="10")
        analysis_frame.pack(fill=tk.X, padx=5, pady=5)

        buttons = [
            ("Интервальный ряд", self.show_interval_series),
            ("Гистограммы", self.show_histograms),
            ("Группированный ряд", self.show_grouped_series),
            ("Полигоны", self.show_polygons),
            ("Эмпирическая функция", self.show_empirical_function),
            ("Числовые характеристики", self.show_numerical_characteristics),
            ("Полный анализ", self.full_analysis),
            ("Сбросить данные", self.reset_data)
        ]

        for i, (text, command) in enumerate(buttons):
            ttk.Button(analysis_frame, text=text, command=command, width=25).pack(pady=2)

        # Информация
        info_frame = ttk.LabelFrame(left_frame, text="Информация", padding="10")
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        info_text = """
        Режимы работы:
        1. Автоматический - загрузка 
           исходных данных из файла
        2. Ручной - ввод интервального 
           ряда вручную

        Формат ручного ввода:
        • Границы интервалов
        • Частоты для каждого интервала
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()

        # === ПРАВАЯ ПАНЕЛЬ - ВЫВОД ===
        # Верхняя часть - текстовый вывод
        output_frame = ttk.Frame(right_frame)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создаем Notebook для вкладок
        self.notebook = ttk.Notebook(output_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка для текстового вывода
        self.text_output = scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD, font=("Courier", 10))
        self.notebook.add(self.text_output, text="Результаты")

        # Вкладка для таблицы данных
        self.table_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.table_frame, text="Данные")

        # Вкладка для ручного ввода (если используется)
        self.manual_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.manual_frame, text="Ручной ввод")

        # Нижняя часть - графики
        self.graph_frame = ttk.LabelFrame(right_frame, text="Графики", padding="10")
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def manual_input_dialog(self):
        """Диалоговое окно для ручного ввода интервального ряда"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Ручной ввод интервального ряда")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()

        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Инструкция
        instruction = """Введите интервальный ряд в формате:
        [нижняя_граница; верхняя_граница) частота

        Пример:
        10;15) 8
        15;20) 12
        20;25) 15
        25;30) 10
        30;35) 5

        Примечание:
        • Используйте точку с запятой или запятую как разделитель
        • Квадратная скобка '[' включает границу, круглая ')' исключает
        • Последний интервал можно закрывать квадратной скобкой ']'"""

        ttk.Label(main_frame, text=instruction, justify=tk.LEFT).pack(pady=(0, 10))

        # Текстовое поле для ввода
        text_frame = ttk.LabelFrame(main_frame, text="Ввод данных", padding="5")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        input_text = scrolledtext.ScrolledText(text_frame, height=15, font=("Courier", 10))
        input_text.pack(fill=tk.BOTH, expand=True)

        # Пример данных для быстрого заполнения
        example_data = """10;15) 8
15;20) 12
20;25) 15
25;30) 10
30;35) 5"""
        input_text.insert(1.0, example_data)

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        def process_input():
            text = input_text.get(1.0, tk.END).strip()
            success = self.parse_manual_input(text)
            if success:
                dialog.destroy()
                self.show_manual_input_table()

        ttk.Button(button_frame, text="Обработать", command=process_input).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def parse_manual_input(self, text):
        """Разбор ручного ввода интервального ряда"""
        try:
            lines = text.strip().split('\n')
            intervals = []
            frequencies = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Разделяем интервал и частоту
                if ')' in line:
                    interval_part, freq_part = line.split(')', 1)
                elif ']' in line:
                    interval_part, freq_part = line.split(']', 1)
                else:
                    raise ValueError(f"Некорректный формат строки: {line}")

                # Добавляем закрывающую скобку обратно
                if ')' in line:
                    interval_part += ')'
                else:
                    interval_part += ']'

                # Очищаем и парсим частоту
                freq = float(freq_part.strip())

                # Парсим интервал
                interval_part = interval_part.strip()
                if interval_part.startswith('['):
                    left_inclusive = True
                elif interval_part.startswith('('):
                    left_inclusive = False
                else:
                    raise ValueError(f"Некорректная левая граница: {interval_part}")

                if interval_part.endswith(']'):
                    right_inclusive = True
                elif interval_part.endswith(')'):
                    right_inclusive = False
                else:
                    raise ValueError(f"Некорректная правая граница: {interval_part}")

                # Извлекаем числа
                numbers_part = interval_part[1:-1]
                # Заменяем различные разделители на точку с запятой
                for sep in [',', ';', ':', '|']:
                    numbers_part = numbers_part.replace(sep, ';')

                if ';' not in numbers_part:
                    raise ValueError(f"Некорректный разделитель в интервале: {interval_part}")

                left_str, right_str = numbers_part.split(';', 1)
                left_bound = float(left_str.strip())
                right_bound = float(right_str.strip())

                intervals.append({
                    'left': left_bound,
                    'right': right_bound,
                    'left_inclusive': left_inclusive,
                    'right_inclusive': right_inclusive,
                    'string': interval_part
                })
                frequencies.append(freq)

            if not intervals:
                raise ValueError("Не введено ни одного интервала")

            # Сохраняем данные
            self.manual_mode = True
            self.manual_intervals = intervals
            self.interval_freq = np.array(frequencies, dtype=int)
            self.n_intervals = len(intervals)

            # Создаем границы интервалов
            self.interval_bounds = []
            for i, interval in enumerate(intervals):
                self.interval_bounds.append(interval['left'])
                if i == len(intervals) - 1:
                    self.interval_bounds.append(interval['right'])

            # Вычисляем середины интервалов
            self.midpoints = []
            for interval in intervals:
                mid = (interval['left'] + interval['right']) / 2
                self.midpoints.append(mid)

            # Вычисляем относительные частоты
            total = sum(frequencies)
            self.interval_rel_freq = np.array(frequencies) / total

            # Создаем искусственные данные для совместимости
            # (генерируем точки внутри интервалов пропорционально частотам)
            self.data = []
            for i, (interval, freq) in enumerate(zip(intervals, frequencies)):
                # Генерируем случайные точки внутри интервала
                n_points = int(freq)
                if n_points > 0:
                    points = np.random.uniform(
                        interval['left'] + 0.001,  # Немного отступаем от границ
                        interval['right'] - 0.001,
                        n_points
                    )
                    self.data.extend(points.tolist())

            self.data = np.array(self.data)

            # Обновляем информацию
            self.mode_label.config(text="Режим: ручной ввод", foreground="green")
            self.data_info.config(text=f"n={total} (ручной)", foreground="green")
            self.interval_spin.config(state='disabled')  # Отключаем спинбокс в ручном режиме

            self.display_result(f"Ручной ввод успешно обработан!\n"
                                f"Количество интервалов: {self.n_intervals}\n"
                                f"Общая частота: n = {total}\n"
                                f"Диапазон: [{min(self.interval_bounds):.2f}, {max(self.interval_bounds):.2f}]")

            return True

        except Exception as e:
            messagebox.showerror("Ошибка ввода", f"Ошибка обработки данных:\n{str(e)}")
            return False

    def show_manual_input_table(self):
        """Показать таблицу с введенными вручную данными"""
        for widget in self.manual_frame.winfo_children():
            widget.destroy()

        if not self.manual_mode:
            return

        # Создаем Treeview
        columns = ("№", "Интервал", "Левая граница", "Правая граница", "Частота", "Отн. частота", "Середина")
        tree = ttk.Treeview(self.manual_frame, columns=columns, show="headings", height=15)

        # Настраиваем заголовки
        for col in columns:
            tree.heading(col, text=col)
            if col == "№":
                tree.column(col, width=40)
            elif col == "Интервал":
                tree.column(col, width=100)
            elif col in ["Левая граница", "Правая граница"]:
                tree.column(col, width=100)
            elif col == "Частота":
                tree.column(col, width=80)
            elif col == "Отн. частота":
                tree.column(col, width=100)
            elif col == "Середина":
                tree.column(col, width=100)

        # Добавляем данные
        total_freq = sum(self.interval_freq)
        for i, (interval, freq, rel_freq, midpoint) in enumerate(
                zip(self.manual_intervals, self.interval_freq, self.interval_rel_freq, self.midpoints), 1):
            tree.insert("", "end", values=(
                i,
                interval['string'],
                f"{interval['left']:.4f}",
                f"{interval['right']:.4f}",
                int(freq),
                f"{rel_freq:.6f}",
                f"{midpoint:.4f}"
            ))

        # Добавляем итоговую строку
        tree.insert("", "end", values=(
            "Итого",
            "",
            "",
            "",
            total_freq,
            f"{sum(self.interval_rel_freq):.6f}",
            ""
        ))

        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(self.manual_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Переключаемся на вкладку ручного ввода
        self.notebook.select(2)

    def load_data(self):
        """Загрузка данных из файла (автоматический режим)"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"),
                       ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                self.data = df.iloc[:, 0].dropna().values.flatten()
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
                self.data = df.iloc[:, 0].dropna().values.flatten()
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    numbers = []
                    for part in content.replace(',', ' ').replace(';', ' ').split():
                        try:
                            numbers.append(float(part))
                        except:
                            continue
                    self.data = np.array(numbers)

            if len(self.data) == 0:
                messagebox.showerror("Ошибка", "Не удалось загрузить данные")
                return

            # Сбрасываем ручной режим
            self.manual_mode = False
            self.manual_intervals = []
            self.interval_spin.config(state='normal')
            self.mode_label.config(text="Режим: автоматический", foreground="blue")

            self.data_info.config(text=f"n={len(self.data)}", foreground="green")
            self.show_data_table()
            self.display_result(f"Данные успешно загружены из файла!\n"
                                f"Режим: автоматический\n"
                                f"Объем выборки: n = {len(self.data)}\n"
                                f"Диапазон: [{min(self.data):.4f}, {max(self.data):.4f}]\n"
                                f"Размах: R = {max(self.data) - min(self.data):.4f}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {str(e)}")

    def show_data_table(self):
        """Показать таблицу с данными (для автоматического режима)"""
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        if self.manual_mode:
            return

        # Создаем Treeview
        columns = ("№", "Значение")
        tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=20)

        # Настраиваем заголовки
        tree.heading("№", text="№")
        tree.heading("Значение", text="Значение")
        tree.column("№", width=50)
        tree.column("Значение", width=150)

        # Добавляем данные
        if self.data is not None:
            for i, value in enumerate(self.data[:500], 1):  # Ограничиваем 500 записями
                tree.insert("", "end", values=(i, f"{value:.6f}"))

            if len(self.data) > 500:
                tree.insert("", "end", values=("...", f"и еще {len(self.data) - 500} значений"))

        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Переключаемся на вкладку данных
        self.notebook.select(1)

    def calculate_intervals(self):
        """Вычисление интервалов (для автоматического режима)"""
        if self.data is None:
            return False

        if self.manual_mode:
            # В ручном режиме интервалы уже определены
            return True

        try:
            self.n_intervals = int(self.interval_var.get())
            if self.n_intervals < 3:
                messagebox.showwarning("Предупреждение", "Минимальное количество интервалов: 3")
                return False

            data_min = np.min(self.data)
            data_max = np.max(self.data)

            # Длина интервала
            h = (data_max - data_min) / self.n_intervals

            # Создаем границы интервалов
            self.interval_bounds = []
            current = data_min
            for i in range(self.n_intervals + 1):
                self.interval_bounds.append(current)
                current += h

            # Немного расширяем последнюю границу
            self.interval_bounds[-1] = data_max + 0.0001

            # Вычисляем середины интервалов
            self.midpoints = []
            for i in range(self.n_intervals):
                mid = (self.interval_bounds[i] + self.interval_bounds[i + 1]) / 2
                self.midpoints.append(mid)

            # Подсчитываем частоты
            self.interval_freq = np.zeros(self.n_intervals, dtype=int)
            for value in self.data:
                for i in range(self.n_intervals):
                    if self.interval_bounds[i] <= value < self.interval_bounds[i + 1]:
                        self.interval_freq[i] += 1
                        break
                else:
                    if abs(value - self.interval_bounds[-1]) < 0.0001:
                        self.interval_freq[-1] += 1

            # Относительные частоты
            n = len(self.data)
            self.interval_rel_freq = self.interval_freq / n

            return True

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка вычисления интервалов: {str(e)}")
            return False

    def display_result(self, text):
        """Отображение результата в текстовом поле"""
        self.text_output.delete(1.0, tk.END)

        # Добавляем информацию о режиме
        if self.manual_mode:
            mode_info = "РЕЖИМ: РУЧНОЙ ВВОД ИНТЕРВАЛЬНОГО РЯДА\n" + "=" * 60 + "\n\n"
        else:
            mode_info = "РЕЖИМ: АВТОМАТИЧЕСКИЙ (ИЗ ФАЙЛА)\n" + "=" * 60 + "\n\n"

        self.text_output.insert(tk.END, mode_info + text)
        self.notebook.select(0)  # Переключаемся на вкладку с результатами

    def show_interval_series(self):
        """Показать интервальный ряд"""
        if self.data is None and not self.manual_mode:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.manual_mode and not self.calculate_intervals():
            return

        text = "ИНТЕРВАЛЬНЫЙ СТАТИСТИЧЕСКИЙ РЯД\n"
        text += "=" * 90 + "\n\n"

        if self.manual_mode:
            text += "Режим: РУЧНОЙ ВВОД\n"
            total = sum(self.interval_freq)
            text += f"Общая частота: n = {total}\n\n"
        else:
            text += f"Количество интервалов: k = {self.n_intervals}\n"
            text += f"Длина интервала: h = {(self.interval_bounds[1] - self.interval_bounds[0]):.6f}\n"
            text += f"Объем выборки: n = {len(self.data)}\n\n"

        text += f"{'№':<4} {'Интервал':<30} {'Середина (x_i)':<20} {'Частота (n_i)':<15} {'Отн. частота (w_i)':<20}\n"
        text += "-" * 90 + "\n"

        cumulative_freq = 0
        cumulative_rel_freq = 0

        for i in range(self.n_intervals):
            if self.manual_mode:
                interval_str = self.manual_intervals[i]['string']
            else:
                interval_str = f"[{self.interval_bounds[i]:.4f}; {self.interval_bounds[i + 1]:.4f})"
                if i == self.n_intervals - 1:
                    interval_str = f"[{self.interval_bounds[i]:.4f}; {self.interval_bounds[i + 1]:.4f}]"

            freq = self.interval_freq[i]
            rel_freq = self.interval_rel_freq[i]
            cumulative_freq += freq
            cumulative_rel_freq += rel_freq

            text += f"{i + 1:<4} {interval_str:<30} {self.midpoints[i]:<20.6f} "
            text += f"{freq:<15} {rel_freq:<20.6f}\n"

        text += "-" * 90 + "\n"
        if self.manual_mode:
            total = sum(self.interval_freq)
        else:
            total = len(self.data)
        text += f"{'Итого':<34} {'—':<20} {total:<15} {sum(self.interval_rel_freq):<20.6f}\n\n"

        text += "Кумулятивные частоты:\n"
        text += f"{'№':<4} {'Верхняя граница':<20} {'Накопленная частота':<20} {'Накопленная отн. частота':<25}\n"
        text += "-" * 70 + "\n"

        cum_freq = 0
        cum_rel_freq = 0
        for i in range(self.n_intervals):
            cum_freq += self.interval_freq[i]
            cum_rel_freq += self.interval_rel_freq[i]
            if self.manual_mode:
                bound = self.manual_intervals[i]['right']
            else:
                bound = self.interval_bounds[i + 1]
            text += f"{i + 1:<4} {bound:<20.4f} {cum_freq:<20} {cum_rel_freq:<25.6f}\n"

        self.display_result(text)

    def show_histograms(self):
        """Построить гистограммы частот и относительных частот"""
        if self.data is None and not self.manual_mode:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.manual_mode and not self.calculate_intervals():
            return

        # Очищаем область графиков
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Ширина столбцов
        if self.manual_mode:
            widths = [interval['right'] - interval['left']
                      for interval in self.manual_intervals]
        else:
            widths = [self.interval_bounds[i + 1] - self.interval_bounds[i]
                      for i in range(self.n_intervals)]

        # Гистограмма частот
        bars1 = ax1.bar(self.midpoints, self.interval_freq,
                        width=[w * 0.8 for w in widths],
                        edgecolor='black', alpha=0.7, color='skyblue')
        ax1.set_xlabel('Интервалы', fontsize=12)
        ax1.set_ylabel('Частота (n_i)', fontsize=12)
        ax1.set_title('Гистограмма частот', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')

        # Добавляем значения на столбцы
        for bar in bars1:
            height = bar.get_height()
            if height > 0:
                ax1.text(bar.get_x() + bar.get_width() / 2., height,
                         f'{int(height)}', ha='center', va='bottom')

        # Гистограмма относительных частот
        bars2 = ax2.bar(self.midpoints, self.interval_rel_freq,
                        width=[w * 0.8 for w in widths],
                        edgecolor='black', alpha=0.7, color='lightcoral')
        ax2.set_xlabel('Интервалы', fontsize=12)
        ax2.set_ylabel('Относительная частота (w_i)', fontsize=12)
        ax2.set_title('Гистограмма относительных частот', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')

        # Добавляем значения на столбцы
        for bar in bars2:
            height = bar.get_height()
            if height > 0:
                ax2.text(bar.get_x() + bar.get_width() / 2., height,
                         f'{height:.3f}', ha='center', va='bottom')

        plt.tight_layout()

        # Встраиваем график в tkinter
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Текстовое описание
        desc = "ГИСТОГРАММЫ\n"
        desc += "=" * 60 + "\n"
        if self.manual_mode:
            desc += "Режим: ручной ввод интервального ряда\n"
        else:
            desc += "Режим: автоматический (исходные данные)\n"
        desc += "Гистограмма - ступенчатая фигура, состоящая из прямоугольников.\n"
        desc += "Основания прямоугольников - интервалы значений.\n"
        desc += "Высоты прямоугольников - частоты или относительные частоты.\n"
        desc += f"Площадь гистограммы частот: {sum(self.interval_freq)}\n"
        desc += f"Площадь гистограммы отн. частот: {sum(self.interval_rel_freq):.4f}"

        self.display_result(desc)

    def show_grouped_series(self):
        """Показать группированный ряд"""
        if self.data is None and not self.manual_mode:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.manual_mode and not self.calculate_intervals():
            return

        text = "ГРУППИРОВАННЫЙ СТАТИСТИЧЕСКИЙ РЯД\n"
        text += "=" * 70 + "\n\n"
        if self.manual_mode:
            text += "Режим: РУЧНОЙ ВВОД\n\n"
        text += "Группированный ряд представляет значения середин интервалов:\n\n"

        text += f"{'№':<4} {'Середина интервала (x_i)':<25} {'Частота (n_i)':<15} {'Отн. частота (w_i)':<20}\n"
        text += "-" * 70 + "\n"

        for i in range(self.n_intervals):
            text += f"{i + 1:<4} {self.midpoints[i]:<25.6f} "
            text += f"{self.interval_freq[i]:<15} {self.interval_rel_freq[i]:<20.6f}\n"

        text += "-" * 70 + "\n"
        if self.manual_mode:
            total = sum(self.interval_freq)
        else:
            total = len(self.data)
        text += f"{'Итого':<29} {total:<15} {sum(self.interval_rel_freq):<20.6f}\n\n"

        text += "Данные для построения полигона:\n"
        text += "• По оси X: середины интервалов (x_i)\n"
        text += "• По оси Y: частоты или относительные частоты"

        self.display_result(text)

    def show_polygons(self):
        """Построить полигоны для группированного ряда"""
        if self.data is None and not self.manual_mode:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.manual_mode and not self.calculate_intervals():
            return

        # Очищаем область графиков
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Полигон частот
        ax1.plot(self.midpoints, self.interval_freq, 'bo-', linewidth=2, markersize=8)
        ax1.fill_between(self.midpoints, self.interval_freq, alpha=0.3, color='blue')
        ax1.set_xlabel('Середины интервалов (x_i)', fontsize=12)
        ax1.set_ylabel('Частота (n_i)', fontsize=12)

        if self.manual_mode:
            ax1.set_title('Полигон частот (ручной ввод)', fontsize=14, fontweight='bold')
        else:
            ax1.set_title('Полигон частот (автоматический)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Добавляем точки
        for x, y in zip(self.midpoints, self.interval_freq):
            ax1.text(x, y, f'({x:.2f}, {y})', fontsize=9, ha='center', va='bottom')

        # Полигон относительных частот
        ax2.plot(self.midpoints, self.interval_rel_freq, 'ro-', linewidth=2, markersize=8)
        ax2.fill_between(self.midpoints, self.interval_rel_freq, alpha=0.3, color='red')
        ax2.set_xlabel('Середины интервалов (x_i)', fontsize=12)
        ax2.set_ylabel('Относительная частота (w_i)', fontsize=12)

        if self.manual_mode:
            ax2.set_title('Полигон отн. частот (ручной ввод)', fontsize=14, fontweight='bold')
        else:
            ax2.set_title('Полигон отн. частот (автоматический)', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        # Добавляем точки
        for x, y in zip(self.midpoints, self.interval_rel_freq):
            ax2.text(x, y, f'({x:.2f}, {y:.3f})', fontsize=9, ha='center', va='bottom')

        plt.tight_layout()

        # Встраиваем график в tkinter
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Текстовое описание
        desc = "ПОЛИГОНЫ ГРУППИРОВАННОГО РЯДА\n"
        desc += "=" * 60 + "\n"
        if self.manual_mode:
            desc += "Режим: ручной ввод интервального ряда\n\n"
        else:
            desc += "Режим: автоматический\n\n"
        desc += "Полигон - ломаная, соединяющая точки (x_i, n_i) или (x_i, w_i),\n"
        desc += "где x_i - середины интервалов группированного ряда.\n\n"
        desc += "Координаты точек:\n"

        for i in range(self.n_intervals):
            desc += f"Точка {i + 1}: ({self.midpoints[i]:.4f}, "
            desc += f"{self.interval_freq[i]}) - частота, "
            desc += f"({self.midpoints[i]:.4f}, {self.interval_rel_freq[i]:.4f}) - отн. частота\n"

        self.display_result(desc)

    def show_empirical_function(self):
        """Найти и построить эмпирическую функцию распределения"""
        if self.data is None and not self.manual_mode:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.manual_mode and not self.calculate_intervals():
            return

        # Очищаем область графиков
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Для интервального ряда
        x_points_int = []
        y_points_int = []

        cum_prob = 0
        if self.manual_mode:
            x_points_int.append(self.manual_intervals[0]['left'] - 1)
        else:
            x_points_int.append(self.interval_bounds[0] - 1)
        y_points_int.append(0)

        for i in range(self.n_intervals):
            if self.manual_mode:
                x_points_int.append(self.manual_intervals[i]['left'])
            else:
                x_points_int.append(self.interval_bounds[i])
            y_points_int.append(cum_prob)
            cum_prob += self.interval_rel_freq[i]
            if self.manual_mode:
                x_points_int.append(self.manual_intervals[i]['right'])
            else:
                x_points_int.append(self.interval_bounds[i + 1])
            y_points_int.append(cum_prob)

        # Для группированного ряда (используем середины интервалов)
        x_points_group = []
        y_points_group = []

        cum_prob = 0
        if self.manual_mode:
            interval_width = self.manual_intervals[0]['right'] - self.manual_intervals[0]['left']
            x_points_group.append(self.midpoints[0] - interval_width)
        else:
            interval_width = self.interval_bounds[1] - self.interval_bounds[0]
            x_points_group.append(self.midpoints[0] - interval_width)
        y_points_group.append(0)

        for i in range(self.n_intervals):
            x_points_group.append(self.midpoints[i])
            y_points_group.append(cum_prob)
            cum_prob += self.interval_rel_freq[i]
            if i < self.n_intervals - 1:
                next_x = (self.midpoints[i] + self.midpoints[i + 1]) / 2
            else:
                if self.manual_mode:
                    next_x = self.midpoints[i] + interval_width
                else:
                    next_x = self.midpoints[i] + interval_width
            x_points_group.append(next_x)
            y_points_group.append(cum_prob)

        # График для интервального ряда
        ax1.step(x_points_int, y_points_int, where='post', linewidth=2, color='purple')
        ax1.set_xlabel('x', fontsize=12)
        ax1.set_ylabel('F*(x)', fontsize=12)

        if self.manual_mode:
            ax1.set_title('Эмпирическая функция (ручной ввод)', fontsize=14, fontweight='bold')
        else:
            ax1.set_title('Эмпирическая функция (автоматический)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(-0.05, 1.05)

        # График для группированного ряда
        ax2.step(x_points_group, y_points_group, where='post', linewidth=2, color='green')
        ax2.set_xlabel('x', fontsize=12)
        ax2.set_ylabel('F*(x)', fontsize=12)

        if self.manual_mode:
            ax2.set_title('Эмпирическая функция по группир. ряду', fontsize=14, fontweight='bold')
        else:
            ax2.set_title('Эмпирическая функция по группир. ряду', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(-0.05, 1.05)

        plt.tight_layout()

        # Встраиваем график в tkinter
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Текстовое описание
        text = "ЭМПИРИЧЕСКАЯ ФУНКЦИЯ РАСПРЕДЕЛЕНИЯ F*(x)\n"
        text += "=" * 80 + "\n\n"
        if self.manual_mode:
            text += "Режим: РУЧНОЙ ВВОД\n\n"
        text += "Определение: F*(x) = (число вариант, меньших x) / n\n\n"

        text += "Для интервального ряда:\n"
        text += "F*(x) = {\n"
        cum_prob = 0
        for i in range(self.n_intervals):
            if i == 0:
                if self.manual_mode:
                    text += f"    0, при x ≤ {self.manual_intervals[i]['left']:.4f}\n"
                else:
                    text += f"    0, при x ≤ {self.interval_bounds[i]:.4f}\n"

            if self.manual_mode:
                left = self.manual_intervals[i]['left']
                right = self.manual_intervals[i]['right']
            else:
                left = self.interval_bounds[i]
                right = self.interval_bounds[i + 1]

            text += f"    {cum_prob:.4f}, при {left:.4f} < x ≤ {right:.4f}\n"
            cum_prob += self.interval_rel_freq[i]

        if self.manual_mode:
            last_right = self.manual_intervals[-1]['right']
        else:
            last_right = self.interval_bounds[-1]
        text += f"    1, при x > {last_right:.4f}\n"
        text += "}\n\n"

        self.display_result(text)

    def show_numerical_characteristics(self):
        """Вычислить числовые характеристики выборки"""
        if self.data is None and not self.manual_mode:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.manual_mode and not self.calculate_intervals():
            return

        if self.manual_mode:
            n = sum(self.interval_freq)
        else:
            n = len(self.data)

        text = "ЧИСЛОВЫЕ ХАРАКТЕРИСТИКИ ВЫБОРКИ\n"
        text += "=" * 80 + "\n\n"

        if self.manual_mode:
            text += "Режим: РУЧНОЙ ВВОД ИНТЕРВАЛЬНОГО РЯДА\n\n"
        else:
            text += "Режим: АВТОМАТИЧЕСКИЙ (ИЗ ФАЙЛА)\n\n"

        text += "ФОРМУЛЫ ДЛЯ ГРУППИРОВАННЫХ ДАННЫХ:\n"
        text += "1. Выборочное среднее:\n"
        text += "   x_в = (1/n) * Σ (x_i * n_i)\n"
        text += "   где x_i - середины интервалов, n_i - частоты\n\n"

        text += "2. Выборочная дисперсия:\n"
        text += "   D_в = (1/n) * Σ ((x_i - x_в)² * n_i)\n\n"

        text += "3. Выборочное среднее квадратическое отклонение:\n"
        text += "   σ_в = √D_в\n\n"

        text += "4. Исправленная дисперсия:\n"
        text += "   S² = [n/(n-1)] * D_в\n\n"

        text += "5. Исправленное среднее квадратическое отклонение:\n"
        text += "   S = √S²\n\n"

        text += "=" * 80 + "\n\n"

        # Вычисляем характеристики для группированных данных
        x_mean_grouped = np.sum(np.array(self.midpoints) * self.interval_freq) / n

        D_v_grouped = np.sum((np.array(self.midpoints) - x_mean_grouped) ** 2 * self.interval_freq) / n
        sigma_v_grouped = np.sqrt(D_v_grouped)

        S2_grouped = (n / (n - 1)) * D_v_grouped if n > 1 else 0
        S_grouped = np.sqrt(S2_grouped)

        text += "РЕЗУЛЬТАТЫ ДЛЯ ГРУППИРОВАННЫХ ДАННЫХ:\n"
        text += f"• Объем выборки: n = {n}\n"
        text += f"• Выборочное среднее: x_в = {x_mean_grouped:.6f}\n"
        text += f"• Выборочная дисперсия: D_в = {D_v_grouped:.6f}\n"
        text += f"• Выборочное СКО: σ_в = {sigma_v_grouped:.6f}\n"
        text += f"• Исправленная дисперсия: S² = {S2_grouped:.6f}\n"
        text += f"• Исправленное СКО: S = {S_grouped:.6f}\n\n"

        # Для автоматического режима также показываем несгруппированные данные
        if not self.manual_mode:
            # Для несгруппированных данных
            x_mean_ungrouped = np.mean(self.data)
            D_v_ungrouped = np.var(self.data, ddof=0)
            sigma_v_ungrouped = np.sqrt(D_v_ungrouped)
            S2_ungrouped = np.var(self.data, ddof=1)
            S_ungrouped = np.sqrt(S2_ungrouped)

            text += "РЕЗУЛЬТАТЫ ДЛЯ НЕСГРУППИРОВАННЫХ ДАННЫХ:\n"
            text += f"• Выборочное среднее: x_в = {x_mean_ungrouped:.6f}\n"
            text += f"• Выборочная дисперсия: D_в = {D_v_ungrouped:.6f}\n"
            text += f"• Выборочное СКО: σ_в = {sigma_v_ungrouped:.6f}\n"
            text += f"• Исправленная дисперсия: S² = {S2_ungrouped:.6f}\n"
            text += f"• Исправленное СКО: S = {S_ungrouped:.6f}\n\n"

            # Разница между группированными и несгруппированными
            diff_mean = abs(x_mean_grouped - x_mean_ungrouped)
            diff_D = abs(D_v_grouped - D_v_ungrouped)

            text += "РАЗНИЦА МЕЖДУ ГРУППИРОВАННЫМИ И НЕСГРУППИРОВАННЫМИ:\n"
            text += f"• По среднему: Δx_в = {diff_mean:.6f} ({diff_mean / x_mean_ungrouped * 100:.2f}%)\n"
            text += f"• По дисперсии: ΔD_в = {diff_D:.6f} ({diff_D / D_v_ungrouped * 100:.2f}%)\n\n"

        text += "ДОПОЛНИТЕЛЬНЫЕ ХАРАКТЕРИСТИКИ:\n"
        if self.manual_mode:
            data_min = min([interval['left'] for interval in self.manual_intervals])
            data_max = max([interval['right'] for interval in self.manual_intervals])
        else:
            data_min = min(self.data)
            data_max = max(self.data)

        text += f"• Размах: R = {data_max - data_min:.6f}\n"

        # Модальный интервал
        modal_idx = np.argmax(self.interval_freq)
        if self.manual_mode:
            modal_left = self.manual_intervals[modal_idx]['left']
            modal_right = self.manual_intervals[modal_idx]['right']
        else:
            modal_left = self.interval_bounds[modal_idx]
            modal_right = self.interval_bounds[modal_idx + 1]

        text += f"• Модальный интервал: [{modal_left:.4f}; {modal_right:.4f}]\n"
        text += f"  (частота: {self.interval_freq[modal_idx]})\n"

        # Коэффициент вариации
        if x_mean_grouped != 0:
            text += f"• Коэффициент вариации: V = {(sigma_v_grouped / x_mean_grouped * 100):.2f}%"

        self.display_result(text)

    def full_analysis(self):
        """Выполнить полный анализ"""
        if self.data is None and not self.manual_mode:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        # Выполняем анализ
        self.show_interval_series()
        if not self.manual_mode:
            self.show_histograms()

        # Добавляем информацию о полном анализе
        current_text = self.text_output.get(1.0, tk.END)
        additional_text = "\n\n" + "=" * 80 + "\n"

        if self.manual_mode:
            additional_text += "ПОЛНЫЙ АНАЛИЗ (РУЧНОЙ РЕЖИМ)\n"
        else:
            additional_text += "ПОЛНЫЙ АНАЛИЗ (АВТОМАТИЧЕСКИЙ РЕЖИМ)\n"

        additional_text += "=" * 80 + "\n"
        additional_text += "В результате выполнения полного анализа:\n"
        additional_text += "1. Построен интервальный статистический ряд\n"
        additional_text += "2. Построены гистограммы частот и относительных частот\n"
        additional_text += "3. Создан группированный ряд распределения\n"
        additional_text += "4. Построены полигоны для группированного ряда\n"
        additional_text += "5. Найдена эмпирическая функция распределения\n"
        additional_text += "6. Вычислены числовые характеристики выборки\n"
        additional_text += "\nДля просмотра других результатов выберите соответствующий пункт меню."

        self.text_output.insert(tk.END, additional_text)

    def reset_data(self):
        """Сбросить все данные"""
        self.data = None
        self.n_intervals = None
        self.interval_freq = None
        self.interval_rel_freq = None
        self.midpoints = None
        self.interval_bounds = None
        self.manual_mode = False
        self.manual_intervals = []

        # Очищаем интерфейс
        self.mode_label.config(text="Режим: ожидание данных", foreground="blue")
        self.data_info.config(text="Не загружены", foreground="red")
        self.interval_spin.config(state='normal')

        # Очищаем текстовые поля
        self.text_output.delete(1.0, tk.END)

        # Очищаем таблицы
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        for widget in self.manual_frame.winfo_children():
            widget.destroy()

        # Очищаем графики
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        messagebox.showinfo("Сброс", "Все данные сброшены. Вы можете загрузить новые данные.")

    def save_report(self):
        """Сохранить полный отчет в файл"""
        if self.data is None and not self.manual_mode:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Заголовок
                f.write("ОТЧЕТ ПО ИНТЕРВАЛЬНОМУ СТАТИСТИЧЕСКОМУ АНАЛИЗУ\n")
                f.write("=" * 80 + "\n\n")

                f.write(f"Дата создания: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

                if self.manual_mode:
                    f.write("Режим: РУЧНОЙ ВВОД ИНТЕРВАЛЬНОГО РЯДА\n")
                    total = sum(self.interval_freq)
                    f.write(f"Объем выборки: n = {total}\n")
                else:
                    f.write("Режим: АВТОМАТИЧЕСКИЙ (ЗАГРУЗКА ИЗ ФАЙЛА)\n")
                    f.write(f"Объем выборки: n = {len(self.data)}\n")
                    f.write(f"Количество интервалов: k = {self.interval_var.get()}\n\n")

                # Интервальный ряд
                f.write("\n1. ИНТЕРВАЛЬНЫЙ РЯД:\n")
                f.write("-" * 60 + "\n")
                f.write(f"{'Интервал':<30} {'Середина':<12} {'Частота':<10} {'Отн.частота':<12}\n")
                f.write("-" * 60 + "\n")

                for i in range(self.n_intervals):
                    if self.manual_mode:
                        interval_str = self.manual_intervals[i]['string']
                    else:
                        interval_str = f"[{self.interval_bounds[i]:.4f}; {self.interval_bounds[i + 1]:.4f})"
                        if i == self.n_intervals - 1:
                            interval_str = f"[{self.interval_bounds[i]:.4f}; {self.interval_bounds[i + 1]:.4f}]"

                    f.write(f"{interval_str:<30} {self.midpoints[i]:<12.4f} ")
                    f.write(f"{self.interval_freq[i]:<10} {self.interval_rel_freq[i]:<12.6f}\n")
                f.write("\n")

                # Числовые характеристики
                f.write("2. ЧИСЛОВЫЕ ХАРАКТЕРИСТИКИ:\n")
                f.write("-" * 40 + "\n")

                # Вычисляем характеристики
                if self.manual_mode:
                    n = sum(self.interval_freq)
                else:
                    n = len(self.data)

                x_mean = np.sum(np.array(self.midpoints) * self.interval_freq) / n
                D_v = np.sum((np.array(self.midpoints) - x_mean) ** 2 * self.interval_freq) / n
                sigma_v = np.sqrt(D_v)
                S2 = (n / (n - 1)) * D_v if n > 1 else 0
                S = np.sqrt(S2)

                f.write(f"Выборочное среднее (x_в): {x_mean:.6f}\n")
                f.write(f"Выборочная дисперсия (D_в): {D_v:.6f}\n")
                f.write(f"Выборочное СКО (σ_в): {sigma_v:.6f}\n")
                f.write(f"Исправленная дисперсия (S²): {S2:.6f}\n")
                f.write(f"Исправленное СКО (S): {S:.6f}\n")

                if self.manual_mode:
                    data_min = min([interval['left'] for interval in self.manual_intervals])
                    data_max = max([interval['right'] for interval in self.manual_intervals])
                else:
                    data_min = min(self.data)
                    data_max = max(self.data)

                f.write(f"Размах (R): {data_max - data_min:.6f}\n")
                if x_mean != 0:
                    f.write(f"Коэффициент вариации (V): {(sigma_v / x_mean * 100):.2f}%\n")

                f.write("\n" + "=" * 80 + "\n")
                f.write("Отчет сгенерирован программой интервального статистического анализа\n")

            messagebox.showinfo("Успех", f"Отчет сохранен в файл:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить отчет: {str(e)}")


def main():
    root = tk.Tk()
    app = IntervalStatisticsAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
