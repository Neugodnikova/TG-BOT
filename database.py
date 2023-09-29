from peewee import Model, SqliteDatabase, CharField, AutoField

# Инициализируем базу данных SQLite
db = SqliteDatabase('./app_data/users.db')

# для переделки на PostgreSQL раскомментировать и удалить переменную db выше(закоментировать)
# from peewee import PostgresqlDatabase
# db = PostgresqlDatabase('your_database_name', user='your_database_user', password='your_database_password',
#                         host='your_database_host', port='your_database_port')

# Определяем модель данных для таблицы users
class User(Model):
    id = AutoField()
    user_id = CharField(unique=True)
    username = CharField(null=True)

    class Meta:
        database = db

# Создаем таблицу users, если она еще не существует
db.connect()
db.create_tables([User], safe=True)


# Проверка наличия пользователя по тг-id
def user_exists(user_id):
    try:
        User.get(User.user_id == user_id)
        return True
    except User.DoesNotExist:
        return False
    
# Добавление нового пользователя
def add_user(user_id, username=None):
    User.create(user_id=user_id, username=username)