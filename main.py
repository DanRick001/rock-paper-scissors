# - *- coding: utf- 8 - *-
import asyncio
import requests
import DBcontrol
import random

from SimpleQIWI import *

from pyqiwip2p import QiwiP2P
from pyqiwip2p.p2p_types import QiwiCustomer, QiwiDatetime

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, ContentType

from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.callback_data import CallbackData

TOKEN = '5510764755:AAEgrVbJG3PTB6qkhUd7Bdq_xlOiMblWRkw'
OWNER_ID = ["1194880448", "1285111166"]

#token_QIWI = 'd46b523a448ab2a646f182ddefd6f775'
token_QIWI = '98c478d0d4601f5ab7b8abfdda46b1ab'
authKey_QIWI = 'eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6InNpdjFvai0wMCIsInVzZXJfaWQiOiI3OTE5MTQyMDk2MyIsInNlY3JldCI6ImVjY2E5MDUxNWUxZjUyYzY4MGEzNGMyZDQwZWNiZmVjOWVmY2EzODVhYjUyMmQ0NjdiNDAzZDM0YzU2MTgwMzgifX0='
my_phone = '+79191420963'
p2p = QiwiP2P(auth_key=authKey_QIWI) #Сессия QIWI

qiwi_api = QApi(token=token_QIWI, phone=my_phone)
#print(qiwi_api.balance)

for chat_id in OWNER_ID:
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text=In developing") #Online message

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
global amount
#так называемые "обработчики состояния"
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
vote_cb = CallbackData('vote', "action", "user_id", "chat_id")

###############################################################################################################################################################################
rooms = {}

inline_btn_1 = InlineKeyboardButton('Первая кнопка!', callback_data='button1')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)
###############################################################################################################################################################################

#создаём состояния
class States(Helper):
    mode = HelperMode.snake_case

    AMOUNT_TOP_DOWN_3 = ListItem()
    ANSWER_ON_MESSAGE_1 = ListItem()
    AMOUNT_TOP_UP_2 = ListItem()

print(States.all())

async def pay_check(new_bill, username, amount, chat_id):
    while True:
        await asyncio.sleep(0.0001)
        print(username, p2p.check(bill_id=new_bill.bill_id).status)
        if p2p.check(bill_id=new_bill.bill_id).status == 'PAID':
            p2p.reject(bill_id=new_bill.bill_id)
            await asyncio.ensure_future(DBcontrol.top_up(username, amount))
            await bot.send_message(chat_id, "Спасибо за оплату!💜")
            return
            break
        if p2p.check(bill_id=new_bill.bill_id).status == 'REJECTED':
            await bot.send_message(chat_id, "Успешно!😃 Ваш счёт был закрыт.")
            return

async def check_data(username, ref_check=None):
    data = await asyncio.ensure_future(DBcontrol.get_data(username))
    if data == False:
        reg_data = await asyncio.ensure_future(DBcontrol.reg(username, ref_check))
        if reg_data == True:
            data = await asyncio.ensure_future(DBcontrol.get_data(username))
            return data
    else:
        return data

@dp.message_handler(state=States.ANSWER_ON_MESSAGE_1)
async def referal_state(message: types.Message):
    referal_username = message.text.split(' ')[0]
    message_username = message.from_user.username
    state = dp.current_state(user=message.from_user.id)
    if '@' in referal_username:
        referal_username = referal_username.replace('@', '')

    if message_username != referal_username:
        if await asyncio.ensure_future(DBcontrol.reg(referal_username, True, message_username)) == 1:
            await message.reply('Вас пригласил: ' + referal_username, reply=False)
            await state.reset_state()
            await asyncio.ensure_future(profile(message))
        elif message.text == '-':
            await state.reset_state()
            await asyncio.ensure_future(profile(message))

        else:
            await message.reply('Такого пользователя нет. Проверьте правильность написания никнейма!', reply=False)
    else:
        await message.reply('Вы не можете использовать свой юзернейм!', reply=False)

@dp.message_handler(state='*', commands=['start'], commands_prefix='/')
async def start(message: types.Message):
    username = message.from_user.username
    data = await asyncio.ensure_future(DBcontrol.get_data(username))
    if data == False:
        data = await asyncio.ensure_future(check_data(username))
        await message.answer('Введите юзернейм пригласившего(если его нет, то напишите \"-\"): ')
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(States.all()[2]) #создаём стейт

    else:
        await message.answer('Вы уже зарегистрированы!')

@dp.message_handler(commands=['profile'], commands_prefix='/') #обработчик комманды /profile
async def profile(message: types.Message):
    username = message.from_user.username
    data = await asyncio.ensure_future(check_data(username))
    if data != False:
        topUP_button = KeyboardButton('Пополнить баланс')
        withdraw_button = KeyboardButton('Вывести деньги')
        info_button = KeyboardButton('Информация')
        #markup3 = ReplyKeyboardMarkup().add(button1).add(button2).add(button3)
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True) #инициализируем клавиатуру клавиатуру с параметром маленького размера кнопок
        keyboard.add(topUP_button, withdraw_button) #добавляем кнопки и изменяем размер кнопки
        keyboard.row(info_button) #кнопка на новой строчке

        await message.reply(f'👤Имя: {username}\n🤑Баланс: {data[0]}\n✏️История: {data[1]}\n🤖Кол-во рефералов: {data[2]}\n📣Вас прегласил: {data[3]}', reply_markup=keyboard)

###############################################################################################################################################################################
@dp.message_handler(commands=['create_room'], commands_prefix='/') #обработчик комманды /create_room
async def create_new_room(message: types.Message):
    try:
        username = message.from_user.username
        data = await asyncio.ensure_future(check_data(username))
        #rooms[username] = random.randint(96, 100)
        rooms[username] = int(message.text[13:])
        await message.answer(f"Ставка на {rooms[username]} руб. успешно создана!")
        print(rooms)
    except:
        await message.answer("Что-то пошло не так")

@dp.message_handler(commands=['find_room'], commands_prefix='/') #обработчик комманды /find_room
async def find_room(message: types.Message):
    username = message.from_user.username
    data = await asyncio.ensure_future(check_data(username))
    try:
        amount = int(message.text[11:])
    #await message.answer(amount)
        people=[]
        for i in rooms.items():
            for j in range(-10, 10):
                if i[1] == j + amount :#and username != i[0]
                    people.append(i)
        room_creator_id = str(people[random.randint(0, len(people)-1)][0])
        amount = int(people[random.randint(0, len(people)-1)][1])
        await message.answer(f'Вы играете с {room_creator_id}. Ставка: {amount} руб.')
        #print(people[random.randint(0, len(people)-1)])

    except:
        await message.answer("Что-то пошло не так")

###############################################################################################################################################################################

@dp.message_handler(state=States.AMOUNT_TOP_UP_2)
async def amount_topUP(message: types.Message):
    username = message.from_user.username
    chat_id = message.chat.id
    amount = int(message.text)
    state = dp.current_state(user=message.from_user.id)
    new_bill = p2p.bill(bill_id=random.randint(111111111,999999999), amount=amount, lifetime=15)

    keyboard = InlineKeyboardMarkup(row_with=2)
    keyboard.add(InlineKeyboardButton('✅Оплатить', url=new_bill.pay_url))
    await message.reply('Выберите способ оплаты: ', reply_markup=keyboard)
    asyncio.ensure_future(pay_check(new_bill, username, amount, chat_id))
    await state.reset_state()

@dp.message_handler(state=States.AMOUNT_TOP_DOWN_3)
async def amount_topDOWN(message: types.Message):
    try:
        data = await asyncio.ensure_future(check_data(username))
        username = message.from_user.username
        text = message.text.split(' ')
        phone_number = text[0]
        amount = int(text[1])
        if data[0] >= amount:
            state = dp.current_state(user=message.from_user.id)
            qiwi_api.pay(account=phone_number, amount=amount, comment='RPS_stavka')
            await message.answer('Вывод средств произошёл успешно!')
        else:
            await message.answer('У вас недостаточно средств.')
    except:
        await message.answer('Произошла неизвестная ошибка. Попробуйте ещё раз!')

    await state.reset_state()

@dp.callback_query_handler(vote_cb.filter(action='qiwi_up'))
async def qiwi_up_callback(query: types.CallbackQuery, callback_data: dict):
    user_id = callback_data['user_id']
    chat_id = callback_data['chat_id']
    await bot.send_message(chat_id, 'Введите сумму пополнения(без зяпятых и точек)')
    state = dp.current_state(user=user_id)
    await state.set_state(States.all()[1]) #создаём стейт

@dp.callback_query_handler(vote_cb.filter(action='qiwi_down'))
async def qiwi_down_callback_amount(query: types.CallbackQuery, callback_data: dict):
    user_id = callback_data['user_id']
    chat_id = callback_data['chat_id']
    await bot.send_message(chat_id, 'Введите команду следущего вида(без скобок): НОМЕР_ТЕЛЕФОНА(в виде +79000000000) СУММА_ВЫВОДА\nЕсли данные будут введены неверно, то мы не несём ответственность за ваши деньги!')
    state = dp.current_state(user=user_id)
    await state.set_state(States.all()[0]) #создаём стейт

@dp.message_handler(state='*') #Обработчик всех сообщений, который не прошли проверку от обработчиков выше
async def keyboard_commands(message: types.Message):
    text = message.text.lower()
    username = message.from_user.username
    if text == 'информация':
        await message.answer('some information')

    elif text == 'пополнить баланс':
        keyboard = InlineKeyboardMarkup(row_with=2)
        qiwi_button = InlineKeyboardButton('QIWI🥝', callback_data=vote_cb.new(action='qiwi_up', user_id=message.from_user.id, chat_id=message.chat.id))
        keyboard.add(qiwi_button)
        await message.reply('Выберите способ оплаты: ', reply_markup=keyboard)

    elif text == 'вывести деньги':
        keyboard = InlineKeyboardMarkup(row_with=2)
        qiwi_button = InlineKeyboardButton('QIWI🥝', callback_data=vote_cb.new(action='qiwi_down', user_id=message.from_user.id, chat_id=message.chat.id))
        keyboard.add(qiwi_button)
        await message.reply('Выберите метод вывода денег: ', reply_markup=keyboard)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True) #Стартуем бота.