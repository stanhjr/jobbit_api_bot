import asyncio

import aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ChatType
from aiogram.utils import executor

import api_jobitt_connect
from config import ADMIN_IDS
import config
from models.db_api import data_api
import keyboards
from deploy.deploy_config import TOKEN

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class MessageAnswerFrom(StatesGroup):
    room_id = State()
    new_message = State()


class NewCandidateMessageForm(StatesGroup):
    candidate_id = State()
    new_message = State()


class NewVacancyMessageForm(StatesGroup):
    vacancy_id = State()
    new_message = State()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='❌ Отменить', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await bot.send_message(chat_id=message.from_user.id,
                           text='Операция отменена успешно',
                           reply_markup=keyboards.default_keyboard(message.from_user.id))
    await state.finish()


@dp.message_handler(aiogram.filters.ChatTypeFilter(chat_type=ChatType.PRIVATE), commands=['start'])
async def process_start_command(message: types.Message):
    try:
        print(message)
        if not data_api.get_user(message):
            data = await asyncio.create_task(
                api_jobitt_connect.get_user_account_details(token=message.text.split(' ')[1]))
            if data:

                data_api.create_user(message=message, data=data)
                await bot.send_message(chat_id=message.from_user.id,
                                       text=f"{str(data['data']['name'])} {config.bot_messages['start_message_text']}",
                                       reply_markup=keyboards.default_keyboard(message.from_user.id))
            else:
                await bot.send_message(chat_id=message.from_user.id,
                                       text=config.bot_messages['token_expired_error'])
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                   text=config.bot_messages['you_are_already_logged_in'],
                                   reply_markup=keyboards.default_keyboard(message.from_user.id))

    except IndexError:
        if message.from_user.id in ADMIN_IDS:
            await bot.send_message(chat_id=message.from_user.id,
                                   text=config.bot_messages['start_admin_message_text'],
                                   reply_markup=keyboards.admin_keyboard())
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                   text=config.bot_messages['no_code_error'])


@dp.message_handler(aiogram.filters.ChatTypeFilter(chat_type=ChatType.PRIVATE), commands=['clear'])
async def clear_command(message: types.Message):
    data_api.delete_user(message)
    await bot.send_message(chat_id=message.from_user.id,
                           text="Аккаунт успешно отвязан",
                           reply_markup=keyboards.default_keyboard(message.from_user.id))


# callback of a reply to a message
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('a~'))
async def answer_process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['room_id'] = callback_query.data.split('~')[1]
    await MessageAnswerFrom.new_message.set()
    await bot.send_message(chat_id=callback_query.from_user.id, text=config.bot_messages['ask_to_send_text_message'],
                           reply_markup=keyboards.cancel_keyboard())


# get text a message for request
@dp.message_handler(state=MessageAnswerFrom.new_message)
async def new_message_for_answer_getter(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['new_message'] = message.text
        room_id = data['room_id']
    website_id = data_api.get_user_website_id(message)
    data = await asyncio.create_task(api_jobitt_connect.send_message(room_id=room_id,
                                                                     message_text=data['new_message'],
                                                                     sender_id=website_id))
    await bot.send_message(chat_id=message.from_user.id, text=f"{data}",
                           reply_markup=keyboards.default_keyboard(message.from_user.id))
    await state.finish()


# processing the start of writing a message to a new candidate
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('c~'))
async def answer_to_new_candidate_callback(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['candidate_id'] = callback_query.data.split('~')[1]
    await NewCandidateMessageForm.new_message.set()
    await bot.send_message(chat_id=callback_query.from_user.id, text=config.bot_messages['ask_to_send_text_message'],
                           reply_markup=keyboards.cancel_keyboard())


# write a message to a new candidate and send it
@dp.message_handler(state=NewCandidateMessageForm.new_message)
async def new_message_for_answer_getter(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['new_message'] = message.text
        candidate_id = data['candidate_id']
    website_id = data_api.get_user_website_id(message)
    await state.finish()
    data = await asyncio.create_task(api_jobitt_connect.send_new_message_to_candidate(candidate=candidate_id,
                                                                                      from_user=website_id,
                                                                                      message=data['new_message']))
    await bot.send_message(chat_id=message.from_user.id,
                           text=f"{data}",
                           reply_markup=keyboards.default_keyboard(message.from_user.id))


# call back response to messages about a new vacancy
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('av~'))
async def answer_process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['vacancy_id'] = callback_query.data.split('~')[1]
    await NewVacancyMessageForm.new_message.set()
    await bot.send_message(chat_id=callback_query.from_user.id, text=config.bot_messages['ask_to_send_text_message'],
                           reply_markup=keyboards.cancel_keyboard())


# get the text of the message to reply to a message about a new vacancy
@dp.message_handler(state=NewVacancyMessageForm.new_message)
async def new_message_for_answer_getter(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['new_message'] = message.text
        vacancy_id = data['vacancy_id']
    website_id = data_api.get_user_website_id(message)
    data = await asyncio.create_task(api_jobitt_connect.vacancy_response(vacancy=vacancy_id,
                                                                         from_user=website_id,
                                                                         message=data['new_message']))
    await bot.send_message(chat_id=message.from_user.id, text=f"{data}",
                           reply_markup=keyboards.default_keyboard(message.from_user.id))
    await state.finish()


# open contacts
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('o~'))
async def open_contacts_to_vacancy_callback(callback_query: types.CallbackQuery):
    company_id = callback_query.data.split('~')[1]
    website_id = data_api.get_user_website_id(callback_query)
    data = await asyncio.create_task(api_jobitt_connect.open_contacts_to_company(company=company_id,
                                                                                 website_id=website_id))
    await bot.send_message(chat_id=callback_query.from_user.id, text=f"{data}",
                           reply_markup=keyboards.default_keyboard(callback_query.from_user.id))


# push settings button
@dp.message_handler(aiogram.filters.ChatTypeFilter(chat_type=ChatType.PRIVATE),
                    aiogram.dispatcher.filters.Text(startswith=config.buttons_names['settings_button_name']))
async def setting_button_callback(message: types.Message):
    try:
        await bot.send_message(chat_id=message.from_user.id,
                               text=config.bot_messages['settings_message_text'],
                               reply_markup=keyboards.settings_keyboard(message))
    except TypeError:
        await bot.send_message(chat_id=message.from_user.id,
                               text=config.bot_messages['not access'])


# enable receiving messages button
@dp.message_handler(aiogram.filters.ChatTypeFilter(chat_type=ChatType.PRIVATE),
                    aiogram.dispatcher.filters.Text(startswith=config.buttons_names['want_to_receive_text_messages']))
async def want_to_receive_text_messages_callback(message: types.Message):
    data_api.enable_message_allowed(message)
    await bot.send_message(chat_id=message.from_user.id,
                           text=config.bot_messages['settings_changed'],
                           reply_markup=keyboards.settings_keyboard(message))


# disable receiving messages button
@dp.message_handler(aiogram.filters.ChatTypeFilter(chat_type=ChatType.PRIVATE),
                    aiogram.dispatcher.filters.Text(startswith=config.buttons_names['stop_receiving_text_messages']))
async def stop_receiving_text_messages_callback(message: types.Message):
    data_api.disable_message_allowed(message)
    await bot.send_message(chat_id=message.from_user.id,
                           text=config.bot_messages['settings_changed'],
                           reply_markup=keyboards.settings_keyboard(message))


# enable receiving alerts
@dp.message_handler(aiogram.filters.ChatTypeFilter(chat_type=ChatType.PRIVATE),
                    aiogram.dispatcher.filters.Text(startswith=config.buttons_names['want_to_receive_other_messages']))
async def want_to_receive_other_messages_callback(message: types.Message):
    data_api.enable_other_alerts_allowed(message)
    await bot.send_message(chat_id=message.from_user.id,
                           text=config.bot_messages['settings_changed'],
                           reply_markup=keyboards.settings_keyboard(message))


# disable receiving alerts
@dp.message_handler(aiogram.filters.ChatTypeFilter(chat_type=ChatType.PRIVATE),
                    aiogram.dispatcher.filters.Text(startswith=config.buttons_names['stop_receiving_other_messages']))
async def stop_receiving_other_messages_callback(message: types.Message):
    data_api.disable_other_alerts_allowed(message)
    await bot.send_message(chat_id=message.from_user.id,
                           text=config.bot_messages['settings_changed'],
                           reply_markup=keyboards.settings_keyboard(message))


# go home
@dp.message_handler(aiogram.filters.ChatTypeFilter(chat_type=ChatType.PRIVATE),
                    aiogram.dispatcher.filters.Text(startswith=config.buttons_names['go_back_button']))
async def go_back_button_callback(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=config.bot_messages['go_to_main_page_text'],
                           reply_markup=keyboards.default_keyboard(message))


#
@dp.message_handler(aiogram.filters.ChatTypeFilter(chat_type=ChatType.PRIVATE),
                    aiogram.dispatcher.filters.Text(startswith=config.buttons_names['skills_update']))
async def skills_update_callback(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text=config.bot_messages['skills_update_menu_text'],
                           reply_markup=await keyboards.skills_keyboard(message))


# get list of subscriptions
@dp.message_handler(aiogram.filters.ChatTypeFilter(chat_type=ChatType.PRIVATE),
                    aiogram.dispatcher.filters.Text(startswith=config.buttons_names['get_list_of_subscription']))
async def get_list_of_subscription(message: types.Message):
    website_user_id = data_api.get_user_website_id(message)
    data = await asyncio.create_task(api_jobitt_connect.get_skills_for_user_in_website(website_user_id))
    if not data:
        await bot.send_message(chat_id=message.from_user.id,
                               text=' Активных подписок пока нет',
                               reply_markup=keyboards.settings_keyboard(message))
    for subscription in data:
        specializations = [f'#{vacancy.get("name")}' for vacancy in subscription.get("specializations")]
        specializations_text = ' '.join(specializations)
        english = subscription.get("english")
        salary_to = subscription.get("salary_to")
        salary_from = subscription.get("salary_from")

        text = f'<b>Skills:</b> {specializations_text}\n<b>English:</b> {english}\n<b>Salary_from:</b>{salary_from}\n<b>Salary_to:</b>{salary_to}'
        msg = await bot.send_message(chat_id=message.from_user.id,
                                     text=text,
                                     reply_markup=keyboards.get_subscription(subscription, message.message_id),
                                     parse_mode='HTML')

        await bot.edit_message_text(message_id=msg.message_id,
                                    chat_id=message.from_user.id,
                                    reply_markup=keyboards.get_subscription(subscription, msg.message_id),
                                    text=text,
                                    parse_mode='HTML')


# removing a subscription
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('remove_sub'))
async def skills_process_callback(callback_query: types.CallbackQuery):
    callback_data = callback_query.data[10:].split('%%%')
    subscription_id = callback_data[0]
    message_id = callback_data[1]
    website_user_id = data_api.get_user_website_id(callback_query)
    result = await asyncio.create_task(
        api_jobitt_connect.delete_subscription_for_user_in_website(website_user_id=website_user_id,
                                                                   sub_id=subscription_id))

    if result:
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=message_id)


# skills_add
@dp.message_handler(aiogram.filters.ChatTypeFilter(chat_type=ChatType.PRIVATE),
                    aiogram.dispatcher.filters.Text(startswith=config.buttons_names['skills_add']))
async def skills_update_callback(message: types.Message):
    data_api.delete_all_skill_for_user(message)
    msg = await bot.send_message(chat_id=message.from_user.id,
                                 text=config.bot_messages['skills_update_menu_text'],
                                 reply_markup=await keyboards.skills_keyboard(message, msg_id=message.message_id))
    await bot.edit_message_text(message_id=msg.message_id,
                                chat_id=message.from_user.id,
                                text=config.bot_messages['skills_update_menu_text'],
                                reply_markup=await keyboards.skills_keyboard(message, msg_id=msg.message_id))


# pagination
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('i'))
async def skills_update_callback_pagination(callback_query: types.CallbackQuery):
    callback_data = callback_query.data.split('=')
    type_id = int(callback_data[1])
    msg_id = int(callback_data[2])
    markup = await keyboards.skills_keyboard_pagination(callback_query, type_id=type_id, msg_id=msg_id)
    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                text=config.bot_messages['skills_update_menu_text'],
                                message_id=msg_id,
                                reply_markup=markup)


# skill_update
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('s~'))
async def skills_process_callback(callback_query: types.CallbackQuery):
    callback_data = callback_query.data[2:].split('%')
    skill_id = callback_data[0]
    skill_name = callback_data[1]
    msg_id = int(callback_data[2])
    type_id = int(callback_data[3])
    if data_api.check_skill_for_user(message=callback_query, skill_id=skill_id):
        data_api.delete_skill_for_user(message=callback_query, skill_id=skill_id)
    else:
        data_api.add_skill_for_user(message=callback_query, skill_id=skill_id, skill_name=skill_name)

    keyboards_new = await keyboards.skills_keyboard_pagination(callback_query=callback_query, msg_id=msg_id, type_id=type_id)
    await bot.edit_message_reply_markup(chat_id=callback_query.from_user.id,
                                        message_id=msg_id,
                                        reply_markup=keyboards_new)


# call back for sending subscriptions
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('send_skills'))
async def answer_process_callback(callback_query: types.CallbackQuery):
    user_skills_list, my_side, website_user_id = data_api.get_user_list_skill_id(callback_query)
    msg_id = int(callback_query.data.split('%')[1])

    if user_skills_list:

        data = await asyncio.create_task(api_jobitt_connect.skills_subscription(website_user_id=website_user_id,
                                                                                account_type=my_side,
                                                                                skills_list=user_skills_list))
        if not data:
            await bot.edit_message_text(message_id=msg_id, chat_id=callback_query.from_user.id,
                                        text=config.bot_messages['skills_update_success'])
        if data.get('status'):
            await bot.edit_message_text(message_id=msg_id, chat_id=callback_query.from_user.id,
                                        text=config.bot_messages['skills_update_success'])

        elif data.get("response_code") == 400:
            await bot.edit_message_text(message_id=msg_id, chat_id=callback_query.from_user.id,
                                        text=config.bot_messages['skills_update_fail_count_sub'])

        elif data.get("response_code") == 422:
            await bot.edit_message_text(message_id=msg_id, chat_id=callback_query.from_user.id,
                                        text=config.bot_messages['skills_update_fail_count'])

        else:
            await bot.edit_message_text(message_id=msg_id, chat_id=callback_query.from_user.id,
                                        text=config.bot_messages['skills_update_fail'])

        data_api.delete_all_skill_for_user(message=callback_query)


# get stats for admin
@dp.message_handler(aiogram.filters.ChatTypeFilter(chat_type=ChatType.PRIVATE),
                    aiogram.dispatcher.filters.Text(startswith=config.buttons_names['stats_button_name']))
async def stats_button_name_callback(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        final_text = f"<b>Всего пользователей:</b> {data_api.get_count_of_active_user()}\n\n" \
                     f"<b>Всего уведомлений отправлено:</b> {data_api.get_sum_notifications()}\n"
        await bot.send_message(chat_id=message.from_user.id, text=final_text, parse_mode='HTML')


if __name__ == '__main__':
    executor.start_polling(dp)
