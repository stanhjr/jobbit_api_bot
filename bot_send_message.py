from aiogram.utils.exceptions import ChatNotFound, BotBlocked

import keyboards
from jobbit_bot import bot


async def send_message_new_vacancy(chat_id, company_id, vacancy_id, name, url):
    try:
        text = f"🔥 <b>Новая вакансия!</b>\n\n<b>Название:</b> {name}\n\n<b>Ссылка:</b> {url}"

        await bot.send_message(chat_id=chat_id, text=text,
                               parse_mode='HTML',
                               reply_markup=keyboards.new_vacancy_keyboard(
                                   company_id=company_id,
                                   vacancy_id=vacancy_id,
                                   url=url))
    except (ChatNotFound, BotBlocked):
        pass


async def send_message_new_candidate(chat_id, candidate_id, name, url):
    try:
        text = f"🔥 <b>Новый работник!</b>\n\n<b>Должность:</b> {name}\n\n<b>Ссылка:</b> {url}"

        await bot.send_message(chat_id=chat_id, text=text,
                               reply_markup=keyboards.new_candidate_keyboard(candidate_id=candidate_id),
                               parse_mode='HTML')
    except (ChatNotFound, BotBlocked):
        pass


async def send_message_for_user(chat_id, room_id, sender_name, text):
    try:
        text = f"📩 <b>Сообщение от {sender_name}!</b>\n\n{text}"
        await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML',
                               reply_markup=keyboards.new_message_answer_keyboard(room=room_id))

    except (ChatNotFound, BotBlocked):
        pass
