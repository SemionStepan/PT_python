from math import inf

from _utils import input_num_limit, input_sub_n, input_params


def main():
    print("=" * 60)
    print("ЗАДАНИЕ 4: Формулы полной вероятности и Байеса.")
    print("=" * 60)

    print("""1. Введите число событий, образующих полную группу:
>>> """, end="")
    n = input_num_limit(lower_limit=1)
    print("""Укажите вероятности событий, образующих полную группу(гипотез):""")
    His = input_sub_n(n, "P(H")

    Phas = []
    for i in range(len(His)):
        print(f"Введите вероятность A, зависимую от H{i + 1}: ", end="")
        Pha = input_num_limit(lower_limit=0, upper_limit=1, type_int=False, strong=False)
        Phas.append(Pha)

    print("""2. Выберите формулу для вычислений:
  1 - формула полной вероятности;
  2 - формула Байеса;
  3 - посчитать всё.""")
    form = input_params(('1', '2', '3'))

    P = 0
    for i in range(n):
        P += Phas[i] * His[i]
    Pahs = []
    for i in range(n):
        Pahs.append((Phas[i] * P) / His[i])

    if form == '1':
        print(f"""Выбрана формула полной вероятности: P(A) = ∑ ([i от 1 до n] | P(A | Hi) ⋅ P(Hi))
P(A) = {P:.6f}""")

    elif form == '2':
        print("""Выбрана формула Байеса: P(Hi | A) = (P(A | Hi) ⋅ P(A)) / P(Hi).
Выберите условные вероятности, которые следует рассчитать: укажите номера требуемых гипотез через пробел [1..n],
если требуется вывести все вероятности, введите '0'.""")
        request = set(map(str, range(1, n + 1)))
        request.add('0')
        while True:
            print(">>> ", end="")
            param = input().split()

            for i in param:
                if i not in request:
                    break
            else:
                if param[0] == '0':
                    print("\n".join([f"P(H{i + 1} | A) = {Pahs[i]:.6f}" for i in range(n)]))
                    break
                else:
                    print("\n".join([f"P(H{int(i)} | A) = {Pahs[int(i) - 1]:.6f}" for i in param]))
                    break
            print("Ошибка ввода, неверное значение. Введите одно из предложенных значений.")

    else:
        print(f"""Формула полной вероятности: P(A) = ∑ ([i от 1 до n] | P(A | Hi) ⋅ P(Hi))
Формула Байеса: P(Hi | A) = (P(A | Hi) ⋅ P(A)) / P(Hi)
P(A) = {P:.6f}""")
        print("\n".join([f"P(H{i + 1} | A) = {Pahs[i]:.6f}" for i in range(n)]))


if __name__ == "__main__":
    main()
