from _utils import input_num_limit, bernoulli_formula, bernoulli_task, input_sub_n, input_sub_prob, \
    permutations_repeatable, prod_with_pows


def main():
    Ps = []

    print("=" * 60)
    print("ЗАДАНИЕ 1: Применение формулы Бернулли и полиномиальной формулы.")
    print("=" * 60)

    print("""Часть первая: программа, позволяющая вычислить вероятность событий по формуле Бернулли:
P(n, k=m),
P(n, k<m),
P(n, k>m),
P(n, m1 <= k <= m2).

Пусть q = 1 - p, тогда:
    Формула Бернулли: P(n, m) = C(n, m) ⋅ p^m ⋅ q^(n-m)

Введите число испытаний (n > 0):
>>> """, end="")
    n = input_num_limit()
    print("""Введите вероятность благоприятного исхода испытания (0 <= p <= 1):
>>> """, end="")
    p = input_num_limit(lower_limit=0, upper_limit=1, type_int=False, strong=False)
    print("""Введите количество испытаний, завершившихся с благоприятным исходом (0 <= m <= n):
>>> """, end="")
    m = input_num_limit(upper_limit=n, strong=False)
    print("""Введите диапазон допустимых благоприятных исходов, для вычисления Pn(m1 <= k <= m2)
Введите m1 (0 <= m1 <= n):
>>> """, end="")
    m1 = input_num_limit(upper_limit=n, strong=False)
    print("""Введите m2 (m1 <= m2 <= n):
>>> """, end="")
    m2 = input_num_limit(lower_limit=m1, upper_limit=n, strong=False)

    Ps.append(bernoulli_formula(n, m, p))
    Ps.append(bernoulli_task(n, 0, m - 1, p))
    Ps.append(bernoulli_task(n, m, n, p))
    Ps.append(bernoulli_task(n, m1, m2, p))

    print("""Выберите требуемые для вывода типы событий. Введите их номера через пробел:
1. P(n, k=m)
2. P(n, k<m)
3. P(n, k>m)
4. P(n, m1 <= k <= m2).
Для того, чтобы вывести результат всех четырех событий для введенных значений, введите '0':""")

    request = ('0', '1', '2', '3', '4')
    while True:
        print(">>> ", end="")
        param = input().split()

        for i in param:
            if i not in request:
                break
        else:
            if param[0] == '0':
                print(f"""P(n, k=m) = {Ps[0]:.6f}
P(n, k<m) = {Ps[1]:.6f}
P(n, k>m) = {Ps[2]:.6f}
P(n, m1 <= k <= m2) = {Ps[3]:.6f}""")
                break
            param = sorted(set(param))
            for i in param:
                if i == '1':
                    print(f"1. P(n, k=m) = {Ps[0]:.6f}")
                elif i == '2':
                    print(f"2. P(n, k<m) = {Ps[1]:.6f}")
                elif i == '3':
                    print(f"3. P(n, k>m) = {Ps[2]:.6f}")
                elif i == '4':
                    print(f"4. P(n, m1 <= k <= m2) = {Ps[3]:.6f}")

            break
        print("Ошибка ввода, неверное значение. Введите одно из предложенных значений.")

    print("=" * 60)
    print("""Часть вторая: программа, позволяющая вычислить вероятности событий по полиномиальной формуле:""")
    print("""Введите число испытаний (n > 0):
>>> """, end="")
    n = input_num_limit()
    print("""Введите число количество исходов испытания (k > 0):
>>> """, end="")
    k = input_num_limit()
    ms = input_sub_n(k, n, 'm')
    print("""Введите вероятности исходов испытания:""")
    ps = input_sub_prob(k, 'p')
    print("""Расчётная формула решения задачи: 
P(n, m1, m2, ..., mk) = (n!/(m1! ⋅ m2! ⋅ ... ⋅ mk!)) ⋅ p1^m1 ⋅ p2^m2 ⋅ ... ⋅ pk^mk = 
= P~(n, m1, m2, ..., mk) ⋅ p1^m1 ⋅ p2^m2 ⋅ ... ⋅ pk^mk""")
    print(permutations_repeatable(n, ms))
    P = permutations_repeatable(n, ms) * prod_with_pows(ps, ms)
    print(f"""Ответ: P = {P:.6f}""")


if __name__ == "__main__":
    main()
