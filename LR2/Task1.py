def main():
    print("=" * 60)
    print("ЗАДАНИЕ 1: Нахождение вероятности безотказной работы схемы")
    print("=" * 60)
    print("""Схема:
     - - - 2 - - - 
    |              |
1 -                 - 3
    |              |
     - 4 - 5 - 6 - 
Событие B - схема работает безотказно в течение времени T
Событие Bi - i-ый элемент работает с отказом
Событие Ai - i-ый элемент работает безотказно
""")

    print("""1. ФОРМУЛА ДЛЯ СОБЫТИЯ B:
B = A1 ⋅ A3 ⋅ A2 + A4 ⋅ A5 ⋅ A6
""")

    print("2. ФОРМУЛА ДЛЯ ВЕРОЯТНОСТИ P(B):")
    print("""P(B) = P(A1 ⋅ A3 ⋅ A2 + A1 ⋅ A3 ⋅ A4 ⋅ A5 ⋅ A6) = P(A1 ⋅ A3 ⋅ (A2 + A4 ⋅ A5 ⋅ A6)) = 
= P(A1) ⋅ P(A3) ⋅ (P(A2) + P(A4) ⋅ P(A5) ⋅ P(A6) - P(A2) ⋅ P(A4) ⋅ P(A5) ⋅ P(A6))
Для расчёта формулы, понадобится знать P(Ai). Поскольку событие Ai является дополнением события Bi, то:
P(Ai) = 1 - P(Bi)
""")

    print("3. ВВОД ВЕРОЯТНОСТЕЙ ОТКАЗА РАБОТЫ ЭЛЕМЕНТОВ (n = 6):")
    probabilities = {}

    for i in range(1, 7):
        while True:
            try:
                p = float(input(f"Введите P(B{i}) [0-1]: "))
                if 0 <= p <= 1:
                    probabilities[f'A{i}'] = 1 - p
                    break
                else:
                    print("Ошибка: вероятность должна быть в диапазоне [0, 1]")
            except ValueError:
                print("Ошибка: введите число")

    p1, p2, p3, p4, p5, p6 = probabilities['A1'], probabilities['A2'], probabilities['A3'], probabilities['A4'], \
    probabilities['A5'], probabilities['A6']

    P_B = (p1 * p3 * (p2 + p4 * p5 * p6 - p2 * p4 * p5 * p6))

    print("\n4. РЕЗУЛЬТАТ:")
    print(f"P(A1) = {p1:.4f}")
    print(f"P(A2) = {p2:.4f}")
    print(f"P(A3) = {p3:.4f}")
    print(f"P(A4) = {p4:.4f}")
    print(f"P(A5) = {p5:.4f}")
    print(f"P(A6) = {p6:.4f}")
    print(f"P(B) = {P_B:.6f}")


if __name__ == "__main__":
    main()
