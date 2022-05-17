import asyncio

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


import config
from api_jobitt_connect import get_skills_for_website
from models.db_api import data_api


def default_keyboard(user_id):
    default_keyboard_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    settings_button = KeyboardButton(text=config.buttons_names['settings_button_name'])
    stats_button = KeyboardButton(text=config.buttons_names['stats_button_name'])
    if user_id in config.admin_ids:
        default_keyboard_markup.add(stats_button)
    default_keyboard_markup.add(settings_button)
    return default_keyboard_markup


def settings_keyboard(message):
    settings_keyboard_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    user_settings = data_api.get_user_settings(message)

    skills_add = KeyboardButton(text=config.buttons_names['skills_add'])
    list_of_subscription = KeyboardButton(text=config.buttons_names['get_list_of_subscription'])
    settings_keyboard_markup.add(skills_add, list_of_subscription)

    if user_settings['messages_allowed']:
        receiving_text_messages = KeyboardButton(text=config.buttons_names['stop_receiving_text_messages'])
    else:
        receiving_text_messages = KeyboardButton(text=config.buttons_names['want_to_receive_text_messages'])
    if user_settings['other_alerts_allowed']:
        receiving_other_messages = KeyboardButton(text=config.buttons_names['stop_receiving_other_messages'])
    else:
        receiving_other_messages = KeyboardButton(text=config.buttons_names['want_to_receive_other_messages'])

    settings_keyboard_markup.add(receiving_text_messages, receiving_other_messages)
    go_back_button = KeyboardButton(text=config.buttons_names['go_back_button'])

    stats_button = KeyboardButton(text=config.buttons_names['stats_button_name'])
    if message.from_user.id in config.admin_ids:
        settings_keyboard_markup.add(go_back_button, stats_button)
    else:
        settings_keyboard_markup.add(go_back_button)

    # if user_settings['messages_allowed']:
    #     stop_receiving_text_messages = KeyboardButton(text=config.buttons_names['stop_receiving_text_messages'])
    #     settings_keyboard_markup.add(stop_receiving_text_messages)
    # else:
    #     want_to_receive_text_messages = KeyboardButton(text=config.buttons_names['want_to_receive_text_messages'])
    #     settings_keyboard_markup.add(want_to_receive_text_messages)
    # if user_settings['other_alerts_allowed']:
    #     stop_receiving_other_messages = KeyboardButton(text=config.buttons_names['stop_receiving_other_messages'])
    #     settings_keyboard_markup.add(stop_receiving_other_messages)
    # else:
    #     want_to_receive_other_messages = KeyboardButton(text=config.buttons_names['want_to_receive_other_messages'])
    #     settings_keyboard_markup.add(want_to_receive_other_messages)
    # go_back_button = KeyboardButton(text=config.buttons_names['go_back_button'])
    # settings_keyboard_markup.add(go_back_button)

    return settings_keyboard_markup


# клавиатура для ответа на входящее сообщение
def new_message_answer_keyboard(room):
    answer_button_reply_markup = InlineKeyboardMarkup()
    answer_button = InlineKeyboardButton(text='Ответить', callback_data=f"a~{room}")
    answer_button_reply_markup.add(answer_button)
    return answer_button_reply_markup


# клавиатура для отмены ввода
def cancel_keyboard():
    cancel_keyboard_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_button = KeyboardButton(text='❌ Отменить')
    cancel_keyboard_markup.add(cancel_button)
    return cancel_keyboard_markup


# # инлайн клавиатура для выбора и отправки скилов (Stan)
# async def skills_keyboard(message):
#     website_skills = await asyncio.create_task(get_skills_for_website())
#     user_skills_dict, user_list_skill_id = data_api.get_user_skills(message)
#     skills_keyboard_markup = InlineKeyboardMarkup(row_width=2)
#
#     for skill in website_skills:
#         if skill.get("id") in user_list_skill_id:
#             skills_keyboard_markup.insert(InlineKeyboardButton(text=f"❌ {skill['name']}",
#                                                                callback_data=f"s~{skill['id']}%%%{skill['name']}"))
#
#         else:
#             skills_keyboard_markup.insert(InlineKeyboardButton(text=f"✔ {skill['name']}",
#                                                                callback_data=f"s~{skill['id']}%%%{skill['name']}"))
#
#     choose_around = InlineKeyboardButton(text=config.buttons_names['mark_all_skills_button_name'],
#                                          callback_data='change_all_skills')
#     send_button = InlineKeyboardButton(text=config.buttons_names['send_skills_button_name'],
#                                        callback_data='send_skills')
#     skills_keyboard_markup.add(choose_around)
#     skills_keyboard_markup.add(send_button)
#     return skills_keyboard_markup

# add skills
async def skills_keyboard(message):
    website_skills = await asyncio.create_task(get_skills_for_website())
    user_skills_dict, user_list_skill_id = data_api.get_user_skills(message)
    skills_keyboard_markup = InlineKeyboardMarkup(row_width=2)

    for skill in website_skills:
        if skill.get("id") in user_list_skill_id:
            skills_keyboard_markup.insert(InlineKeyboardButton(text=f"❌ {skill['name']}",
                                                               callback_data=f"s~{skill['id']}%%%{skill['name']}"))

        else:
            skills_keyboard_markup.insert(InlineKeyboardButton(text=f"✔ {skill['name']}",
                                                               callback_data=f"s~{skill['id']}%%%{skill['name']}"))

    # choose_around = InlineKeyboardButton(text=config.buttons_names['mark_all_skills_button_name'],
    #                                      callback_data='change_all_skills')
    # skills_keyboard_markup.add(choose_around)
    send_button = InlineKeyboardButton(text=config.buttons_names['send_skills_button_name'],
                                       callback_data='send_skills')

    skills_keyboard_markup.add(send_button)
    return skills_keyboard_markup


def new_candidate_keyboard(candidate_id):
    new_candidate_keyboard_markup = InlineKeyboardMarkup()
    send_message_to_candidate = InlineKeyboardButton(text=config.buttons_names['new_candidate_message_button_name'],
                                                     callback_data=f"c~{candidate_id}")
    new_candidate_keyboard_markup.add(send_message_to_candidate)
    return new_candidate_keyboard_markup


def new_vacancy_keyboard(company_id, vacancy_id, url):
    new_vacancy_keyboard_markup = InlineKeyboardMarkup(row_width=2)
    send_message_button = InlineKeyboardButton(text=config.buttons_names['send_message_to_vacancy_button_name'],
                                               callback_data=f"av~{vacancy_id}")


    open_contacts_button_button = InlineKeyboardButton(
        text=config.buttons_names['open_contacts_to_vacancy_button_name'],
        callback_data=f"o~{company_id}")

    new_vacancy_keyboard_markup.add(send_message_button)
    new_vacancy_keyboard_markup.insert(open_contacts_button_button)
    # link_button = InlineKeyboardButton(text="🌐 Перейти на сайт", url=url)
    # new_vacancy_keyboard_markup.add(link_button)
    return new_vacancy_keyboard_markup


# def get_subscription(data):
#     inline_kb_full = InlineKeyboardMarkup(row_width=2)
#     for dict_ in data:
#         specializations = [item.get("name") for item in dict_.get("specializations")]
#         text = f'Скилы {specializations}'
#         inline_kb_full.add(InlineKeyboardButton(text, callback_data=f"remove_sub{dict_.get('id')}"),
#                            InlineKeyboardButton('Удалить', callback_data=f"remove_sub{dict_.get('id')}"))
#     # inline_kb_full.add(InlineKeyboardButton("❌Отмена", callback_data="currencydone"))
#     return inline_kb_full

def get_subscription(subscription, message_id):
    inline_kb_full = InlineKeyboardMarkup(row_width=1)

    inline_kb_full.add(InlineKeyboardButton('❌ Удалить', callback_data=f"remove_sub{subscription.get('id')}%%%{message_id}"))
    return inline_kb_full
