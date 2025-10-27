from math import inf, factorial


def prod_with_pows(data, pows):
    prod = 1
    for i in range(len(data)):
        prod *= data[i] ** pows[i]
    return prod


def input_num_limit(lower_limit=0, upper_limit=inf, type_int=True, strong=True):
    """Функция ввода int-значения с проверкой на ограничение снизу и сверху \n
    lower_limit - нижняя граница (не включительно) [int] \n
    upper_limit - верхняя граница (не включительно) [int] \n

    return None"""

    while True:
        try:
            n = int(input()) if type_int else float(input())
        except ValueError:
            print("""Ошибка ввода, неверный тип входного значения.
>>> """, end="")
            continue
        if (lower_limit < n < upper_limit and strong) or (lower_limit <= n <= upper_limit and not strong):
            return n
        print(f"""Ошибка ввода, значение не удовлетворяет ограничениям ({lower_limit} < значение < {upper_limit}).
>>> """, end="")


def combinations_non_repeatable(n, m):
    """Сочетания без повторений"""
    return factorial(n) // (factorial(n - m) * factorial(m))


def bernoulli_formula(test_total, favorable, probability):
    """Считает формулу Бернулли"""

    return (combinations_non_repeatable(test_total, favorable) * (probability ** favorable)
            * ((1 - probability) ** (test_total - favorable)))


def bernoulli_task(n, m1, m2, p):
    """Считает вероятность получения благоприятных исходов из допустимого диапазона в серии независимых испытаний"""

    P = 0
    for i in range(m1, m2 + 1):
        P += bernoulli_formula(n, i, p)

    return P


def input_sub_n(count, n, name='n'):
    """Ввод многих значений sub_n, проверка на то, что их сумма равна n"""
    data = []
    print(f"""Введите значения {name}1, {name}2, ..., {name}k такие, что {name}1 + {name}2 + ... + {name}k = n
>>> """, end="")
    while True:
        a = input_num_limit(upper_limit=n)
        for i in range(count - 1):
            data.append(a)
            print(">>> ", end="")
            a = input_num_limit(upper_limit=n)
        data.append(a)
        if sum(data) == n:
            return data
        else:
            data = []
            print(f"""Неверное условие, сумма значений {name}1, {name}2, ..., {name}k должна равняться n, попробуйте еще раз.
>>> """, end="")


def input_sub_prob(count, name='n'):
    """Ввод многих значений probabilities, проверка на то, что их сумма равна 1"""
    data = []
    print(f"""Введите значения {name}1, {name}2, ..., {name}k такие, что {name}1 + {name}2 + ... + {name}k = 1, значение p = [0..1]
>>> """, end="")
    while True:
        a = input_num_limit(lower_limit=0, upper_limit=1, type_int=False, strong=False)
        for i in range(count - 1):
            data.append(a)
            print(">>> ", end="")
            a = input_num_limit(lower_limit=0, upper_limit=1, type_int=False, strong=False)
        data.append(a)
        if sum(data) == 1:
            return data
        else:
            data = []
            print(f"""Неверное условие, сумма значений {name}1, {name}2, ..., {name}k должна равняться 1, попробуйте еще раз.
>>> """, end="")


def product_of_factorials(numbers):
    """Функция считает произведение факториалов"""
    prod = 1
    for number in numbers:
        prod *= factorial(number)
    return prod


def permutations_repeatable(total, sub_n):
    """Перестановки с повторением"""
    return factorial(total) // product_of_factorials(sub_n)
