import sys
from math import factorial, inf
from msvcrt import getch


def input_params(request):
    """Функция ввода параметров типа решаемой задачи"""

    while True:
        print(">>> ", end="")
        param = input()

        if param in request:
            return param
        print("Ошибка ввода, неверное значение. Введите одно из предложенных значений.")


def input_int_limit(lower_limit=0, upper_limit=inf):
    """Функция ввода int-значения с проверкой на ограничение снизу и сверху"""

    while True:
        try:
            n = int(input())
        except ValueError:
            print("""Ошибка ввода, неверный тип входного значения.
>>> """, end="")
            continue
        if lower_limit < n < upper_limit:
            return n
        print(f"""Ошибка ввода, значение не удовлетворяет ограничениям ({lower_limit} < значение < {upper_limit}).
>>> """, end="")


def input_sub_n(n, name='n'):
    """Ввод многих значений sub_n, проверка на то, что их сумма равна значению n"""
    data = []
    print(
        f"""Введите целые значения {name}1, {name}2, ..., {name}k такие, что {name}1 + {name}2 + ... + {name}k = {name}, введенное раньше.
Для остановки ввода, введите '!'
>>> """, end="")
    while True:
        try:
            a = input()
            while a != '!':
                data.append(a)
                a = input()
            if sum(map(int, data)) == n:
                return list(map(int, data))
            else:
                data = []
                print(f"""Неверное условие, сумма значений {name}1, {name}2, ..., {name}k должна равняться общему числу элементов,
попробуйте еще раз.
>>> """, end="")
        except ValueError:
            data = []
            print("""Среди введенных значений есть не целое числовое значение, попробуйте еще раз.
>>> """, end="")


def input_nm(repeatable=False):
    print("""------------------------------------------------
Введите общее число элементов(n)
>>> """, end="")
    n = input_int_limit() if repeatable else input_int_limit(lower_limit=1)
    print("""------------------------------------------------
Введите число выборки(m). Оно должно быть меньше введенного n, если выбрана комбинация без повторений. 
>>> """, end="")
    m = input_int_limit() if repeatable else input_int_limit(upper_limit=n)
    return n, m


def product_of_factorials(numbers):
    """Функция считает произведение факториалов"""
    prod = 1
    for number in numbers:
        prod *= factorial(number)
    return prod


def permutations_non_repeatable(n):
    """Перестановки без повторений"""
    return factorial(n)


def permutations_repeatable(total, sub_n):
    """Перестановки с повторением"""
    return factorial(total) // product_of_factorials(sub_n)


def replacement_non_repeatable(n, m):
    """Размещения без повторений"""
    return factorial(n) // factorial(n - m)


def replacement_repeatable(n, m):
    """Размещения с повторением"""
    return n ** m


def combinations_non_repeatable(n, m):
    """Сочетания без повторений"""
    return factorial(n) // (factorial(n - m) * factorial(m))


def combinations_repeatable(n, m):
    """Сочетания с повторением"""
    return combinations_non_repeatable(n + m - 1, m)


def main():
    print("""------------------------------------------------
Выберите тип решаемой комбинации:
1 - Перестановка P(n);
2 - Размещение A(n, m);
3 - Сочетание C(n, m).
""", end="")
    comb_type = input_params(('1', '2', '3'))

    print("""------------------------------------------------
Введите тип комбинации (с повторением или без):
1 - комбинация без повторения;
2 - комбинация с повторением.
""", end="")
    repeatable = bool(int(input_params(('1', '2'))) - 1)

    if comb_type == '1' and not repeatable:
        print("""------------------------------------------------
Введите общее число элементов(n)
>>> """, end="")
        n = input_int_limit()
        print("""Выбранный тип комбинации: перестановки без повторений, P(n) = n!.
Ответ:""", permutations_non_repeatable(n))

    elif comb_type == '1' and repeatable:
        print("""------------------------------------------------
Введите общее число элементов(n)
>>> """, end="")
        n = input_int_limit()
        sub_n = input_sub_n(n)
        print("""Выбранный тип комбинации: перестановки c повторениями, 
P~(n, n1, n2, ..., nk) = n/(n1! * n2! * ... * nk!).
Ответ:""", permutations_repeatable(n, sub_n))

    elif comb_type == '2' and not repeatable:
        n, m = input_nm()
        print("""Выбранный тип комбинации: размещения без повторений, A(n, m) = n!/(n - m)!.
Ответ:""", replacement_non_repeatable(n, m))

    elif comb_type == '2' and repeatable:
        n, m = input_nm(repeatable=True)
        print("""Выбранный тип комбинации: размещения с повторением, A~(n, m) = n ** m.
Ответ:""", replacement_repeatable(n, m))

    elif comb_type == '3' and not repeatable:
        n, m = input_nm()
        print("""Выбранный тип комбинации: сочетания без повторений, C(n, m) = n!/(m!(n - m)!).
Ответ:""", combinations_non_repeatable(n, m))

    elif comb_type == '3' and repeatable:
        n, m = input_nm(repeatable=True)
        print("""Выбранный тип комбинации: сочетания с повторением, С~(n, m) = C(n + m - 1, m).
Ответ:""", combinations_repeatable(n, m))

    print("Нажмите любую клавишу, чтобы завершить программу!")
    if getch() == b'\r':
        sys.exit(0)


if __name__ == '__main__':
    main()
