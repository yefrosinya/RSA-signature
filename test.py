#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы RSA Signature
"""
import sys
import os

# Добавляем путь к src в PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Тестируем импорты всех модулей"""
    try:
        from src.utils.math_utils import MathUtils
        from src.crypto.rsa_algorithm import RSAAlgorithm
        from src.crypto.hash_calculator import HashCalculator
        from src.utils.file_manager import FileManager
        from src.gui.rsa_signature_gui import RSASignatureGUI
        print("✅ Все модули импортированы успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_rsa_functionality():
    """Тестируем основную функциональность RSA"""
    try:
        from src.crypto.rsa_algorithm import RSAAlgorithm
        from src.crypto.hash_calculator import HashCalculator
        
        # Тестируем с простыми числами
        rsa = RSAAlgorithm(61, 53)  # p=61, q=53
        e, d = rsa.generate_key_pair(17)  # e=17
        
        # Тестируем подпись
        hash_calc = HashCalculator(rsa.n)
        message = b"Test message"
        h, _ = hash_calc.calculate_hash(message)
        signature = rsa.sign(h)
        
        # Тестируем проверку
        is_valid = rsa.verify_signature(h, signature)
        
        if is_valid:
            print("✅ RSA функциональность работает корректно")
            return True
        else:
            print("❌ RSA проверка подписи не работает")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка RSA функциональности: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🧪 Тестирование RSA Signature приложения...")
    print()
    
    # Тест импортов
    if not test_imports():
        return
    
    # Тест функциональности
    if not test_rsa_functionality():
        return
    
    print()
    print("🎉 Все тесты пройдены успешно!")
    print("Приложение готово к использованию.")
    print()
    print("Для запуска GUI используйте: python3 run.py")

if __name__ == "__main__":
    main()
