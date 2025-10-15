from math import inf


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


def only_n_hits(total, shooters, probabilities):
    """Считает вероятность попадания в цель только n количеством стрелков. \n
    total - всего стрелков [int] \n
    shooters - номера стрелков, для которых следует рассчитать вероятность [iterable: int] \n
    probabilities - вероятности попадания для стрелков [dictionary: str -> float] \n

    return float"""

    P_b = 1
    n = len(shooters)

    for i in range(1, total + 1):
        P_b *= (1 - probabilities[f"p{i}"])
    for i in range(n):
        P_b /= (1 - probabilities[f"p{shooters[i]}"])

    P_a = P_b
    for i in range(n):
        P_a *= probabilities[f"p{shooters[i]}"]
    return P_a


def input_probabilities(n):
    """Ввод вероятностей для стрелков. \n
    n - всего стрелков [int] \n

    return dictionary["p{i}"] = int     i=[1..n]"""

    probabilities = {}

    for i in range(1, n + 1):
        while True:
            try:
                p = float(input(f"Введите p{i} [0-1]: "))
                if 0 <= p <= 1:
                    probabilities[f'p{i}'] = p
                    break
                else:
                    print("Ошибка: вероятность должна быть в диапазоне [0, 1]")
            except ValueError:
                print("Ошибка: введите число")
    return probabilities


def input_sub_n(count, name='n'):
    """Ввод многих значений sub_n, проверка на то, что их сумма равна 1"""
    data = []
    print(
        f"""Введите значения {name}1), {name}2), ..., {name}k) такие, что {name}1) + {name}2) + ... + {name}k) = 1, значение P(Hi) = [0..1]
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
            print(f"""Неверное условие, сумма значений {name}1), {name}2), ..., {name}k) должна равняться 1, попробуйте еще раз.
>>> """, end="")


def input_params(request):
    """Функция ввода параметров типа решаемой задачи"""

    while True:
        print(">>> ", end="")
        param = input()

        if param in request:
            return param
        print("Ошибка ввода, неверное значение. Введите одно из предложенных значений.")