# - *- coding: utf- 8 - *-
import asyncio
import requests
import DBcontrol

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, ContentType

from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

TOKEN = '5510764755:AAEgrVbJG3PTB6qkhUd7Bdq_xlOiMblWRkw'
OWNER_ID = ["1194880448", "1285111166"]

for chat_id in OWNER_ID:
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text=In developing") #Online message

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

#так называемые "обработчики состояния"
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

#создаём состояния
class States(Helper):
    mode = HelperMode.snake_case
    ANSWER_ON_MESSAGE_1 = ListItem()

#print(States.all())

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
            await message.reply('Вас прегласил: ' + referal_username, reply=False)
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
        await state.set_state(States.all()[0]) #создаём стейт

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

@dp.message_handler() #Обработчик всех сообщений, который не прошли проверку от обработчиков выше
async def commands(message: types.Message):
    text = message.text.lower()
    username = message.from_user.username
    if text == 'информация':
        await message.answer('some information')

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True) #Стартуем бота.