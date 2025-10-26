import sys
from math import factorial
from msvcrt import getch

from Task1 import input_params, input_int_limit, combinations_non_repeatable, replacement_non_repeatable, input_sub_n, \
    product_of_factorials


def prod(data):
    prod = 1
    for i in data:
        prod *= i
    return prod


def main():
    print("""------------------------------------------------
Выберите номер решаемой типовой задачи:
1. Задача о дефектных деталях.
2. Задача про операторов и приборы.
3. Задача про телеграммы и каналы связи.
4. Задача про телеграммы (разное количество телеграмм).
5. Задача про элементы в ящике.
""", end="")
    comb_type = input_params(('1', '2', '3', '4', '5'))

    if comb_type == '1':
        print("""Введите общее число деталей k:
>>> """, end="")
        k = input_int_limit()
        print("""Введите число дефектных деталей l <= k:
>>> """, end="")
        l = input_int_limit(upper_limit=k+1)
        print("""Введите число деталей для контроля r <= k:
>>> """, end="")
        r = input_int_limit(upper_limit=k+1)
        print("""Введите число дефектных деталей в выборке S <= r:
>>> """, end="")
        S = input_int_limit(upper_limit=r+1)
        print(f"""Выбранная задача: <<Задача о дефектных деталях>>
Формула: P = (C(l, S) * C(k - l, r - S)) / C(k, r)
Ответ: P = {(combinations_non_repeatable(l, S) * combinations_non_repeatable(k - l, r - S))
            / combinations_non_repeatable(k, r)}""")

    elif comb_type == '2':
        print("""Введите общее число операторов m:
>>> """, end="")
        m = input_int_limit()
        print("""Введите число приборов n >= m:
>>> """, end="")
        n = input_int_limit(lower_limit=m-1)
        print(f"""Выбранная задача: <<Задача про операторов и приборы>>
Формула: P = 1 / C(n, m)
Ответ: P = {1 / combinations_non_repeatable(n, m)}""")

    elif comb_type == '3':
        print("""Введите общее число телеграмм m:
>>> """, end="")
        m = input_int_limit()
        print("""Введите число каналов связи n > m:
>>> """, end="")
        n = input_int_limit(lower_limit=m)
        print(f"""Выбранная задача: <<Задача про телеграммы и каналы связи>>
Формула: P = A(n, m) / n^m
Ответ: P = {replacement_non_repeatable(n, m) / n**m}""")

    elif comb_type == '4':
        print("""Введите общее число телеграмм m:
>>> """, end="")
        m = input_int_limit()
        print("""Введите число каналов связи n:
>>> """, end="")
        n = input_int_limit()
        ks = input_sub_n(m, name='m')
        print(f"""Выбранная задача: <<Задача про телеграммы (разное количество телеграмм)>>
Формула: P = m! / (k1! * k2! * ... * kn! * n^m)
Ответ: P = {factorial(m) / (product_of_factorials(ks) * n ** m)}""")

    elif comb_type == '5':
        print("""Введите общее число элементов K:
>>> """, end="")
        K = input_int_limit()
        print("""Введите общее число типов элементов m:
>>> """, end="")
        m = input_int_limit()
        ks = input_sub_n(K, name='K')
        print("""Введите общее число элементов, которые выбирают наугад n:
>>> """, end="")
        n = input_int_limit(upper_limit=K+1)
        ns = input_sub_n(n)
        print(f"""Выбранная задача: <<Задача про элементы в ящике>>
Формула: P = (П [от i=1 до m] (C(ki, ni))) / C(K, n)
Ответ: P = {prod(list(combinations_non_repeatable(ks[i], ns[i]) for i in range(1, m))) /
            combinations_non_repeatable(K, n)}""")

    print("Нажмите любую клавишу, чтобы завершить программу!")
    if getch() == b'\r':
        sys.exit(0)


if __name__ == '__main__':
    main()
