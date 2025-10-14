from math import inf


def input_int_limit(lower_limit=0, upper_limit=inf):
    """Функция ввода int-значения с проверкой на ограничение снизу и сверху \n
    lower_limit - нижняя граница (не включительно) [int] \n
    upper_limit - верхняя граница (не включительно) [int] \n

    return None"""

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
