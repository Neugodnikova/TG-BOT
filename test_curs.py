import unittest
from unittest.mock import patch
from curs import *

class TestCheckValuteFunction(unittest.TestCase):
    def test_existing_valute(self):
        valute = 'EUR'
        result = check_valute(valute)
        self.assertEqual(result, (valute, valutes_cb[valute]))

    def test_non_existing_valute(self):
        valute = 'XYZ'  # Предполагаем, что 'XYZ' отсутствует в valutes
        result = check_valute(valute)
        self.assertEqual(result, (False, False))

    def test_case_insensitive_valute(self):
        valute = 'usd'  # Проверяем, что функция регистрозависима
        result = check_valute(valute)
        self.assertEqual(result, (False, False))

class TestGetNowRubleCursesFunction(unittest.TestCase):
    @patch('curs.requests.get')
    def test_get_now_ruble_curses(self, mock_requests_get):
        # Создаем фиктивный ответ от сервера
        fake_response = {
            'Valute': {
                'USD': {'Value': 70.5},
                'EUR': {'Value': 80.0},
                # Другие валюты
            }
        }
        
        # Настраиваем фиктивный объект запроса
        mock_requests_get.return_value.json.return_value = fake_response

        # список валют для теста
        valutes = ['USD', 'EUR', 'XYZ']

        # Запускаем функцию
        result = get_now_ruble_curses(valutes)

        # Проверяем, что функция возвращает ожидаемый результат
        expected_result = {'USD': 70.5, 'EUR': 80.0}
        self.assertEqual(result, expected_result)

class TestGetNowRubleCurseFunction(unittest.TestCase):
    @patch('curs.requests.get')
    def test_get_now_ruble_curse(self, mock_requests_get):
        # Создаем фиктивный ответ от сервера
        fake_response = {
            'Valute': {
                'USD': {'Value': 70.5},
                'EUR': {'Value': 80.0},
                # Другие валюты
            }
        }
        
        # Настраиваем фиктивный объект запроса
        mock_requests_get.return_value.json.return_value = fake_response

        # Ваша валюта для теста
        valute = 'USD'

        # Запускаем функцию
        result = get_now_ruble_curse(valute)

        # Проверяем, что функция возвращает ожидаемый результат
        expected_result = 70.5
        self.assertEqual(result, expected_result)

class TestGetNowOtherCurseFunction(unittest.TestCase):
    @patch('curs.requests.get') 
    def test_get_now_other_curse(self, mock_requests_get):
        # Создаем фиктивный ответ от сервера
        fake_response = {
            'Valute': {
                'USD': {'Value': 70.5},
                'EUR': {'Value': 80.0},
                # Другие валюты
            }
        }
        
        # Настраиваем фиктивный объект запроса
        mock_requests_get.return_value.json.return_value = fake_response

        # Ваши валюты для теста
        valute1 = 'USD'
        valute2 = 'EUR'

        # Запускаем функцию
        result = get_now_other_curse(valute1, valute2)

        # Проверяем, что функция возвращает ожидаемый результат
        expected_result = 70.5 / 80.0  # Результат деления USD на EUR
        self.assertEqual(result, expected_result)

class TestIsValidNumberFunction(unittest.TestCase):
    def test_valid_number(self):
        # Проверяем валидные числа
        valid_numbers = ["3.14", "-42", "0.0", "12345"]
        for number in valid_numbers:
            result = is_valid_number(number)
            self.assertTrue(result, f"Ожидается, что {number} - это валидное число")

    def test_invalid_number(self):
        # Проверяем невалидные числа
        invalid_numbers = ["abc", "1,000", "3.14.15"]
        for number in invalid_numbers:
            result = is_valid_number(number)
            self.assertFalse(result, f"Ожидается, что {number} - это невалидное число")

class TestGetGrafFunction(unittest.TestCase):
    def test_get_graf(self):
        # Вызываем функцию и получаем результат
        valute = 'USD'
        period = 30  # Замените на желаемый период
        result = get_graf(valute, period)

        # Проверяем наличие результата
        self.assertIsNotNone(result, "Результат должен быть не None")

        # Проверяем тип результата (должен быть буфером)
        self.assertTrue(isinstance(result, io.BytesIO), "Результат должен быть объектом io.BytesIO")


if __name__ == '__main__':
    unittest.main()