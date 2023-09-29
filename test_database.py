import unittest
from peewee import SqliteDatabase, Model, CharField, AutoField
from database import user_exists, add_user

# Определяем временную базу данных SQLite для тестов
test_db = SqliteDatabase(':memory:')

# Определяем модель данных для таблицы users
class User(Model):
    id = AutoField()
    user_id = CharField(unique=True)
    username = CharField(null=True)

    class Meta:
        database = test_db

# Создаем таблицу users во временной базе данных
test_db.connect()
test_db.create_tables([User], safe=True)

def user_exists(user_id):
    try:
        User.get(User.user_id == user_id)
        return True
    except User.DoesNotExist:
        return False

def add_user(user_id, username=None):
    User.create(user_id=user_id, username=username)

class TestUserFunctions(unittest.TestCase):
    def setUp(self):
        # Удаление всех записей из временной базы данных перед каждым тестом
        User.delete().execute()
        self.user_id = "12345"
        self.username = "testuser"

    def test_user_exists_existing_user(self):
        add_user(self.user_id, self.username)
        self.assertTrue(user_exists(self.user_id))

    def test_user_exists_non_existing_user(self):
        self.assertFalse(user_exists(self.user_id))

    def test_add_user(self):
        add_user(self.user_id, self.username)
        user = User.get(User.user_id == self.user_id)
        self.assertEqual(user.username, self.username)

if __name__ == '__main__':
    unittest.main()
