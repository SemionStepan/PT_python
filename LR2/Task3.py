from itertools import combinations

from _utils import input_int_limit, only_n_hits, input_probabilities


def main():
    print("=" * 60)
    print("ЗАДАНИЕ 3: Выстрелы по цели.")
    print("=" * 60)

    print("""1. Введите количество стрелков:
>>> """, end="")
    n = input_int_limit(lower_limit=0)

    print(f"\n2. ВВОД ВЕРОЯТНОСТЕЙ ПОПАДАНИЯ (n = {n}):")
    probabilities = input_probabilities(n)

    print("""
3. Найдем вероятность попадания ТОЛЬКО выбранного стрелка.
Введите номер стрелка, который должен попасть:
>>> """, end="")
    shooter = input_int_limit(lower_limit=0, upper_limit=n + 1)
    print(f"""Ai - i-ый стрелок попал в цель.
Bi - никакой стрелок, кроме i, не попал в цель.
P(Bi) = ∏ ([j от 0 до n] | P(¬Aj)) / ¬Ai
P(A{shooter}) = P(A{shooter} ⋅ P(B{shooter}))""")

    P = only_n_hits(n, [shooter], probabilities)
    print(f"P(A) = {P:.6f}\n")

    print("""4. Найдем вероятность попадания ТОЛЬКО одного стрелка.
Сi - только i стрелков попали
P(C1) = ∑ ([i от 0 до n] | P(Ai))""")

    P = 0
    for i in range(1, n + 1):
        P += only_n_hits(n, [i], probabilities)
    print(f"P(C1) = {P:.6f}\n")

    print("""5. Найдем вероятность попадания ТОЛЬКО двух стрелков.
C2 - только два стрелка попали.""")
    #TODO: ДОПИСАТЬ ФОРМУЛУ

    P = 0
    for i in range(1, n):
        for j in range(i + 1, n + 1):
            P += only_n_hits(n, [i, j], probabilities)
    print(f"P(C2) = {P:.6f}\n")

    print("""6. Найдем вероятность попадания в цель хотя бы одного стрелка.
B - ни один стрелок не попал в цель.
D - хотя бы один стрелок попал в цель.
Событие D является дополнением события B -> P(D) = 1 - P(B)
P(B) = ∏ ([j от 0 до n] | P(¬Aj))""")
    P_b = 1
    for i in range(1, n + 1):
        P_b *= (1 - probabilities[f"p{i}"])
    print(f"P(D) = 1 - {P_b} = {1 - P_b:.6f}")

    print("""
7. Найдем вероятность попадания не менее четырех стрелков.""")

    if n < 4:
        print("""Введены данные о менее чем 4 стрелках, повторите попытку.
Введите количество стрелков:
>>> """, end="")
        n = input_int_limit(lower_limit=0)
        print(f"ВВОД ВЕРОЯТНОСТЕЙ ПОПАДАНИЯ (n = {n}):")
        probabilities = input_probabilities(n)

    print("""D - попали не менее 4-ех стрелков
P(D) = ∑([i от 4 до n] | P(Ci))""")

    P = 0
    shooters = tuple(range(1, n + 1))
    for length in range(4, n + 1):
        shooters_comb = list(combinations(shooters, length))

        for cur_comb in shooters_comb:
            P += only_n_hits(n, cur_comb, probabilities)
    print(f"P(D) = {P:.6f}")


if __name__ == '__main__':
    main()
