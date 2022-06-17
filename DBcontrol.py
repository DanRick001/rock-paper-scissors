import sqlite3
import os
import asyncio

db = sqlite3.connect("mainBase.db")
cursor = db.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS data(
        login TEXT,
        balance INTEGER,
        history TEXT,
        count_ref INTEGER
    )""")

db.commit()

async def get_data(username): #функция получения всех данных пользователя
    for data_info in cursor.execute('SELECT login, balance, history, count_ref FROM data'):
        if data_info[0] == username:
            cursor.execute(f'SELECT login FROM data WHERE login = "{username}"')
            balance = data_info[1] #баланс
            history = data_info[2] #история игр
            count_ref = data_info[3] #кол-во приведённых рефералов
            return balance, history, count_ref
            break

    return False

async def reg(username, ref_check): #функция стартовой регистрации пользователя
    cursor.execute(f"SELECT login FROM data WHERE login = '{username}'") #выбрать ячейку с именем пользователя
    fetchone = cursor.fetchone() # я хз зачем это нужно в переменную, но без неё не работает(
    if fetchone is None and ref_check != True: 
        cursor.execute(f"INSERT INTO data VALUES (?, ?, ?, ?)", (username, 0, 'Нету', 0)) #внести данные в эту ячейку
        db.commit() #сохранить изменения
        print('Новый пользователь: ' + username)
        return True

    elif fetchone is not None and ref_check == True:
        data = await asyncio.ensure_future(get_data(username))
        count_ref = data[2]
        cursor.execute(f"UPDATE data SET count_ref = {count_ref + 1} WHERE login = '{username}'")
        db.commit()
        return 1