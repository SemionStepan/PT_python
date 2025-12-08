import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
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

        self.setup_ui()

    def setup_ui(self):
        # Создаем меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Загрузить данные", command=self.load_data)
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

        # Загрузка данных
        ttk.Label(control_frame, text="Данные:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.data_info = ttk.Label(control_frame, text="Не загружены", foreground="red")
        self.data_info.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))

        ttk.Button(control_frame, text="Загрузить из файла",
                   command=self.load_data).grid(row=1, column=0, columnspan=2, pady=(0, 10))

        # Количество интервалов
        ttk.Label(control_frame, text="Количество интервалов:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.interval_var = tk.StringVar(value="7")
        interval_spin = ttk.Spinbox(control_frame, from_=3, to=20, textvariable=self.interval_var, width=10)
        interval_spin.grid(row=2, column=1, pady=5)

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
            ("Полный анализ", self.full_analysis)
        ]

        for i, (text, command) in enumerate(buttons):
            ttk.Button(analysis_frame, text=text, command=command, width=25).pack(pady=3)

        # Информация
        info_frame = ttk.LabelFrame(left_frame, text="Информация", padding="10")
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        info_text = """
        Шаги анализа:
        1. Загрузите данные
        2. Укажите число интервалов
        3. Выберите нужный пункт

        Формулы:
        • h = (x_max - x_min)/k
        • x_mid = (a_i + b_i)/2
        • x_в = Σ(x_mid_i * n_i)/n
        • D_в = Σ((x_mid_i - x_в)² * n_i)/n
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

        # Вкладка для таблицы
        self.table_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.table_frame, text="Таблица данных")

        # Нижняя часть - графики
        self.graph_frame = ttk.LabelFrame(right_frame, text="Графики", padding="10")
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_data(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
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

            self.data_info.config(text=f"n={len(self.data)}", foreground="green")
            self.show_data_table()
            self.display_result(f"Данные успешно загружены!\nОбъем выборки: n = {len(self.data)}\n"
                                f"Диапазон: [{min(self.data):.4f}, {max(self.data):.4f}]\n"
                                f"Размах: R = {max(self.data) - min(self.data):.4f}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {str(e)}")

    def show_data_table(self):
        """Показать таблицу с данными"""
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Создаем Treeview
        columns = ("№", "Значение")
        tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=20)

        # Настраиваем заголовки
        tree.heading("№", text="№")
        tree.heading("Значение", text="Значение")
        tree.column("№", width=50)
        tree.column("Значение", width=150)

        # Добавляем данные
        for i, value in enumerate(self.data, 1):
            tree.insert("", "end", values=(i, f"{value:.6f}"))

        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def calculate_intervals(self):
        """Вычисление интервалов"""
        if self.data is None:
            return False

        try:
            self.n_intervals = int(self.interval_var.get())
            if self.n_intervals < 3:
                messagebox.showwarning("Предупреждение", "Минимальное количество интервалов: 3")
                return False

            data_min = np.min(self.data)
            data_max = np.max(self.data)

            # Длина интервала по формуле Стерджеса (если не задано явно)
            h = (data_max - data_min) / self.n_intervals

            # Создаем границы интервалов
            self.interval_bounds = []
            current = data_min
            for i in range(self.n_intervals + 1):
                self.interval_bounds.append(current)
                current += h

            # Немного расширяем последнюю границу, чтобы включить максимальное значение
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
                    # Если значение равно последней границе
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
        self.text_output.insert(tk.END, text)
        self.notebook.select(0)  # Переключаемся на вкладку с результатами

    def show_interval_series(self):
        """Показать интервальный ряд"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.calculate_intervals():
            return

        text = "ИНТЕРВАЛЬНЫЙ СТАТИСТИЧЕСКИЙ РЯД\n"
        text += "=" * 90 + "\n\n"

        text += f"Количество интервалов: k = {self.n_intervals}\n"
        text += f"Длина интервала: h = {(self.interval_bounds[1] - self.interval_bounds[0]):.6f}\n"
        text += f"Объем выборки: n = {len(self.data)}\n\n"

        text += f"{'№':<4} {'Интервал':<30} {'Середина (x_i)':<20} {'Частота (n_i)':<15} {'Отн. частота (w_i)':<20}\n"
        text += "-" * 90 + "\n"

        cumulative_freq = 0
        cumulative_rel_freq = 0

        for i in range(self.n_intervals):
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
        text += f"{'Итого':<34} {'—':<20} {sum(self.interval_freq):<15} {sum(self.interval_rel_freq):<20.6f}\n\n"

        text += "Кумулятивные частоты:\n"
        text += f"{'№':<4} {'Верхняя граница':<20} {'Накопленная частота':<20} {'Накопленная отн. частота':<25}\n"
        text += "-" * 70 + "\n"

        cum_freq = 0
        cum_rel_freq = 0
        for i in range(self.n_intervals):
            cum_freq += self.interval_freq[i]
            cum_rel_freq += self.interval_rel_freq[i]
            text += f"{i + 1:<4} {self.interval_bounds[i + 1]:<20.4f} {cum_freq:<20} {cum_rel_freq:<25.6f}\n"

        self.display_result(text)

    def show_histograms(self):
        """Построить гистограммы частот и относительных частот"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.calculate_intervals():
            return

        # Очищаем область графиков
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Ширина столбцов
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
        desc += "Гистограмма - ступенчатая фигура, состоящая из прямоугольников.\n"
        desc += "Основания прямоугольников - интервалы значений.\n"
        desc += "Высоты прямоугольников - частоты или относительные частоты.\n"
        desc += f"Площадь гистограммы частот: {sum(self.interval_freq)}\n"
        desc += f"Площадь гистограммы отн. частот: {sum(self.interval_rel_freq):.4f}"

        self.display_result(desc)

    def show_grouped_series(self):
        """Показать группированный ряд"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.calculate_intervals():
            return

        text = "ГРУППИРОВАННЫЙ СТАТИСТИЧЕСКИЙ РЯД\n"
        text += "=" * 70 + "\n\n"
        text += "Группированный ряд представляет значения середин интервалов:\n\n"

        text += f"{'№':<4} {'Середина интервала (x_i)':<25} {'Частота (n_i)':<15} {'Отн. частота (w_i)':<20}\n"
        text += "-" * 70 + "\n"

        for i in range(self.n_intervals):
            text += f"{i + 1:<4} {self.midpoints[i]:<25.6f} "
            text += f"{self.interval_freq[i]:<15} {self.interval_rel_freq[i]:<20.6f}\n"

        text += "-" * 70 + "\n"
        text += f"{'Итого':<29} {sum(self.interval_freq):<15} {sum(self.interval_rel_freq):<20.6f}\n\n"

        text += "Данные для построения полигона:\n"
        text += "• По оси X: середины интервалов (x_i)\n"
        text += "• По оси Y: частоты или относительные частоты"

        self.display_result(text)

    def show_polygons(self):
        """Построить полигоны для группированного ряда"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.calculate_intervals():
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
        ax1.set_title('Полигон частот (группированный ряд)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Добавляем точки
        for x, y in zip(self.midpoints, self.interval_freq):
            ax1.text(x, y, f'({x:.2f}, {y})', fontsize=9, ha='center', va='bottom')

        # Полигон относительных частот
        ax2.plot(self.midpoints, self.interval_rel_freq, 'ro-', linewidth=2, markersize=8)
        ax2.fill_between(self.midpoints, self.interval_rel_freq, alpha=0.3, color='red')
        ax2.set_xlabel('Середины интервалов (x_i)', fontsize=12)
        ax2.set_ylabel('Относительная частота (w_i)', fontsize=12)
        ax2.set_title('Полигон относительных частот (группированный ряд)', fontsize=14, fontweight='bold')
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
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.calculate_intervals():
            return

        # Очищаем область графиков
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Для интервального ряда
        x_points_int = []
        y_points_int = []

        cum_prob = 0
        x_points_int.append(self.interval_bounds[0] - 1)
        y_points_int.append(0)

        for i in range(self.n_intervals):
            x_points_int.append(self.interval_bounds[i])
            y_points_int.append(cum_prob)
            cum_prob += self.interval_rel_freq[i]
            x_points_int.append(self.interval_bounds[i + 1])
            y_points_int.append(cum_prob)

        # Для группированного ряда (используем середины интервалов)
        x_points_group = []
        y_points_group = []

        cum_prob = 0
        x_points_group.append(self.midpoints[0] - (self.interval_bounds[1] - self.interval_bounds[0]))
        y_points_group.append(0)

        for i in range(self.n_intervals):
            x_points_group.append(self.midpoints[i])
            y_points_group.append(cum_prob)
            cum_prob += self.interval_rel_freq[i]
            if i < self.n_intervals - 1:
                next_x = (self.midpoints[i] + self.midpoints[i + 1]) / 2
            else:
                next_x = self.midpoints[i] + (self.interval_bounds[1] - self.interval_bounds[0])
            x_points_group.append(next_x)
            y_points_group.append(cum_prob)

        # График для интервального ряда
        ax1.step(x_points_int, y_points_int, where='post', linewidth=2, color='purple')
        ax1.set_xlabel('x', fontsize=12)
        ax1.set_ylabel('F*(x)', fontsize=12)
        ax1.set_title('Эмпирическая функция (интервальный ряд)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(-0.05, 1.05)

        # График для группированного ряда
        ax2.step(x_points_group, y_points_group, where='post', linewidth=2, color='green')
        ax2.set_xlabel('x', fontsize=12)
        ax2.set_ylabel('F*(x)', fontsize=12)
        ax2.set_title('Эмпирическая функция (группированный ряд)', fontsize=14, fontweight='bold')
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
        text += "Определение: F*(x) = (число вариант, меньших x) / n\n\n"

        text += "Для интервального ряда:\n"
        text += "F*(x) = {\n"
        cum_prob = 0
        for i in range(self.n_intervals):
            if i == 0:
                text += f"    0, при x ≤ {self.interval_bounds[i]:.4f}\n"
            text += f"    {cum_prob:.4f}, при {self.interval_bounds[i]:.4f} < x ≤ {self.interval_bounds[i + 1]:.4f}\n"
            cum_prob += self.interval_rel_freq[i]
        text += f"    1, при x > {self.interval_bounds[-1]:.4f}\n"
        text += "}\n\n"

        text += "Для группированного ряда (по серединам интервалов):\n"
        text += "F*(x) = {\n"
        cum_prob = 0
        for i in range(self.n_intervals):
            if i == 0:
                left_bound = self.midpoints[i] - (self.interval_bounds[1] - self.interval_bounds[0]) / 2
                text += f"    0, при x ≤ {left_bound:.4f}\n"

            right_bound = self.midpoints[i] + (self.interval_bounds[1] - self.interval_bounds[0]) / 2
            if i < self.n_intervals - 1:
                right_bound = (self.midpoints[i] + self.midpoints[i + 1]) / 2

            text += f"    {cum_prob:.4f}, при x ≤ {right_bound:.4f}\n"
            cum_prob += self.interval_rel_freq[i]

        text += f"    1, при x > {right_bound:.4f}\n"
        text += "}"

        self.display_result(text)

    def show_numerical_characteristics(self):
        """Вычислить числовые характеристики выборки"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.calculate_intervals():
            return

        n = len(self.data)

        # Для несгруппированных данных
        x_mean_ungrouped = np.mean(self.data)
        D_v_ungrouped = np.var(self.data, ddof=0)
        sigma_v_ungrouped = np.sqrt(D_v_ungrouped)
        S2_ungrouped = np.var(self.data, ddof=1)
        S_ungrouped = np.sqrt(S2_ungrouped)

        # Для сгруппированных данных (по интервальному ряду)
        # Выборочное среднее: x_в = Σ(x_i * n_i) / n
        x_mean_grouped = np.sum(np.array(self.midpoints) * self.interval_freq) / n

        # Выборочная дисперсия: D_в = Σ((x_i - x_в)² * n_i) / n
        D_v_grouped = np.sum((np.array(self.midpoints) - x_mean_grouped) ** 2 * self.interval_freq) / n
        sigma_v_grouped = np.sqrt(D_v_grouped)

        # Исправленная дисперсия: S² = n/(n-1) * D_в
        S2_grouped = (n / (n - 1)) * D_v_grouped if n > 1 else 0
        S_grouped = np.sqrt(S2_grouped)

        text = "ЧИСЛОВЫЕ ХАРАКТЕРИСТИКИ ВЫБОРКИ\n"
        text += "=" * 80 + "\n\n"

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

        text += "РЕЗУЛЬТАТЫ ДЛЯ НЕСГРУППИРОВАННЫХ ДАННЫХ:\n"
        text += f"• Выборочное среднее: x_в = {x_mean_ungrouped:.6f}\n"
        text += f"• Выборочная дисперсия: D_в = {D_v_ungrouped:.6f}\n"
        text += f"• Выборочное СКО: σ_в = {sigma_v_ungrouped:.6f}\n"
        text += f"• Исправленная дисперсия: S² = {S2_ungrouped:.6f}\n"
        text += f"• Исправленное СКО: S = {S_ungrouped:.6f}\n\n"

        text += "РЕЗУЛЬТАТЫ ДЛЯ ГРУППИРОВАННЫХ ДАННЫХ:\n"
        text += f"• Выборочное среднее: x_в = {x_mean_grouped:.6f}\n"
        text += f"• Выборочная дисперсия: D_в = {D_v_grouped:.6f}\n"
        text += f"• Выборочное СКО: σ_в = {sigma_v_grouped:.6f}\n"
        text += f"• Исправленная дисперсия: S² = {S2_grouped:.6f}\n"
        text += f"• Исправленное СКО: S = {S_grouped:.6f}\n\n"

        # Разница между группированными и несгруппированными
        diff_mean = abs(x_mean_grouped - x_mean_ungrouped)
        diff_D = abs(D_v_grouped - D_v_ungrouped)

        text += "РАЗНИЦА МЕЖДУ ГРУППИРОВАННЫМИ И НЕСГРУППИРОВАННЫМИ:\n"
        text += f"• По среднему: Δx_в = {diff_mean:.6f} ({diff_mean / x_mean_ungrouped * 100:.2f}%)\n"
        text += f"• По дисперсии: ΔD_в = {diff_D:.6f} ({diff_D / D_v_ungrouped * 100:.2f}%)\n\n"

        text += "ДОПОЛНИТЕЛЬНЫЕ ХАРАКТЕРИСТИКИ:\n"
        text += f"• Объем выборки: n = {n}\n"
        text += f"• Размах: R = {max(self.data) - min(self.data):.6f}\n"
        text += f"• Модальный интервал: [{self.interval_bounds[np.argmax(self.interval_freq)]:.4f}; "
        text += f"{self.interval_bounds[np.argmax(self.interval_freq) + 1]:.4f}]\n"
        text += f"• Медиана (приближенно): ≈ {np.median(self.data):.6f}\n"
        text += f"• Коэффициент вариации: V = {(sigma_v_grouped / x_mean_grouped * 100):.2f}%"

        self.display_result(text)

    def full_analysis(self):
        """Выполнить полный анализ"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        # Выполняем все виды анализа последовательно
        self.show_interval_series()
        self.show_histograms()

        # Добавляем информацию о полном анализе
        current_text = self.text_output.get(1.0, tk.END)
        additional_text = "\n\n" + "=" * 80 + "\n"
        additional_text += "ПОЛНЫЙ АНАЛИЗ ВЫПОЛНЕН\n"
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

    def save_report(self):
        """Сохранить полный отчет в файл"""
        if self.data is None:
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
                f.write(f"Объем выборки: n = {len(self.data)}\n")
                f.write(f"Количество интервалов: k = {self.interval_var.get()}\n\n")

                # Исходные данные
                f.write("1. ИСХОДНЫЕ ДАННЫЕ:\n")
                f.write("-" * 40 + "\n")
                for i, val in enumerate(self.data[:50], 1):
                    f.write(f"{val:.4f} ")
                    if i % 10 == 0:
                        f.write("\n")
                if len(self.data) > 50:
                    f.write(f"\n... и еще {len(self.data) - 50} значений\n")
                f.write("\n")

                # Вычисляем интервалы для отчета
                self.calculate_intervals()

                # Интервальный ряд
                f.write("2. ИНТЕРВАЛЬНЫЙ РЯД:\n")
                f.write("-" * 60 + "\n")
                f.write(f"{'Интервал':<30} {'Середина':<12} {'Частота':<10} {'Отн.частота':<12}\n")
                f.write("-" * 60 + "\n")

                for i in range(self.n_intervals):
                    interval_str = f"[{self.interval_bounds[i]:.4f}; {self.interval_bounds[i + 1]:.4f})"
                    if i == self.n_intervals - 1:
                        interval_str = f"[{self.interval_bounds[i]:.4f}; {self.interval_bounds[i + 1]:.4f}]"

                    f.write(f"{interval_str:<30} {self.midpoints[i]:<12.4f} ")
                    f.write(f"{self.interval_freq[i]:<10} {self.interval_rel_freq[i]:<12.6f}\n")
                f.write("\n")

                # Числовые характеристики
                f.write("3. ЧИСЛОВЫЕ ХАРАКТЕРИСТИКИ:\n")
                f.write("-" * 40 + "\n")

                # Вычисляем характеристики
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
                f.write(f"Размах (R): {max(self.data) - min(self.data):.6f}\n")
                f.write(f"Коэффициент вариации (V): {(sigma_v / x_mean * 100):.2f}%\n\n")

                f.write("=" * 80 + "\n")
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
