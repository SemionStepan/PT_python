import Task1
def main():
    print("=" * 60)
    print("ЗАДАНИЕ 1: Нахождение вероятности безотказной работы схемы")
    print("=" * 60)
    print("Схема:")
    print("  A1 -- A2")
    print("   |     |")
    print("  A3 -- A4")
    print()
    print("Событие B - схема работает безотказно в течение времени T")
    print("Событие Ai - i-ый элемент работает безотказно")
    print()
    
    # Пункт 1: Формула для события B через события Ai
    print("1. ФОРМУЛА ДЛЯ СОБЫТИЯ B:")
    print("B = (A1 ∩ A2) ∪ (A3 ∩ A4) ∪ (A1 ∩ A4) ∪ (A2 ∩ A3)")
    print("Обоснование: Схема работает, если есть путь из левого верхнего")
    print("в правый нижний угол через работающие элементы.")
    print()
    
    # Пункт 2: Формула для вероятности P(B)
    print("2. ФОРМУЛА ДЛЯ ВЕРОЯТНОСТИ P(B):")
    print("P(B) = P(A1)P(A2) + P(A3)P(A4) + P(A1)P(A4) + P(A2)P(A3)")
    print("     - P(A1)P(A2)P(A3) - P(A1)P(A2)P(A4) - P(A1)P(A3)P(A4)")
    print("     - P(A2)P(A3)P(A4) + P(A1)P(A2)P(A3)P(A4)")
    print("Обоснование: Применена формула включений-исключений для")
    print("объединения четырех событий.")
    print()
    
    # Ввод вероятностей
    print("3. ВВОД ВЕРОЯТНОСТЕЙ РАБОТЫ ЭЛЕМЕНТОВ:")
    probabilities = {}
    
    for i in range(1, 5):
        while True:
            try:
                p = float(input(f"Введите P(A{i}) [0-1]: "))
                if 0 <= p <= 1:
                    probabilities[f'A{i}'] = p
                    break
                else:
                    print("Ошибка: вероятность должна быть в диапазоне [0, 1]")
            except ValueError:
                print("Ошибка: введите число")
    
    # Вычисление P(B)
    p1, p2, p3, p4 = probabilities['A1'], probabilities['A2'], probabilities['A3'], probabilities['A4']
    
    # По формуле включений-исключений для объединения 4 событий
    P_B = (p1*p2 + p3*p4 + p1*p4 + p2*p3 
           - p1*p2*p3 - p1*p2*p4 - p1*p3*p4 - p2*p3*p4 
           + p1*p2*p3*p4)
    
    print()
    print("4. РЕЗУЛЬТАТ:")
    print(f"P(A1) = {p1:.4f}")
    print(f"P(A2) = {p2:.4f}") 
    print(f"P(A3) = {p3:.4f}")
    print(f"P(A4) = {p4:.4f}")
    print(f"P(B) = {P_B:.6f}")
    print(f"P(отказ) = {1-P_B:.6f}")
    
    # Тестирование
    print()
    print("5. ТЕСТИРОВАНИЕ:")
    print("Тест 1: Все элементы надежны (P=1)")
    p_test = 1.0
    P_B_test = 4*p_test**2 - 6*p_test**3 + 4*p_test**4
    print(f"P(B) = {P_B_test:.6f} (ожидается 1.000000)")
    
    print("Тест 2: Все элементы ненадежны (P=0)")
    p_test = 0.0
    P_B_test = 4*p_test**2 - 6*p_test**3 + 4*p_test**4
    print(f"P(B) = {P_B_test:.6f} (ожидается 0.000000)")


if __name__ == "__main__":
    main()
