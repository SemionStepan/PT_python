from itertools import combinations

from _utils import input_num_limit, only_n_hits, input_probabilities


def main():
    print("=" * 60)
    print("ЗАДАНИЕ 3: Выстрелы по цели.")
    print("=" * 60)

    print("""1. Введите количество стрелков:
>>> """, end="")
    n = input_num_limit(lower_limit=0)

    print(f"\n2. ВВОД ВЕРОЯТНОСТЕЙ ПОПАДАНИЯ, p (n = {n}):")
    probabilities = input_probabilities(n)

    print("""
3. Найдем вероятность попадания ТОЛЬКО выбранного стрелка.
Введите номер стрелка, который должен попасть:
>>> """, end="")
    shooter = input_num_limit(lower_limit=0, upper_limit=n + 1)
    print(f"""pi - вероятность попадания i-ого стрелка
Ai - только i-ый стрелок попал в цель.
Bi - никакой стрелок не попал, если исключить из испытания i-ого стрелка.
P(Bi) = ∏ ([j от 1 до n] | P(¬pj)) / ¬pi
P(A{shooter}) = p{shooter} ⋅ P(B{shooter})""")

    P = only_n_hits(n, [shooter], probabilities)
    print(f"P(A) = {P:.6f}\n")

    print("""4. Найдем вероятность попадания ТОЛЬКО одного стрелка.
Сi - только i стрелков попали
P(C1) = ∑ ([i от 1 до n] | P(Ai))""")

    P = 0
    for i in range(1, n + 1):
        P += only_n_hits(n, [i], probabilities)
    print(f"P(C1) = {P:.6f}\n")

    print("""5. Найдем вероятность попадания ТОЛЬКО двух стрелков.
C2 - только два стрелка попали.
По аналогии с подсчетом для вероятности попадания только одного стрелка, найдем промежуточную вероятность исхода B, но уже для нескольких стрелков:
для этого достаточно добавить в знаменатель формулы P(Bij) вероятности стрелков, которых мы исключаем из испытания: 
P(Bij) = ∏ ([k от 1 до n] | ¬pk) / (¬pi ⋅ ¬pj)
Затем подставим получившееся значение в формулу P(Aij), но так же изменим ее для нескольких стрелков.
Здесь домножим P(Bij) на вероятности попадания всех нужных нам стрелков:
P(Aij) = pi ⋅ pj ⋅ P(Bij)
Переберем все возможные пары попавших стрелков и сложим их вероятности попасть (эти события несовместны). 
Получившая сумма и будет равна вероятности P(C2).
P(C2) = ∑ ([i от 1 до n] | P(Aij))""")

    P = 0
    for i in range(1, n):
        for j in range(i + 1, n + 1):
            P += only_n_hits(n, [i, j], probabilities)
    print(f"P(C2) = {P:.6f}\n")

    print("""6. Найдем вероятность попадания в цель хотя бы одного стрелка.
B - ни один стрелок не попал в цель.
D - хотя бы один стрелок попал в цель.
Событие D является дополнением события B -> P(D) = 1 - P(B)
P(B) = ∏ ([j от 1 до n] | P(¬pj))""")
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
        n = input_num_limit(lower_limit=0)
        print(f"ВВОД ВЕРОЯТНОСТЕЙ ПОПАДАНИЯ (n = {n}):")
        probabilities = input_probabilities(n)

    print("""D - попали не менее 4-ех стрелков
Следуя рассуждениям из пятого пункта:
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
