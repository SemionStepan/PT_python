from _utils import input_num_limit
from math import e, factorial


def main():
    print("=" * 60)
    print("ЗАДАНИЕ 2: Изучение предельных теорем в схеме Бернулли.")
    print("=" * 60)

    print("""Часть первая: программа для использования формулы Пуассона:
P(n, m) ≈ ((λ^m) / m!) ⋅ e^(-λ), где λ = np
Введите общее число испытаний (n > 0),
РЕКОМЕНДУЕТСЯ ВВОДИТЬ БОЛЬШЕ ЗНАЧЕНИЕ, n > 100:
>>> """, end="")
    n = input_num_limit()
    print("""Введите вероятность благоприятного исхода (0 <= p <= 1).
РЕКОМЕНДУЕТСЯ ВВОДИТЬ ЗНАЧЕНИЕ p МЕНЬШЕ ЧЕМ 1 ⋅ 10^(-3):
>>> """, end="")
    p = input_num_limit(upper_limit=1, type_int=False, strong=False)
    print("""Введите число благоприятных исходов (0 <= m <= n):
>>> """, end="")
    m = input_num_limit(upper_limit=n+1)
    P = (((n * p) ** m) / factorial(m)) * e ** (-1 * n * p)
    print(f"P(n, m) = {P:.6f}")


if __name__ == "__main__":
    main()
