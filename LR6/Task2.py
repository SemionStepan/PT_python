import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import math
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re


class UniformDistributionTester:
    def __init__(self, root):
        self.root = root
        self.root.title("Проверка гипотезы о равномерном распределении")
        self.root.geometry("1100x800")

        # Данные
        self.intervals = []  # Список кортежей (left, right, left_inclusive, right_inclusive)
        self.frequencies = []  # Наблюдаемые частоты
        self.n_total = 0  # Общий объём выборки

        # Параметры
        self.a_est = 0  # Оценка параметра a
        self.b_est = 0  # Оценка параметра b

        # Результаты
        self.theoretical_probs = []
        self.theoretical_freqs = []
        self.chi2_observed = 0
        self.df = 0
        self.alpha = 0.05

        # ====================== СОЗДАНИЕ ИНТЕРФЕЙСА ======================

        # Основной фрейм с прокруткой
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas и Scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # ====================== СЕКЦИЯ 1: ВВОД ДАННЫХ ======================
        input_frame = ttk.LabelFrame(self.scrollable_frame, text="1. Ввод интервального ряда частот", padding=10)
        input_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Текстовое поле для ввода
        self.data_text = tk.Text(input_frame, height=8, width=70)
        self.data_text.pack(side=tk.LEFT, padx=(0, 10))

        # Пример данных по умолчанию
        default_data = "[10;15) 5\n[15;20) 12\n[20;25] 8"
        self.data_text.insert("1.0", default_data)

        # Фрейм кнопок для ввода данных
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(side=tk.RIGHT)

        ttk.Button(button_frame, text="Загрузить из файла",
                   command=self.load_from_file).pack(pady=5)
        ttk.Button(button_frame, text="Ввести вручную",
                   command=self.parse_input_data).pack(pady=5)
        ttk.Button(button_frame, text="Очистить",
                   command=self.clear_data).pack(pady=5)

        # Метка с информацией о формате
        format_label = ttk.Label(input_frame,
                                 text="Формат: [нижняя;верхняя) частота\n[ - включает, ) - исключает\nПример: [10;15) 5",
                                 font=("Arial", 9))
        format_label.pack(side=tk.BOTTOM, pady=5)

        # ====================== СЕКЦИЯ 2: ПАРАМЕТРЫ РАСЧЁТА ======================
        params_frame = ttk.LabelFrame(self.scrollable_frame, text="2. Параметры расчёта", padding=10)
        params_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Метод оценки параметров
        ttk.Label(params_frame, text="Метод оценки параметров:").grid(row=0, column=0, sticky="w", padx=5)
        self.param_method = tk.StringVar(value="minmax")
        ttk.Radiobutton(params_frame, text="min(X_i), max(X_i)",
                        variable=self.param_method, value="minmax").grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(params_frame, text="X̄ ± √3 * S (через среднее и СКО)",
                        variable=self.param_method, value="mean_std").grid(row=0, column=2, sticky="w")

        # Уровень значимости
        ttk.Label(params_frame, text="Уровень значимости α:").grid(row=1, column=0, sticky="w", padx=5, pady=(10, 0))

        alpha_frame = ttk.Frame(params_frame)
        alpha_frame.grid(row=1, column=1, columnspan=3, sticky="w", pady=(10, 0))

        self.alpha_var = tk.StringVar(value="0.05")
        ttk.Radiobutton(alpha_frame, text="0.01",
                        variable=self.alpha_var, value="0.01").pack(side=tk.LEFT)
        ttk.Radiobutton(alpha_frame, text="0.05",
                        variable=self.alpha_var, value="0.05").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(alpha_frame, text="0.10",
                        variable=self.alpha_var, value="0.10").pack(side=tk.LEFT)

        ttk.Label(alpha_frame, text="Или введите:").pack(side=tk.LEFT, padx=(20, 5))
        self.custom_alpha = ttk.Entry(alpha_frame, width=8)
        self.custom_alpha.pack(side=tk.LEFT)
        self.custom_alpha.insert(0, "0.05")

        # ====================== СЕКЦИЯ 3: КНОПКИ УПРАВЛЕНИЯ ======================
        control_frame = ttk.Frame(self.scrollable_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(control_frame, text="Выполнить расчёт",
                   command=self.calculate_all, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Показать графики",
                   command=self.show_graphs).pack(side=tk.LEFT, padx=5)

        # Стиль для выделенной кнопки
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))

        # ====================== СЕКЦИЯ 4: ВЫВОД РЕЗУЛЬТАТОВ ======================
        results_frame = ttk.LabelFrame(self.scrollable_frame, text="Результаты проверки гипотезы", padding=10)
        results_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        # Текстовое поле для вывода результатов с прокруткой
        results_text_frame = ttk.Frame(results_frame)
        results_text_frame.pack(fill=tk.BOTH, expand=True)

        self.results_text = tk.Text(results_text_frame, height=30, width=100, wrap=tk.WORD)
        scrollbar_results = ttk.Scrollbar(results_text_frame, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar_results.set)

        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_results.pack(side=tk.RIGHT, fill=tk.Y)

        # Настройка весов строк и столбцов для растягивания
        self.scrollable_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Инициализируем данные из примера
        self.parse_input_data()

    # ====================== МЕТОДЫ ДЛЯ РАБОТЫ С ДАННЫМИ ======================

    def load_from_file(self):
        """Загрузка данных из файла"""
        filepath = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.data_text.delete("1.0", tk.END)
                self.data_text.insert("1.0", data)
                self.parse_input_data()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def clear_data(self):
        """Очистка поля ввода"""
        self.data_text.delete("1.0", tk.END)

    def parse_input_data(self):
        """Парсинг введённых данных"""
        data = self.data_text.get("1.0", tk.END).strip()
        lines = data.split('\n')

        self.intervals = []
        self.frequencies = []

        # Регулярное выражение для разбора строки
        pattern = r'([\[\(])([0-9.]+);([0-9.]+)([\]\)])\s+([0-9.]+)'

        for line in lines:
            line = line.strip()
            if not line:
                continue

            match = re.match(pattern, line)
            if match:
                left_bracket, left_val, right_val, right_bracket, freq = match.groups()

                left_val = float(left_val)
                right_val = float(right_val)
                freq = int(freq)

                left_inclusive = (left_bracket == '[')
                right_inclusive = (right_bracket == ']')

                self.intervals.append((left_val, right_val, left_inclusive, right_inclusive))
                self.frequencies.append(freq)
            else:
                messagebox.showwarning("Предупреждение",
                                       f"Строка не распознана: '{line}'\nОжидается формат: [10;15) 5")

        self.n_total = sum(self.frequencies)

        # Вывод информации о загруженных данных
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", "=== ИНТЕРВАЛЬНЫЙ РЯД ЧАСТОТ ===\n")
        self.results_text.insert(tk.END, f"Общий объём выборки: n = {self.n_total}\n\n")

        for i, ((left, right, li, ri), freq) in enumerate(zip(self.intervals, self.frequencies)):
            left_br = "[" if li else "("
            right_br = "]" if ri else ")"
            self.results_text.insert(tk.END,
                                     f"Интервал {i + 1}: {left_br}{left}; {right}{right_br}  n{i + 1} = {freq}\n")

        self.results_text.insert(tk.END, "\n" + "=" * 50 + "\n")

    # ====================== ОСНОВНЫЕ РАСЧЁТЫ ======================

    def calculate_all(self):
        """Основная функция расчётов"""
        if not self.intervals:
            messagebox.showwarning("Нет данных", "Сначала введите данные!")
            return

        try:
            # Получаем уровень значимости
            if self.custom_alpha.get().strip():
                try:
                    self.alpha = float(self.custom_alpha.get())
                except ValueError:
                    self.alpha = float(self.alpha_var.get())
            else:
                self.alpha = float(self.alpha_var.get())

            # Пункт 2,3: Оценка параметров
            self.estimate_parameters()

            # Пункт 4: Функции распределения и плотности
            self.display_functions()

            # Пункт 6: Теоретические вероятности
            self.calculate_theoretical_probs()

            # Пункт 7: Теоретические частоты и разности
            self.calculate_theoretical_freqs()

            # Пункт 8: χ² наблюдаемое
            self.calculate_chi2_observed()

            # Пункт 9: Число степеней свободы
            self.calculate_degrees_of_freedom()

            # Пункт 10: χ² критическое
            self.find_chi2_critical()

            # Пункт 11: Проверка гипотезы
            self.test_hypothesis()

        except Exception as e:
            messagebox.showerror("Ошибка расчёта", f"Произошла ошибка:\n{str(e)}")

    def estimate_parameters(self):
        """Пункт 2,3: Оценка параметров равномерного распределения"""
        # Находим середины интервалов (для метода через среднее/СКО)
        midpoints = []
        for (left, right, li, ri), freq in zip(self.intervals, self.frequencies):
            mid = (left + right) / 2
            midpoints.extend([mid] * freq)

        midpoints = np.array(midpoints)

        if self.param_method.get() == "minmax":
            # Метод min/max
            self.a_est = min(midpoints)
            self.b_est = max(midpoints)
            formula_a = "a* = min(X_i)"
            formula_b = "b* = max(X_i)"
        else:
            # Метод через среднее и СКО
            mean_val = np.mean(midpoints)
            std_val = np.std(midpoints, ddof=1)  # Исправленное СКО
            self.a_est = mean_val - math.sqrt(3) * std_val
            self.b_est = mean_val + math.sqrt(3) * std_val
            formula_a = "a* = X̄ - √3 * S"
            formula_b = "b* = X̄ + √3 * S"

        # Вывод результатов
        self.results_text.insert(tk.END, "\n=== ОЦЕНКА ПАРАМЕТРОВ РАВНОМЕРНОГО РАСПРЕДЕЛЕНИЯ ===\n")
        self.results_text.insert(tk.END, f"Используемый метод: {formula_a}, {formula_b}\n")
        self.results_text.insert(tk.END, f"Оценка параметра a: a* = {self.a_est:.4f}\n")
        self.results_text.insert(tk.END, f"Оценка параметра b: b* = {self.b_est:.4f}\n")

    def display_functions(self):
        """Пункт 4: Функции распределения и плотности"""
        self.results_text.insert(tk.END, "\n=== ФУНКЦИИ РАСПРЕДЕЛЕНИЯ И ПЛОТНОСТИ ===\n")
        self.results_text.insert(tk.END, f"Плотность: f(x) = 1/(b* - a*) = 1/({self.b_est:.4f} - {self.a_est:.4f})\n")
        self.results_text.insert(tk.END,
                                 f"            f(x) = {1 / (self.b_est - self.a_est):.4f} для x ∈ [{self.a_est:.4f}, {self.b_est:.4f}]\n")
        self.results_text.insert(tk.END, f"            f(x) = 0 для x ∉ [{self.a_est:.4f}, {self.b_est:.4f}]\n\n")

        self.results_text.insert(tk.END, "Функция распределения:\n")
        self.results_text.insert(tk.END, f"            F(x) = 0 для x < {self.a_est:.4f}\n")
        self.results_text.insert(tk.END,
                                 f"            F(x) = (x - {self.a_est:.4f})/({self.b_est:.4f} - {self.a_est:.4f}) для x ∈ [{self.a_est:.4f}, {self.b_est:.4f}]\n")
        self.results_text.insert(tk.END, f"            F(x) = 1 для x > {self.b_est:.4f}\n")

    def calculate_theoretical_probs(self):
        """Пункт 6: Теоретические вероятности"""
        self.results_text.insert(tk.END, "\n=== ТЕОРЕТИЧЕСКИЕ ВЕРОЯТНОСТИ ===\n")
        self.results_text.insert(tk.END, "p_i = F(b_i) - F(a_i)\n")
        self.results_text.insert(tk.END, "где a_i, b_i - границы интервала\n\n")

        self.theoretical_probs = []
        total_prob = 0

        for i, (left, right, left_inc, right_inc) in enumerate(self.intervals):
            # Для равномерного распределения вероятность - это отношение длин
            # Но учитываем, что распределение определено на [a*, b*]

            # Фактические границы с учётом включения/исключения
            actual_left = left if left_inc else left + 1e-10
            actual_right = right if right_inc else right - 1e-10

            # Ограничиваем границы областью определения распределения
            interval_left = max(actual_left, self.a_est)
            interval_right = min(actual_right, self.b_est)

            if interval_right > interval_left:
                prob = (interval_right - interval_left) / (self.b_est - self.a_est)
            else:
                prob = 0

            # Учитываем частичные выходящие за пределы интервалы
            if actual_left < self.a_est < actual_right:
                prob += (min(actual_right, self.a_est) - actual_left) / (self.b_est - self.a_est)

            self.theoretical_probs.append(prob)
            total_prob += prob

            self.results_text.insert(tk.END,
                                     f"p{i + 1} = F({right:.2f}) - F({left:.2f}) = {prob:.4f}\n")

        self.results_text.insert(tk.END, f"\nСумма вероятностей: Σp_i = {total_prob:.4f}\n")

    def calculate_theoretical_freqs(self):
        """Пункт 7: Теоретические частоты и разности"""
        self.results_text.insert(tk.END, "\n=== ТАБЛИЦА РАСЧЁТА χ² ===\n")
        self.results_text.insert(tk.END, "i  [a_i; b_i)   n_i    p_i     n_i' = p_i*n    (n_i' - n_i)²\n")
        self.results_text.insert(tk.END, "-" * 60 + "\n")

        self.theoretical_freqs = []
        chi2_components = []

        for i in range(len(self.intervals)):
            n_i = self.frequencies[i]
            p_i = self.theoretical_probs[i]
            n_i_prime = p_i * self.n_total
            self.theoretical_freqs.append(n_i_prime)

            diff_squared = (n_i_prime - n_i) ** 2
            chi2_components.append(diff_squared / n_i_prime if n_i_prime > 0 else 0)

            left, right, li, ri = self.intervals[i]
            left_br = "[" if li else "("
            right_br = "]" if ri else ")"

            self.results_text.insert(tk.END,
                                     f"{i + 1:2} {left_br}{left:4.1f};{right:4.1f}{right_br} {n_i:4}  {p_i:6.4f}   {n_i_prime:8.2f}      {diff_squared:10.4f}\n")

    def calculate_chi2_observed(self):
        """Пункт 8: Вычисление χ² наблюдаемого"""
        self.chi2_observed = 0
        for i in range(len(self.intervals)):
            n_i = self.frequencies[i]
            n_i_prime = self.theoretical_freqs[i]
            if n_i_prime > 0:  # Избегаем деления на 0
                self.chi2_observed += ((n_i - n_i_prime) ** 2) / n_i_prime

        self.results_text.insert(tk.END, "\n" + "=" * 60 + "\n")
        self.results_text.insert(tk.END, "χ²_набл = Σ[(n_i - n_i')² / n_i']\n")
        self.results_text.insert(tk.END, f"χ²_набл = {self.chi2_observed:.4f}\n")

    def calculate_degrees_of_freedom(self):
        """Пункт 9: Число степеней свободы"""
        k = len(self.intervals)
        r = 2  # Для равномерного распределения оцениваем 2 параметра
        self.df = k - 1 - r

        self.results_text.insert(tk.END, "\n=== ЧИСЛО СТЕПЕНЕЙ СВОБОДЫ ===\n")
        self.results_text.insert(tk.END, "df = k - 1 - r, где k - число интервалов, r - число оцененных параметров\n")
        self.results_text.insert(tk.END, f"df = {k} - 1 - {r} = {self.df}\n")

        if self.df <= 0:
            self.results_text.insert(tk.END,
                                     "\n⚠ ВНИМАНИЕ: Число степеней свободы ≤ 0! Необходимо увеличить число интервалов.\n")

    def find_chi2_critical(self):
        """Пункт 10: Нахождение χ² критического"""
        if self.df <= 0:
            self.chi2_critical = float('inf')
            return

        self.chi2_critical = stats.chi2.ppf(1 - self.alpha, self.df)

        self.results_text.insert(tk.END, "\n=== КРИТИЧЕСКОЕ ЗНАЧЕНИЕ χ² ===\n")
        self.results_text.insert(tk.END, f"Уровень значимости: α = {self.alpha}\n")
        self.results_text.insert(tk.END, f"Число степеней свободы: df = {self.df}\n")
        self.results_text.insert(tk.END, f"χ²_крит(α={self.alpha}, df={self.df}) = {self.chi2_critical:.4f}\n")

        # Таблица популярных значений для сравнения
        self.results_text.insert(tk.END, "\nТаблица χ²_крит для различных α:\n")
        self.results_text.insert(tk.END, "α     0.10    0.05    0.01\n")
        self.results_text.insert(tk.END, f"df={self.df}  ")

        for alpha_val in [0.10, 0.05, 0.01]:
            crit_val = stats.chi2.ppf(1 - alpha_val, self.df)
            self.results_text.insert(tk.END, f"{crit_val:6.3f}  ")
        self.results_text.insert(tk.END, "\n")

    def test_hypothesis(self):
        """Пункт 11: Проверка гипотезы"""
        self.results_text.insert(tk.END, "\n" + "=" * 60 + "\n")
        self.results_text.insert(tk.END, "=== ПРОВЕРКА ГИПОТЕЗЫ ===\n\n")

        self.results_text.insert(tk.END, f"χ²_набл = {self.chi2_observed:.4f}\n")
        self.results_text.insert(tk.END, f"χ²_крит = {self.chi2_critical:.4f}\n\n")

        if self.chi2_observed < self.chi2_critical:
            self.results_text.insert(tk.END,
                                     f"✅ χ²_набл < χ²_крит ({self.chi2_observed:.4f} < {self.chi2_critical:.4f})\n")
            self.results_text.insert(tk.END,
                                     f"Гипотеза о равномерном распределении НЕ ОТВЕРГАЕТСЯ на уровне значимости α={self.alpha}\n")
        else:
            self.results_text.insert(tk.END,
                                     f"❌ χ²_набл ≥ χ²_крит ({self.chi2_observed:.4f} ≥ {self.chi2_critical:.4f})\n")
            self.results_text.insert(tk.END,
                                     f"Гипотеза о равномерном распределении ОТВЕРГАЕТСЯ на уровне значимости α={self.alpha}\n")

        # P-value
        if self.df > 0:
            p_value = 1 - stats.chi2.cdf(self.chi2_observed, self.df)
            self.results_text.insert(tk.END, f"\nP-value = {p_value:.6f}")
            if p_value < 0.001:
                self.results_text.insert(tk.END, " (очень значимо)")

    # ====================== ГРАФИКИ ======================

    def show_graphs(self):
        """Пункт 5: Построение графиков"""
        if not self.intervals:
            messagebox.showwarning("Нет данных", "Сначала введите данные и выполните расчёт!")
            return

        # Создаём новое окно для графиков
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Графики распределения")
        graph_window.geometry("900x600")

        # Создаём фигуру matplotlib
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 10))

        # Подготовка данных для гистограммы
        bin_edges = []
        heights = []

        # Для гистограммы относительных частот
        relative_freqs = [freq / self.n_total for freq in self.frequencies]

        for (left, right, li, ri), rel_freq in zip(self.intervals, relative_freqs):
            bin_edges.append(left)
            heights.append(rel_freq)

        # Добавляем правую границу последнего интервала
        last_right = self.intervals[-1][1]
        bin_edges.append(last_right)

        # Ширина интервалов
        widths = [bin_edges[i + 1] - bin_edges[i] for i in range(len(bin_edges) - 1)]

        # 1. Гистограмма относительных частот
        ax1.bar(bin_edges[:-1], heights, width=widths, align='edge',
                alpha=0.6, color='lightblue', edgecolor='blue', label='Относительные частоты')

        # Ломаная линия через середины интервалов
        midpoints = [(bin_edges[i] + bin_edges[i + 1]) / 2 for i in range(len(bin_edges) - 1)]
        ax1.plot(midpoints, heights, 'ro-', linewidth=2, markersize=6, label='Ломаная частот')

        # 2. Теоретическая плотность равномерного распределения
        x_theor = np.linspace(min(bin_edges), max(bin_edges), 500)
        y_theor = np.where((x_theor >= self.a_est) & (x_theor <= self.b_est),
                           1 / (self.b_est - self.a_est), 0)

        ax1.plot(x_theor, y_theor, 'g-', linewidth=2, label=f'Равномерное U({self.a_est:.2f}, {self.b_est:.2f})')

        ax1.set_xlabel('Значения X')
        ax1.set_ylabel('Относительная частота / Плотность')
        ax1.set_title('Гистограмма относительных частот и теоретическая плотность')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 3. Функция распределения (дополнительный график)
        x_f = np.linspace(min(bin_edges) - 1, max(bin_edges) + 1, 500)
        y_f = np.where(x_f < self.a_est, 0,
                       np.where(x_f > self.b_est, 1,
                                (x_f - self.a_est) / (self.b_est - self.a_est)))

        ax2.plot(x_f, y_f, 'b-', linewidth=2, label='Теоретическая F(x)')

        # Эмпирическая функция распределения
        cum_freq = 0
        for i, ((left, right, li, ri), freq) in enumerate(zip(self.intervals, self.frequencies)):
            if i == 0:
                ax2.plot([left, left], [0, cum_freq / self.n_total], 'r--', alpha=0.7)
            cum_freq += freq
            ax2.plot([right, right], [0, cum_freq / self.n_total], 'r--', alpha=0.7)
            if i < len(self.intervals) - 1:
                next_left = self.intervals[i + 1][0]
                ax2.plot([right, next_left], [cum_freq / self.n_total, cum_freq / self.n_total], 'r-', alpha=0.7)

        ax2.set_xlabel('Значения X')
        ax2.set_ylabel('F(x)')
        ax2.set_title('Теоретическая и эмпирическая функции распределения')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Настройка компоновки
        plt.tight_layout()

        # Встраиваем график в Tkinter окно
        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Кнопка для сохранения графика
        ttk.Button(graph_window, text="Сохранить график",
                   command=lambda: self.save_figure(fig)).pack(pady=5)

    def save_figure(self, fig):
        """Сохранение графика в файл"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("Все файлы", "*.*")]
        )
        if filepath:
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Сохранено", f"График сохранён в файл:\n{filepath}")


# ====================== ЗАПУСК ПРИЛОЖЕНИЯ ======================

def main():
    root = tk.Tk()
    app = UniformDistributionTester(root)
    root.mainloop()


if __name__ == "__main__":
    main()
