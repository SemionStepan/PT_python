import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import math
from scipy import special
from collections import Counter


class PearsonChiSquareTest:
    def __init__(self, root):
        self.root = root
        self.root.title("Проверка гипотезы о нормальном распределении - Критерий Пирсона")
        self.root.geometry("1400x900")

        self.data = None
        self.n_intervals = None
        self.interval_freq = None
        self.interval_rel_freq = None
        self.midpoints = None
        self.interval_bounds = None
        self.alpha = 0.05  # Уровень значимости по умолчанию

        self.setup_ui()

    def setup_ui(self):
        # Создаем меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Загрузить данные", command=self.load_data)
        file_menu.add_command(label="Ручной ввод интервалов", command=self.manual_input_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Сохранить отчет", command=self.save_report)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        # Основной фрейм с разделением
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Левый фрейм - управление
        left_frame = ttk.Frame(main_paned, width=350)
        main_paned.add(left_frame, weight=1)

        # Правый фрейм - вывод и графики
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=3)

        # === ЛЕВАЯ ПАНЕЛЬ - УПРАВЛЕНИЕ ===
        control_frame = ttk.LabelFrame(left_frame, text="Параметры анализа", padding="10")
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Информация о данных
        ttk.Label(control_frame, text="Данные:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.data_info = ttk.Label(control_frame, text="Не загружены", foreground="red")
        self.data_info.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))

        ttk.Button(control_frame, text="Загрузить из файла",
                   command=self.load_data).grid(row=1, column=0, columnspan=2, pady=(0, 5))

        # Количество интервалов
        ttk.Label(control_frame, text="Количество интервалов:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.interval_var = tk.StringVar(value="7")
        interval_spin = ttk.Spinbox(control_frame, from_=3, to=20,
                                    textvariable=self.interval_var, width=10)
        interval_spin.grid(row=2, column=1, pady=5)

        # Уровень значимости
        ttk.Label(control_frame, text="Уровень значимости α:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.alpha_var = tk.StringVar(value="0.05")
        alpha_combo = ttk.Combobox(control_frame, textvariable=self.alpha_var,
                                   values=["0.01", "0.05", "0.10"], width=8)
        alpha_combo.grid(row=3, column=1, pady=5)

        # Кнопки анализа
        analysis_frame = ttk.LabelFrame(left_frame, text="Анализ", padding="10")
        analysis_frame.pack(fill=tk.X, padx=5, pady=5)

        buttons = [
            ("1-3: Данные и хар-ки", self.show_basic_stats),
            ("4-5: Оценки параметров", self.show_parameter_estimates),
            ("6: Графики сравнения", self.show_comparison_graphs),
            ("7: Теоретические вероятности", self.show_theoretical_probabilities),
            ("8: χ² наблюдаемое", self.show_chi2_observed),
            ("9-11: Проверка гипотезы", self.perform_hypothesis_test),
            ("Полный анализ", self.full_analysis)
        ]

        for i, (text, command) in enumerate(buttons):
            ttk.Button(analysis_frame, text=text, command=command, width=25).pack(pady=2)

        # Информация о критерии Пирсона
        info_frame = ttk.LabelFrame(left_frame, text="Критерий Пирсона", padding="10")
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        info_text = """χ² = Σ[(n_i - np_i)²/(np_i)]

        где:
        n_i - наблюдаемая частота
        p_i - теоретическая вероятность
        n - объем выборки
        k - число интервалов

        Гипотеза H₀: данные имеют
        нормальное распределение"""
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()

        # === ПРАВАЯ ПАНЕЛЬ - ВЫВОД ===
        # Верхняя часть - текстовый вывод
        output_frame = ttk.Frame(right_frame)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Создаем Notebook для вкладок
        self.notebook = ttk.Notebook(output_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка для текстового вывода
        self.text_output = scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD,
                                                     font=("Courier", 10))
        self.notebook.add(self.text_output, text="Результаты")

        # Вкладка для таблицы данных
        self.table_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.table_frame, text="Таблица данных")

        # Нижняя часть - графики
        self.graph_frame = ttk.LabelFrame(right_frame, text="Графики", padding="10")
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_data(self):
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

            self.data_info.config(text=f"n={len(self.data)}", foreground="green")
            self.show_data_table()
            self.display_result(f"Данные успешно загружены!\n"
                                f"Объем выборки: n = {len(self.data)}\n"
                                f"Диапазон: [{min(self.data):.4f}, {max(self.data):.4f}]\n"
                                f"Размах: R = {max(self.data) - min(self.data):.4f}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {str(e)}")

    def manual_input_dialog(self):
        """Диалоговое окно для ручного ввода интервального ряда"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Ручной ввод интервального ряда")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()

        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        instruction = """Введите интервальный ряд в формате:
        нижняя_граница;верхняя_граница;частота

        Пример:
        10;15;8
        15;20;12
        20;25;15
        25;30;10
        30;35;5"""

        ttk.Label(main_frame, text=instruction, justify=tk.LEFT).pack(pady=(0, 10))

        text_frame = ttk.LabelFrame(main_frame, text="Ввод данных", padding="5")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        input_text = scrolledtext.ScrolledText(text_frame, height=15, font=("Courier", 10))
        input_text.pack(fill=tk.BOTH, expand=True)

        example_data = """10;15;8
15;20;12
20;25;15
25;30;10
30;35;5"""
        input_text.insert(1.0, example_data)

        def process_input():
            text = input_text.get(1.0, tk.END).strip()
            success = self.parse_manual_input(text)
            if success:
                dialog.destroy()

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

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

                parts = line.split(';')
                if len(parts) != 3:
                    raise ValueError(f"Некорректный формат строки: {line}")

                left = float(parts[0].strip())
                right = float(parts[1].strip())
                freq = float(parts[2].strip())

                intervals.append((left, right))
                frequencies.append(freq)

            if not intervals:
                raise ValueError("Не введено ни одного интервала")

            # Сохраняем данные
            self.n_intervals = len(intervals)
            self.interval_bounds = [intervals[0][0]]
            self.midpoints = []

            for left, right in intervals:
                self.interval_bounds.append(right)
                self.midpoints.append((left + right) / 2)

            self.interval_freq = np.array(frequencies, dtype=int)
            total = sum(frequencies)
            self.interval_rel_freq = np.array(frequencies) / total

            # Создаем искусственные данные
            self.data = []
            for i, ((left, right), freq) in enumerate(zip(intervals, frequencies)):
                n_points = int(freq)
                if n_points > 0:
                    points = np.random.uniform(left + 0.001, right - 0.001, n_points)
                    self.data.extend(points.tolist())

            self.data = np.array(self.data)
            self.data_info.config(text=f"n={total} (ручной)", foreground="green")

            self.display_result(f"Ручной ввод успешно обработан!\n"
                                f"Количество интервалов: {self.n_intervals}\n"
                                f"Общая частота: n = {total}")
            return True

        except Exception as e:
            messagebox.showerror("Ошибка ввода", f"Ошибка обработки данных:\n{str(e)}")
            return False

    def show_data_table(self):
        """Показать таблицу с данными"""
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        if self.data is None:
            return

        # Создаем Treeview
        columns = ("№", "Значение")
        tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=20)

        tree.heading("№", text="№")
        tree.heading("Значение", text="Значение")
        tree.column("№", width=50)
        tree.column("Значение", width=150)

        # Добавляем данные
        for i, value in enumerate(self.data[:500], 1):
            tree.insert("", "end", values=(i, f"{value:.6f}"))

        if len(self.data) > 500:
            tree.insert("", "end", values=("...", f"и еще {len(self.data) - 500} значений"))

        scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.notebook.select(1)

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

            # Длина интервала
            h = (data_max - data_min) / self.n_intervals

            # Создаем границы интервалов
            self.interval_bounds = []
            current = data_min
            for i in range(self.n_intervals + 1):
                self.interval_bounds.append(current)
                current += h

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
        self.text_output.insert(tk.END, text)
        self.notebook.select(0)

    def show_basic_stats(self):
        """Пункты 1-3: Исходные данные, интервальный ряд, числовые характеристики"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.calculate_intervals():
            return

        text = "=" * 80 + "\n"
        text += "ПУНКТЫ 1-3: ИСХОДНЫЕ ДАННЫЕ, ИНТЕРВАЛЬНЫЙ РЯД, ЧИСЛОВЫЕ ХАРАКТЕРИСТИКИ\n"
        text += "=" * 80 + "\n\n"

        # 1. Исходные данные
        text += "1. ИСХОДНЫЕ ДАННЫЕ:\n"
        text += "-" * 40 + "\n"
        text += f"Объем выборки: n = {len(self.data)}\n"
        text += f"Минимальное значение: {np.min(self.data):.6f}\n"
        text += f"Максимальное значение: {np.max(self.data):.6f}\n"
        text += f"Размах: R = {np.max(self.data) - np.min(self.data):.6f}\n\n"

        # 2. Интервальный статистический ряд
        text += "2. ИНТЕРВАЛЬНЫЙ СТАТИСТИЧЕСКИЙ РЯД:\n"
        text += "-" * 70 + "\n"
        text += f"{'Интервал':<30} {'Середина':<12} {'Частота':<10} {'Отн.частота':<12}\n"
        text += "-" * 70 + "\n"

        for i in range(self.n_intervals):
            interval_str = f"[{self.interval_bounds[i]:.4f}; {self.interval_bounds[i + 1]:.4f})"
            if i == self.n_intervals - 1:
                interval_str = f"[{self.interval_bounds[i]:.4f}; {self.interval_bounds[i + 1]:.4f}]"

            text += f"{interval_str:<30} {self.midpoints[i]:<12.4f} "
            text += f"{self.interval_freq[i]:<10} {self.interval_rel_freq[i]:<12.6f}\n"
        text += "\n"

        # 3. Числовые характеристики
        text += "3. ЧИСЛОВЫЕ ХАРАКТЕРИСТИКИ ВЫБОРКИ:\n"
        text += "-" * 60 + "\n"

        # Выборочное среднее
        x_mean = np.mean(self.data)
        text += f"Выборочное среднее: x̂в = (1/n) * Σx_i = {x_mean:.6f}\n"

        # Выборочная дисперсия
        D_v = np.var(self.data, ddof=0)
        text += f"Выборочная дисперсия: D̂в = (1/n) * Σ(x_i - x̂в)² = {D_v:.6f}\n"

        # Выборочное среднее квадратическое отклонение
        sigma_v = np.sqrt(D_v)
        text += f"Выборочное СКО: σ̂в = √D̂в = {sigma_v:.6f}\n\n"

        text += "где:\n"
        text += "n = объем выборки\n"
        text += "x_i = значения выборки\n"
        text += "x̂в = выборочное среднее\n"

        self.display_result(text)

    def show_parameter_estimates(self):
        """Пункты 4-5: Точечные оценки параметров и формула плотности"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.calculate_intervals():
            return

        text = "=" * 80 + "\n"
        text += "ПУНКТЫ 4-5: ТОЧЕЧНЫЕ ОЦЕНКИ ПАРАМЕТРОВ И ФОРМУЛА ПЛОТНОСТИ\n"
        text += "=" * 80 + "\n\n"

        # 4. Точечные оценки параметров нормального распределения
        text += "4. ТОЧЕЧНЫЕ ОЦЕНКИ ПАРАМЕТРОВ НОРМАЛЬНОГО РАСПРЕДЕЛЕНИЯ:\n"
        text += "-" * 60 + "\n"

        # Оценка математического ожидания
        a_star = np.mean(self.data)
        text += f"Оценка математического ожидания: a* = x̂в = {a_star:.6f}\n"

        # Оценка среднего квадратического отклонения
        sigma_star = np.std(self.data, ddof=0)
        text += f"Оценка СКО: σ* = σ̂в = {sigma_star:.6f}\n\n"

        # 5. Формула плотности предполагаемого закона распределения
        text += "5. ФОРМУЛА ПЛОТНОСТИ НОРМАЛЬНОГО РАСПРЕДЕЛЕНИЯ:\n"
        text += "-" * 60 + "\n"
        text += "Предполагаемый закон распределения: N(a*, σ*²)\n\n"
        text += "Плотность вероятности:\n"
        text += "         1            (x - a*)²\n"
        text += "f(x) = ——————— * exp(- ———————— )\n"
        text += "       σ*√(2π)         2(σ*)²\n\n"

        text += "С найденными параметрами:\n"
        text += f"         1            (x - {a_star:.6f})²\n"
        text += f"f(x) = ————————— * exp(- —————————————— )\n"
        text += f"       {sigma_star:.6f}·√(2π)      2·({sigma_star:.6f})²\n"

        self.display_result(text)

    def show_comparison_graphs(self):
        """Пункт 6: Графики сравнения"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.calculate_intervals():
            return

        # Очищаем область графиков
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Параметры нормального распределения
        a_star = np.mean(self.data)
        sigma_star = np.std(self.data, ddof=0)

        # 6а) Ломаная с вершинами в серединах горизонтальных отрезков гистограммы
        # Строим гистограмму относительных частот
        widths = [self.interval_bounds[i + 1] - self.interval_bounds[i]
                  for i in range(self.n_intervals)]
        bar_widths = [w * 0.8 for w in widths]

        # Гистограмма относительных частот
        bars = ax1.bar(self.midpoints, self.interval_rel_freq,
                       width=bar_widths, alpha=0.5, color='lightblue',
                       edgecolor='black', label='Гистограмма отн. частот')

        # Ломаная через середины верхних оснований прямоугольников
        # Для каждого прямоугольника берем середину верхнего основания
        poly_x = []
        poly_y = []
        for i in range(self.n_intervals):
            x = self.midpoints[i]
            y = self.interval_rel_freq[i]
            poly_x.append(x)
            poly_y.append(y)

        ax1.plot(poly_x, poly_y, 'ro-', linewidth=2, markersize=8,
                 label='Ломаная через середины')

        ax1.set_xlabel('x', fontsize=12)
        ax1.set_ylabel('Относительная частота / Плотность', fontsize=12)
        ax1.set_title('Гистограмма и ломаная', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 6б) График плотности нормального распределения
        # Создаем точки для графика плотности
        x_min = min(self.interval_bounds)
        x_max = max(self.interval_bounds)
        x_normal = np.linspace(x_min, x_max, 1000)

        # Плотность нормального распределения
        y_normal = (1 / (sigma_star * np.sqrt(2 * np.pi))) * \
                   np.exp(-0.5 * ((x_normal - a_star) / sigma_star) ** 2)

        ax2.plot(x_normal, y_normal, 'b-', linewidth=2, label='Теоретическая плотность N(a*,σ*)')

        # Также покажем гистограмму для сравнения
        ax2.bar(self.midpoints, self.interval_rel_freq, width=bar_widths,
                alpha=0.3, color='orange', label='Гистограмма отн. частот')

        ax2.set_xlabel('x', fontsize=12)
        ax2.set_ylabel('Плотность вероятности', fontsize=12)
        ax2.set_title('Теоретическая и эмпирическая плотности', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        # Встраиваем график
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Текстовое описание
        text = "=" * 80 + "\n"
        text += "ПУНКТ 6: ГРАФИКИ СРАВНЕНИЯ\n"
        text += "=" * 80 + "\n\n"
        text += "6. ГРАФИКИ:\n"
        text += "-" * 60 + "\n"
        text += "а) Ломаная с вершинами в точках, являющихся серединами\n"
        text += "   горизонтальных отрезков гистограммы относительных частот\n\n"
        text += "б) График плотности нормального распределения с параметрами:\n"
        text += f"   a* = {a_star:.6f}\n"
        text += f"   σ* = {sigma_star:.6f}\n\n"
        text += "Сравнение позволяет визуально оценить соответствие\n"
        text += "эмпирического распределения теоретическому нормальному."

        self.display_result(text)

    def simpson_integral(self, f, a, b, n=1000):
        """Вычисление интеграла по составной формуле Симпсона"""
        if n % 2 == 1:
            n += 1  # Делаем n четным

        h = (b - a) / n
        x = np.linspace(a, b, n + 1)
        y = f(x)

        # Формула Симпсона
        integral = h / 3 * (y[0] + y[-1] + 4 * np.sum(y[1:-1:2]) + 2 * np.sum(y[2:-2:2]))
        return integral

    def normal_cdf_simpson(self, x, a_star, sigma_star):
        """Вычисление функции нормального распределения через интеграл Симпсона"""
        # Стандартизируем переменную
        z = (x - a_star) / sigma_star

        # Подынтегральная функция стандартного нормального распределения
        def integrand(t):
            return np.exp(-t ** 2 / 2) / np.sqrt(2 * np.pi)

        # Вычисляем интеграл от -∞ до z
        # Для отрицательных больших значений используем симметрию
        if z < -10:
            return 0.0
        elif z > 10:
            return 1.0
        else:
            # Разбиваем на части для лучшей точности
            if z < 0:
                integral = self.simpson_integral(integrand, z, 0, n=500)
                return 0.5 - integral
            else:
                integral = self.simpson_integral(integrand, 0, z, n=500)
                return 0.5 + integral

    def show_theoretical_probabilities(self):
        """Пункт 7: Теоретические вероятности"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.calculate_intervals():
            return

        text = "=" * 80 + "\n"
        text += "ПУНКТ 7: ТЕОРЕТИЧЕСКИЕ ВЕРОЯТНОСТИ\n"
        text += "=" * 80 + "\n\n"

        # Параметры нормального распределения
        a_star = np.mean(self.data)
        sigma_star = np.std(self.data, ddof=0)

        text += "7. ТЕОРЕТИЧЕСКИЕ ВЕРОЯТНОСТИ p_i:\n"
        text += "-" * 60 + "\n"
        text += "Вероятность попадания в i-й интервал для N(a*, σ*):\n\n"
        text += "       1      x_{i+1} - a*    \n"
        text += "p_i = ———— *  ∫           exp(-t²/2) dt\n"
        text += "      √(2π)   x_i - a*\n"
        text += "                ————\n"
        text += "                 σ*\n\n"

        text += "Вычисление по составной формуле Симпсона (точность 0.001):\n\n"

        text += f"{'Интервал':<30} {'z_i':<15} {'z_{i+1}':<15} {'p_i':<15}\n"
        text += "-" * 75 + "\n"

        p_i_values = []
        total_p = 0

        for i in range(self.n_intervals):
            # Стандартизированные границы
            z1 = (self.interval_bounds[i] - a_star) / sigma_star
            z2 = (self.interval_bounds[i + 1] - a_star) / sigma_star

            # Вычисляем вероятность через функцию распределения
            # Используем собственную реализацию через интеграл Симпсона
            p_i = self.normal_cdf_simpson(self.interval_bounds[i + 1], a_star, sigma_star) - \
                  self.normal_cdf_simpson(self.interval_bounds[i], a_star, sigma_star)

            p_i_values.append(p_i)
            total_p += p_i

            interval_str = f"[{self.interval_bounds[i]:.4f}; {self.interval_bounds[i + 1]:.4f})"
            if i == self.n_intervals - 1:
                interval_str = f"[{self.interval_bounds[i]:.4f}; {self.interval_bounds[i + 1]:.4f}]"

            text += f"{interval_str:<30} {z1:<15.4f} {z2:<15.4f} {p_i:<15.6f}\n"

        text += "-" * 75 + "\n"
        text += f"{'Сумма вероятностей:':<60} {total_p:.6f}\n\n"

        text += "Примечание: Сумма p_i должна быть близка к 1.\n"
        text += "Небольшие отклонения возможны из-за численного интегрирования.\n"

        self.p_i_values = p_i_values  # Сохраняем для использования в других методах
        self.display_result(text)

    def show_chi2_observed(self):
        """Пункт 8: χ² наблюдаемое"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.calculate_intervals():
            return

        # Сначала вычисляем теоретические вероятности, если еще не сделано
        if not hasattr(self, 'p_i_values'):
            self.show_theoretical_probabilities()
            return

        text = "=" * 80 + "\n"
        text += "ПУНКТ 8: χ² НАБЛЮДАЕМОЕ\n"
        text += "=" * 80 + "\n\n"

        n = len(self.data)
        p_i = self.p_i_values

        text += "8. ВЫЧИСЛЕНИЕ χ² НАБЛЮДАЕМОГО:\n"
        text += "-" * 60 + "\n\n"

        text += "Формула для χ² наблюдаемого:\n"
        text += "       k   (n_i - n·p_i)²\n"
        text += "χ² =  Σ  ———————————————\n"
        text += "      i=1      n·p_i\n\n"

        text += "где:\n"
        text += "k = число интервалов = " + str(self.n_intervals) + "\n"
        text += "n = объем выборки = " + str(n) + "\n"
        text += "n_i = наблюдаемая частота в i-м интервале\n"
        text += "p_i = теоретическая вероятность для i-го интервала\n\n"

        text += f"{'Интервал':<30} {'n_i':<10} {'n·p_i':<12} {'(n_i-n·p_i)²':<15} {'(n_i-n·p_i)²/(n·p_i)':<20}\n"
        text += "-" * 90 + "\n"

        chi2_observed = 0
        for i in range(self.n_intervals):
            n_i = self.interval_freq[i]
            n_p_i = n * p_i[i]
            diff_squared = (n_i - n_p_i) ** 2
            term = diff_squared / n_p_i if n_p_i > 0 else 0
            chi2_observed += term

            interval_str = f"[{self.interval_bounds[i]:.4f}; {self.interval_bounds[i + 1]:.4f})"
            if i == self.n_intervals - 1:
                interval_str = f"[{self.interval_bounds[i]:.4f}; {self.interval_bounds[i + 1]:.4f}]"

            text += f"{interval_str:<30} {n_i:<10} {n_p_i:<12.2f} {diff_squared:<15.2f} {term:<20.6f}\n"

        text += "-" * 90 + "\n"
        text += f"{'Сумма:':<52} {chi2_observed:.6f}\n\n"

        text += f"χ² наблюдаемое = {chi2_observed:.6f}\n"

        self.chi2_observed = chi2_observed  # Сохраняем для использования в проверке гипотезы
        self.display_result(text)

    def get_chi2_critical(self, df, alpha):
        """Получение критического значения χ²"""
        # Таблица критических значений χ² для различных уровней значимости
        # Используем аппроксимацию через квантили распределения χ²

        # Для точности используем scipy если доступен, иначе аппроксимацию
        try:
            from scipy import stats
            return stats.chi2.ppf(1 - alpha, df)
        except:
            # Аппроксимация для наиболее распространенных значений
            # Это упрощенная таблица
            chi2_table = {
                0.01: {1: 6.63, 2: 9.21, 3: 11.34, 4: 13.28, 5: 15.09,
                       6: 16.81, 7: 18.48, 8: 20.09, 9: 21.67, 10: 23.21},
                0.05: {1: 3.84, 2: 5.99, 3: 7.81, 4: 9.49, 5: 11.07,
                       6: 12.59, 7: 14.07, 8: 15.51, 9: 16.92, 10: 18.31},
                0.10: {1: 2.71, 2: 4.61, 3: 6.25, 4: 7.78, 5: 9.24,
                       6: 10.64, 7: 12.02, 8: 13.36, 9: 14.68, 10: 15.99}
            }

            alpha_key = round(alpha, 2)
            if alpha_key in chi2_table and df in chi2_table[alpha_key]:
                return chi2_table[alpha_key][df]
            else:
                # Линейная интерполяция для промежуточных значений
                return 2 * df  # Очень грубая аппроксимация

    def perform_hypothesis_test(self):
        """Пункты 9-11: Проверка гипотезы"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        if not self.calculate_intervals():
            return

        # Сначала вычисляем χ² наблюдаемое, если еще не сделано
        if not hasattr(self, 'chi2_observed'):
            self.show_chi2_observed()
            return

        text = "=" * 80 + "\n"
        text += "ПУНКТЫ 9-11: ПРОВЕРКА ГИПОТЕЗЫ\n"
        text += "=" * 80 + "\n\n"

        # 9. Уровень значимости и число степеней свободы
        try:
            alpha = float(self.alpha_var.get())
        except:
            alpha = 0.05

        text += "9. УРОВЕНЬ ЗНАЧИМОСТИ И ЧИСЛО СТЕПЕНЕЙ СВОБОДЫ:\n"
        text += "-" * 60 + "\n\n"

        text += f"Уровень значимости: α = {alpha}\n\n"

        # Число степеней свободы
        # r = k - 1 - m, где m - число оцененных параметров
        # Для нормального распределения: m = 2 (a* и σ*)
        r = self.n_intervals - 1 - 2

        text += "Формула для числа степеней свободы:\n"
        text += "r = k - 1 - m\n"
        text += "где:\n"
        text += f"k = число интервалов = {self.n_intervals}\n"
        text += "m = число оцененных параметров = 2 (для нормального распределения)\n"
        text += f"r = {self.n_intervals} - 1 - 2 = {r}\n\n"

        # 10. Критическое значение χ²
        chi2_critical = self.get_chi2_critical(r, alpha)

        text += "10. КРИТИЧЕСКОЕ ЗНАЧЕНИЕ χ²:\n"
        text += "-" * 60 + "\n\n"

        text += "Таблица критических значений χ²-распределения:\n"
        text += f"Уровень значимости α = {alpha}\n"
        text += f"Число степеней свободы r = {r}\n"
        text += f"χ² критическое = {chi2_critical:.4f}\n\n"

        text += "Сокращенная таблица χ²-распределения:\n"
        text += "-" * 60 + "\n"
        text += f"{'α':<10} {'0.10':<10} {'0.05':<10} {'0.01':<10}\n"
        text += "-" * 60 + "\n"

        # Показываем значения для различных α вокруг нашего r
        r_values = [max(1, r - 2), max(1, r - 1), r, r + 1, r + 2]
        for r_val in r_values:
            line = f"r={r_val:<6}"
            for a in [0.10, 0.05, 0.01]:
                crit_val = self.get_chi2_critical(r_val, a)
                line += f"{crit_val:<10.3f}"
            text += line + "\n"

        text += "\n"

        # 11. Сравнение и вывод результата
        text += "11. СРАВНЕНИЕ И РЕЗУЛЬТАТ ПРОВЕРКИ:\n"
        text += "-" * 60 + "\n\n"

        text += f"χ² наблюдаемое = {self.chi2_observed:.6f}\n"
        text += f"χ² критическое = {chi2_critical:.4f}\n\n"

        if self.chi2_observed < chi2_critical:
            text += "РЕЗУЛЬТАТ: χ² наблюдаемое < χ² критическое\n"
            text += "⇒ Нет оснований отвергнуть нулевую гипотезу H₀\n"
            text += "⇒ Данные согласуются с нормальным распределением\n"
            result = "Гипотеза H₀ не отвергается"
        else:
            text += "РЕЗУЛЬТАТ: χ² наблюдаемое ≥ χ² критическое\n"
            text += "⇒ Отвергаем нулевую гипотезу H₀\n"
            text += "⇒ Данные не согласуются с нормальным распределением\n"
            result = "Гипотеза H₀ отвергается"

        text += f"\nУровень значимости: α = {alpha}\n"
        text += f"Вероятность ошибки первого рода: {alpha * 100}%\n"

        # Строим график распределения χ²
        self.plot_chi2_distribution(r, alpha, self.chi2_observed, chi2_critical, result)

        self.display_result(text)

    def plot_chi2_distribution(self, df, alpha, chi2_obs, chi2_crit, result):
        """Построение графика распределения χ²"""
        # Очищаем область графиков
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(10, 6))

        # Создаем точки для графика плотности χ²-распределения
        x_max = max(chi2_crit * 1.5, chi2_obs * 1.2, 3 * df)
        x = np.linspace(0.001, x_max, 1000)

        # Плотность χ²-распределения
        try:
            from scipy import stats
            y = stats.chi2.pdf(x, df)
        except:
            # Аппроксимация плотности χ²
            y = (x ** (df / 2 - 1) * np.exp(-x / 2)) / (2 ** (df / 2) * special.gamma(df / 2))

        # График плотности
        ax.plot(x, y, 'b-', linewidth=2, label=f'χ²-распределение (df={df})')

        # Критическая область
        x_crit = np.linspace(chi2_crit, x_max, 100)
        y_crit = (x_crit ** (df / 2 - 1) * np.exp(-x_crit / 2)) / (2 ** (df / 2) * special.gamma(df / 2))
        ax.fill_between(x_crit, 0, y_crit, alpha=0.3, color='red',
                        label=f'Критическая область (α={alpha})')

        # Линии для наблюдаемого и критического значений
        ax.axvline(x=chi2_crit, color='r', linestyle='--', linewidth=2,
                   label=f'χ² критическое = {chi2_crit:.3f}')
        ax.axvline(x=chi2_obs, color='g', linestyle='--', linewidth=2,
                   label=f'χ² наблюдаемое = {chi2_obs:.3f}')

        # Точка наблюдаемого значения
        y_obs = (chi2_obs ** (df / 2 - 1) * np.exp(-chi2_obs / 2)) / (2 ** (df / 2) * special.gamma(df / 2))
        ax.plot(chi2_obs, y_obs, 'go', markersize=10)

        ax.set_xlabel('χ²', fontsize=12)
        ax.set_ylabel('Плотность вероятности', fontsize=12)
        ax.set_title(f'Проверка гипотезы: {result}', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        # Встраиваем график
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def full_analysis(self):
        """Выполнить полный анализ (все пункты)"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        # Выполняем все этапы анализа
        self.show_basic_stats()
        self.show_parameter_estimates()
        self.show_comparison_graphs()
        self.show_theoretical_probabilities()
        self.show_chi2_observed()
        self.perform_hypothesis_test()

        # Сводная информация
        current_text = self.text_output.get(1.0, tk.END)
        summary = "\n" + "=" * 80 + "\n"
        summary += "СВОДКА ПОЛНОГО АНАЛИЗА\n"
        summary += "=" * 80 + "\n\n"
        summary += "Выполнены все 11 пунктов задания:\n"
        summary += "1. Ввод и вывод исходных данных ✓\n"
        summary += "2. Интервальный статистический ряд ✓\n"
        summary += "3. Числовые характеристики выборки ✓\n"
        summary += "4. Точечные оценки параметров нормального распределения ✓\n"
        summary += "5. Формула плотности с найденными параметрами ✓\n"
        summary += "6. Графики сравнения ✓\n"
        summary += "7. Теоретические вероятности (формула Симпсона) ✓\n"
        summary += "8. χ² наблюдаемое ✓\n"
        summary += "9. Уровень значимости и число степеней свободы ✓\n"
        summary += "10. Критическое значение χ² ✓\n"
        summary += "11. Сравнение и вывод результата ✓\n"

        self.text_output.insert(tk.END, summary)

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
                f.write("ОТЧЕТ ПО ПРОВЕРКЕ ГИПОТЕЗЫ О НОРМАЛЬНОМ РАСПРЕДЕЛЕНИИ\n")
                f.write("Критерий согласия Пирсона (χ²-критерий)\n")
                f.write("=" * 80 + "\n\n")

                f.write(f"Дата анализа: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Объем выборки: n = {len(self.data)}\n")
                f.write(f"Количество интервалов: k = {self.interval_var.get()}\n")
                f.write(f"Уровень значимости: α = {self.alpha_var.get()}\n\n")

                # Основные характеристики
                f.write("1. ОСНОВНЫЕ ХАРАКТЕРИСТИКИ:\n")
                f.write("-" * 40 + "\n")
                f.write(f"Выборочное среднее: {np.mean(self.data):.6f}\n")
                f.write(f"Выборочная дисперсия: {np.var(self.data, ddof=0):.6f}\n")
                f.write(f"Выборочное СКО: {np.std(self.data, ddof=0):.6f}\n\n")

                # Оценки параметров
                f.write("2. ОЦЕНКИ ПАРАМЕТРОВ НОРМАЛЬНОГО РАСПРЕДЕЛЕНИЯ:\n")
                f.write("-" * 40 + "\n")
                f.write(f"a* (математическое ожидание): {np.mean(self.data):.6f}\n")
                f.write(f"σ* (СКО): {np.std(self.data, ddof=0):.6f}\n\n")

                # Результат проверки
                if hasattr(self, 'chi2_observed'):
                    f.write("3. РЕЗУЛЬТАТ ПРОВЕРКИ ГИПОТЕЗЫ:\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"χ² наблюдаемое: {self.chi2_observed:.6f}\n")

                    try:
                        alpha = float(self.alpha_var.get())
                        r = int(self.interval_var.get()) - 3
                        chi2_crit = self.get_chi2_critical(r, alpha)
                        f.write(f"χ² критическое (α={alpha}, df={r}): {chi2_crit:.4f}\n")

                        if self.chi2_observed < chi2_crit:
                            f.write("Вывод: Гипотеза H₀ не отвергается\n")
                            f.write("Данные согласуются с нормальным распределением\n")
                        else:
                            f.write("Вывод: Гипотеза H₀ отвергается\n")
                            f.write("Данные не согласуются с нормальным распределением\n")
                    except:
                        f.write("(Для получения полного результата выполните проверку гипотезы)\n")

                f.write("\n" + "=" * 80 + "\n")
                f.write("Отчет сгенерирован программой проверки гипотез\n")

            messagebox.showinfo("Успех", f"Отчет сохранен в файл:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить отчет: {str(e)}")


def main():
    root = tk.Tk()
    app = PearsonChiSquareTest(root)
    root.mainloop()


if __name__ == "__main__":
    main()