import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class StatisticsAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ статистических данных")
        self.root.geometry("1200x800")

        self.data = None
        self.variation_series = None
        self.frequency_dict = None
        self.relative_freq_dict = None

        self.setup_ui()

    def setup_ui(self):
        # Создаем меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Загрузить данные", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Панель управления
        control_frame = ttk.LabelFrame(main_frame, text="Управление", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        buttons = [
            ("Вариационный ряд", self.show_variation_series),
            ("Ряд частот/отн. частот", self.show_frequency_series),
            ("Полигоны частот", self.show_frequency_polygons),
            ("Эмпирическая функция", self.show_empirical_function),
            ("Числовые характеристики", self.show_numerical_characteristics),
            ("Полный отчет", self.generate_full_report)
        ]

        for i, (text, command) in enumerate(buttons):
            ttk.Button(control_frame, text=text, command=command).grid(
                row=i // 3, column=i % 3, padx=5, pady=5, sticky=tk.W)

        # Область вывода результатов
        self.result_text = tk.Text(main_frame, width=80, height=25, wrap=tk.WORD)
        self.result_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.result_text.config(yscrollcommand=scrollbar.set)

        # Область для графиков
        self.graph_frame = ttk.Frame(main_frame)
        self.graph_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        # Информационная панель
        info_frame = ttk.LabelFrame(main_frame, text="Информация", padding="10")
        info_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))

        info_text = """
        Инструкция:
        1. Загрузите данные из файла (CSV или TXT)
        2. Выберите нужный пункт анализа
        3. Результаты отобразятся в текстовом поле
        4. Графики появятся в нижней части окна

        Поддерживаемые форматы:
        - CSV с одним столбцом данных
        - TXT с числами через пробел или запятую
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()

        # Настройка расширения
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

    def load_data(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                # Берем первый столбец
                self.data = df.iloc[:, 0].dropna().values
            else:
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Пытаемся разобрать числа, разделенные пробелами или запятыми
                    numbers = []
                    for part in content.replace(',', ' ').split():
                        try:
                            numbers.append(float(part))
                        except:
                            continue
                    self.data = np.array(numbers)

            if len(self.data) == 0:
                messagebox.showerror("Ошибка", "Не удалось загрузить данные")
                return

            if len(self.data) > 100:
                messagebox.showwarning("Предупреждение",
                                       f"Загружено {len(self.data)} значений (рекомендуется до 100)")

            self.process_data()
            self.display_message(f"Загружено {len(self.data)} значений\n"
                                 f"Диапазон: [{min(self.data):.2f}, {max(self.data):.2f}]")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def process_data(self):
        """Обработка данных после загрузки"""
        self.variation_series = np.sort(self.data)

        # Статистический ряд частот
        freq_counter = Counter(self.variation_series)
        self.frequency_dict = dict(sorted(freq_counter.items()))

        # Статистический ряд относительных частот
        n = len(self.data)
        self.relative_freq_dict = {k: v / n for k, v in self.frequency_dict.items()}

    def display_message(self, message):
        """Отображение сообщения в текстовом поле"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, message)

    def show_variation_series(self):
        """Показать вариационный ряд"""
        self.setup_ui()

        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        vs_text = "ВАРИАЦИОННЫЙ РЯД:\n"
        vs_text += "=" * 50 + "\n"

        # Показываем по 10 значений в строке
        for i in range(0, len(self.variation_series), 10):
            chunk = self.variation_series[i:i + 10]
            line = "  ".join(f"{x:.4f}" for x in chunk)
            vs_text += line + "\n"

        vs_text += "\n" + "=" * 50 + "\n"
        vs_text += f"Объем выборки: n = {len(self.variation_series)}\n"
        vs_text += f"Минимальное значение: x_min = {min(self.variation_series):.4f}\n"
        vs_text += f"Максимальное значение: x_max = {max(self.variation_series):.4f}\n"
        vs_text += f"Размах: R = {max(self.variation_series) - min(self.variation_series):.4f}"

        self.display_message(vs_text)

    def show_frequency_series(self):
        """Показать ряды частот и относительных частот"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return
        text = "СТАТИСТИЧЕСКИЕ РЯДЫ\n"
        text += "=" * 70 + "\n"
        text += f"{'Варианта (x_i)':<15} {'Частота (n_i)':<15} {'Отн. частота (w_i)':<20}\n"
        text += "-" * 70 + "\n"

        self.setup_ui()

        for x in self.frequency_dict:
            freq = self.frequency_dict[x]
            rel_freq = self.relative_freq_dict[x]
            text += f"{x:<15.4f} {freq:<15} {rel_freq:<20.6f}\n"

        text += "=" * 70 + "\n"
        text += f"Сумма частот: {sum(self.frequency_dict.values())}\n"
        text += f"Сумма относительных частот: {sum(self.relative_freq_dict.values()):.6f}"

        self.display_message(text)

    def show_frequency_polygons(self):
        """Построить полигоны частот"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        # Очищаем область графиков
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Полигон частот
        x_values = list(self.frequency_dict.keys())
        y_freq = list(self.frequency_dict.values())

        ax1.plot(x_values, y_freq, 'bo-', linewidth=2, markersize=6)
        ax1.fill_between(x_values, y_freq, alpha=0.3)
        ax1.set_xlabel('Значения вариант (x_i)', fontsize=12)
        ax1.set_ylabel('Частота (n_i)', fontsize=12)
        ax1.set_title('Полигон частот', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Полигон относительных частот
        y_rel_freq = list(self.relative_freq_dict.values())

        ax2.plot(x_values, y_rel_freq, 'ro-', linewidth=2, markersize=6)
        ax2.fill_between(x_values, y_rel_freq, alpha=0.3, color='red')
        ax2.set_xlabel('Значения вариант (x_i)', fontsize=12)
        ax2.set_ylabel('Относительная частота (w_i)', fontsize=12)
        ax2.set_title('Полигон относительных частот', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        # Встраиваем график в tkinter
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Текстовое описание
        desc = "ПОЛИГОНЫ ЧАСТОТ:\n"
        desc += "=" * 50 + "\n"
        desc += "Полигон частот - ломаная, соединяющая точки (x_i, n_i)\n"
        desc += "Полигон относительных частот - ломаная, соединяющая точки (x_i, w_i)\n"
        desc += "где x_i - варианты, n_i - частоты, w_i = n_i/n - относительные частоты"

        self.display_message(desc)

    def show_empirical_function(self):
        """Найти и построить эмпирическую функцию распределения"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        # Очищаем область графиков
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        # Создаем эмпирическую функцию распределения
        sorted_values = sorted(self.relative_freq_dict.items())
        x_points = []
        y_points = []

        cum_prob = 0
        for x, w in sorted_values:
            x_points.append(x)
            y_points.append(cum_prob)
            cum_prob += w
            x_points.append(x)
            y_points.append(cum_prob)

        # Добавляем крайние точки
        x_points = [min(x_points) - 1] + x_points + [max(x_points) + 1]
        y_points = [0] + y_points + [1]

        # Строим график
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.step(x_points, y_points, where='post', linewidth=2, color='purple')
        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('F*(x)', fontsize=12)
        ax.set_title('Эмпирическая функция распределения F*(x)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-0.05, 1.05)

        # Добавляем точки разрыва
        for i in range(1, len(x_points) - 1, 2):
            ax.plot(x_points[i], y_points[i], 'go', markersize=8)
            ax.plot(x_points[i], y_points[i + 1], 'ro', markersize=8, fillstyle='none')

        plt.tight_layout()

        # Встраиваем график в tkinter
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Текстовое определение функции
        text = "ЭМПИРИЧЕСКАЯ ФУНКЦИЯ РАСПРЕДЕЛЕНИЯ F*(x)\n"
        text += "=" * 70 + "\n\n"
        text += "Определение:\n"
        text += "F*(x) = (число вариант, меньших x) / n\n\n"
        text += "Конкретный вид для данной выборки:\n"
        text += "F*(x) = {\n"

        cum_prob = 0
        sorted_items = sorted(self.relative_freq_dict.items())

        for i, (x, w) in enumerate(sorted_items):
            if i == 0:
                text += f"        0, при x ≤ {x:.4f}\n"
            else:
                prev_x = sorted_items[i - 1][0]
                text += f"        {cum_prob:.4f}, при {prev_x:.4f} < x ≤ {x:.4f}\n"
            cum_prob += w

        text += f"        {cum_prob:.4f}, при x > {sorted_items[-1][0]:.4f}\n"
        text += "}"

        self.display_message(text)

    def show_numerical_characteristics(self):
        """Вычислить числовые характеристики выборки"""

        self.setup_ui()

        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        n = len(self.data)

        # Выборочное среднее
        x_mean = np.mean(self.data)

        # Выборочная дисперсия
        # D_в = (1/n) * Σ(x_i - x_в)²
        D_v = np.var(self.data, ddof=0)

        # Исправленная дисперсия
        # S² = (1/(n-1)) * Σ(x_i - x_в)²
        S2 = np.var(self.data, ddof=1)

        # Выборочное среднее квадратическое отклонение
        sigma_v = np.sqrt(D_v)

        # Исправленное среднее квадратическое отклонение
        S = np.sqrt(S2)

        # Медиана
        median = np.median(self.data)

        # Мода
        if self.frequency_dict:
            mode_value = max(self.frequency_dict, key=self.frequency_dict.get)
            mode_freq = self.frequency_dict[mode_value]
        else:
            mode_value = None
            mode_freq = 0

        text = "ЧИСЛОВЫЕ ХАРАКТЕРИСТИКИ ВЫБОРКИ\n"
        text += "=" * 70 + "\n\n"

        text += "ФОРМУЛЫ:\n"
        text += "1. Выборочное среднее:\n"
        text += "   x_в = (1/n) * Σ x_i\n"
        text += "2. Выборочная дисперсия:\n"
        text += "   D_в = (1/n) * Σ (x_i - x_в)²\n"
        text += "3. Выборочное среднее квадратическое отклонение:\n"
        text += "   σ_в = √D_в\n"
        text += "4. Исправленная дисперсия:\n"
        text += "   S² = (1/(n-1)) * Σ (x_i - x_в)²\n"
        text += "5. Исправленное среднее квадратическое отклонение:\n"
        text += "   S = √S²\n\n"
        text += "=" * 70 + "\n\n"
        text += "РЕЗУЛЬТАТЫ:\n"
        text += f"Объем выборки: n = {n}\n"
        text += f"Выборочное среднее: x_в = {x_mean:.6f}\n"
        text += f"Выборочная дисперсия: D_в = {D_v:.6f}\n"
        text += f"Выборочное СКО: σ_в = {sigma_v:.6f}\n"
        text += f"Исправленная дисперсия: S² = {S2:.6f}\n"
        text += f"Исправленное СКО: S = {S:.6f}\n"
        text += f"Медиана: Me = {median:.6f}\n"

        if mode_value is not None:
            text += f"Мода: Mo = {mode_value:.4f} (частота: {mode_freq})\n"

        text += f"\nКоэффициент вариации: V = {(sigma_v / x_mean * 100):.2f}%"

        self.display_message(text)

    def generate_full_report(self):
        """Сгенерировать полный отчет"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные")
            return

        # Создаем новый файл для отчета
        report_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not report_file:
            return

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("ПОЛНЫЙ ОТЧЕТ ПО СТАТИСТИЧЕСКОМУ АНАЛИЗУ\n")
                f.write("=" * 80 + "\n\n")

                f.write(f"Дата анализа: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Объем выборки: n = {len(self.data)}\n\n")

                # Исходные данные
                f.write("1. ИСХОДНЫЕ ДАННЫЕ:\n")
                f.write("-" * 40 + "\n")
                f.write(str(self.data) + "\n\n")

                # Вариационный ряд
                f.write("2. ВАРИАЦИОННЫЙ РЯД:\n")
                f.write("-" * 40 + "\n")
                for i, val in enumerate(self.variation_series, 1):
                    f.write(f"{val:.4f} ")
                    if i % 10 == 0:
                        f.write("\n")
                f.write("\n\n")

                # Статистические ряды
                f.write("3. СТАТИСТИЧЕСКИЕ РЯДЫ:\n")
                f.write("-" * 40 + "\n")
                f.write(f"{'x_i':<15} {'n_i':<10} {'w_i':<15}\n")
                f.write("-" * 40 + "\n")
                for x in self.frequency_dict:
                    freq = self.frequency_dict[x]
                    rel_freq = self.relative_freq_dict[x]
                    f.write(f"{x:<15.4f} {freq:<10} {rel_freq:<15.6f}\n")
                f.write("\n")

                # Числовые характеристики
                f.write("4. ЧИСЛОВЫЕ ХАРАКТЕРИСТИКИ:\n")
                f.write("-" * 40 + "\n")
                x_mean = np.mean(self.data)
                D_v = np.var(self.data, ddof=0)
                sigma_v = np.sqrt(D_v)
                S2 = np.var(self.data, ddof=1)
                S = np.sqrt(S2)
                median = np.median(self.data)

                f.write(f"Выборочное среднее (x_в): {x_mean:.6f}\n")
                f.write(f"Выборочная дисперсия (D_в): {D_v:.6f}\n")
                f.write(f"Выборочное СКО (σ_в): {sigma_v:.6f}\n")
                f.write(f"Исправленная дисперсия (S²): {S2:.6f}\n")
                f.write(f"Исправленное СКО (S): {S:.6f}\n")
                f.write(f"Медиана (Me): {median:.6f}\n")
                f.write(f"Коэффициент вариации: {(sigma_v / x_mean * 100):.2f}%\n\n")

                f.write("=" * 80 + "\n")
                f.write("Отчет сгенерирован программой статистического анализа\n")

            messagebox.showinfo("Успех", f"Полный отчет сохранен в файл:\n{report_file}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить отчет: {str(e)}")


def main():
    root = tk.Tk()
    app = StatisticsAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()