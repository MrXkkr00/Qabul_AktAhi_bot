import logging

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor


logging.basicConfig(level=logging.INFO)

API_TOKEN = '5910799250:AAFafcorKqOzEQ11Cy1n3xydTmpFmbpvZOA'

bot = Bot(token=API_TOKEN)

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States
class Form(StatesGroup):
    name = State()  # Will be represented in storage as 'Form:name'
    gender = State()  # Will be represented in storage as 'Form:gender'
    oqishjoyi = State()
    muassasa = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """
    # Set state
    await Form.name.set()

    await message.answer(
        "Assalomu Alekum Bu AKT va AXI tomonidan \n\nQabul haqida malumot bot\n\n Familya Ism Sharifizni kiriting")


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.answer('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process user name
    """
    async with state.proxy() as data:
        data['name'] = message.text

    await Form.next()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Andijon", "Buxoro", "Farg'ona", "Jizzax", "Xorazm", "Namangan", "Toshkent", "Navoiy", "Qashqadaryo",
               "Qoraqolpog'iston Respublikasi", "Samarqand", "Sirdaryo", "Surxandaryo")

    await message.answer("qaysi viloyatda o'iysiz?", reply_markup=markup)


@dp.message_handler(
    lambda message: message.text not in ["Andijon", "Buxoro", "Farg'ona", "Jizzax", "Xorazm", "Namangan", "Toshkent",
                                         "Navoiy", "Qashqadaryo", "Qoraqolpog'iston Respublikasi", "Samarqand",
                                         "Sirdaryo", "Surxandaryo"], state=Form.gender)
async def process_gender_invalid(message: types.Message):
    """
    In this example gender has to be one of: Male, Female, Other.
    """
    return await message.reply("Siz notog'ri kiritdingiz iltimos to'g'ri bo'limni tanlang")


@dp.message_handler(state=Form.oqishjoyi)
async def process_oqishjoyi(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['oqishjoyi'] = message.text
    await Form.next()
    await message.answer("Hozirda o'qiyotgan Oliy talim muassasangizni kiriting", )


@dp.message_handler(state=Form.gender)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gender'] = message.text
    await Form.next()
    # Remove keyboard

    # And send message

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, )
    markup.add("Online ", "Vayanqamat orqali", "2 lasidan ham")

    await message.answer("siz qanday ro'yxatdan o'tgansiz", reply_markup=markup)

@dp.message_handler(state=Form.muassasa)
async def process_muassasa(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, )
    markup.add("start")
    async with state.proxy() as data:
        data['muassasa'] = message.text
        f = open("users_online.txt", "a")
        f.write(
            f"{data['name']}\n   id:{message.chat.id}\n   tn:{data['gender']}\n   {data['oqishjoyi']}\n   {data['muassasa']}\n\n")
        f.close()

        await bot.send_message(

            984568970,
            md.text(
                
                md.text('F I SH:                          ', md.bold(data['name'])),
                md.text('Viloyat:                        ', md.code(data['gender'])),
                md.text('Oqish joyi:                  ', md.code(data['oqishjoyi'])),
                md.text('Muassasa nomi:       ', md.code(data['muassasa'])),
                sep='\n',
            ),
            parse_mode=ParseMode.MARKDOWN,
        )
        markup = types.ReplyKeyboardRemove()

        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('F I SH:                          ', md.bold(data['name'])),

                md.text('Viloyat:                        ', md.code(data['gender'])),
                md.text('Oqish joyi:                  ', md.code(data['oqishjoyi'])),
                md.text('Muassasa nomi:       ', md.code(data['muassasa'])),
                sep='\n',
            ),

            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )

    # Finish conversation

    await message.answer("Agar malumotlarni o'zgartirishni hohlasangiz  /start ni yuboring", reply_markup=markup)
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
