import json

import aiohttp

import config


# получаем даннные человека с сайта
async def get_user_account_details(token):
    async with aiohttp.ClientSession() as session:
        headers = {
            'telegram-bot-token': config.output_api_settings['telegram_bot_token_for_req'],
            'accept-language': 'ru',
        }
        params = (
            ('code', token),
        )
        url = f"{config.output_api_settings['api_hostname']}/api/telegram-bot/user"
        async with session.get(url=url, params=params, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                return None


# отвечаем сообщением на новую вакансию
async def vacancy_response(vacancy, from_user, message):
    async with aiohttp.ClientSession() as session:
        headers = {
            'telegram-bot-token': config.output_api_settings['telegram_bot_token_for_req'],
            'accept-language': 'ru',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        url = f"{config.output_api_settings['api_hostname']}/api/telegram-bot/job-application/{vacancy}"
        data = json.dumps({'from_user': from_user, 'message': message})

        async with session.post(url=url, data=data, headers=headers) as resp:
            if resp.status == 200:
                return f'Сообщение доставлено'
            else:
                return f'Сообщение не доставлно {resp.status}'


# получаем текущий список скилов для подписки
async def get_skills_for_website():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{config.output_api_settings['api_hostname']}/api/specializations") as response:
            if response.status == 200:
                data = await response.json()
                data = data.get("data")
                list_skills = data.get("list")
                return list_skills
            else:
                return False


# список подписок юзера (Stan)
async def get_skills_for_user_in_website(website_user_id):
    async with aiohttp.ClientSession() as session:
        headers = {
            'telegram-bot-token': config.output_api_settings['telegram_bot_token_for_req'],
            'accept-language': 'ru',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        url = f"{config.output_api_settings['api_hostname']}/api/telegram-bot/subscription/{website_user_id}"
        async with session.get(url, headers=headers) as response:

            if response.status == 200:
                data = await response.json()
                data = data.get("data")
                return data
            else:
                return False


# DELETE /api/telegram-bot/subscription/{user}/{subscription} - удаление подписки
async def delete_subscription_for_user_in_website(website_user_id, sub_id):
    async with aiohttp.ClientSession() as session:
        headers = {
            'telegram-bot-token': config.output_api_settings['telegram_bot_token_for_req'],
            'accept-language': 'ru',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        url = f"{config.output_api_settings['api_hostname']}/api/telegram-bot/subscription/{website_user_id}/{sub_id}"
        async with session.delete(url, headers=headers) as response:
            if response.status == 200:
                return True
            else:
                return False


# отправляем запрос для подписки на скилы
async def skills_subscription(website_user_id, account_type, skills_list):
    async with aiohttp.ClientSession() as session:
        headers = {
            'telegram-bot-token': config.output_api_settings['telegram_bot_token_for_req'],
            'accept-language': 'ru',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        url = f"{config.output_api_settings['api_hostname']}/api/telegram-bot/subscription/{website_user_id}"
        data = json.dumps({"skills": skills_list, 'type': account_type})
        async with session.post(url=url, data=data, headers=headers) as response:

            if response.status == 200:
                data = await response.json()
                return data
            else:
                return response.status


# отправляем сообщение
async def send_message(room_id, sender_id, message_text):
    async with aiohttp.ClientSession() as session:
        headers = {
            'telegram-bot-token': config.output_api_settings['telegram_bot_token_for_req'],
            'accept-language': 'ru',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        data = json.dumps({'from_user': sender_id, 'message': message_text})
        url = f"{config.output_api_settings['api_hostname']}/api/telegram-bot/message/{room_id}"
        async with session.post(url=url, data=data, headers=headers) as resp:
            if resp.status == 200:
                return f'Сообщение доставлено'
            else:
                return f'Сообщение не доставлно'


# отправляем сообщение кандидату
async def send_new_message_to_candidate(candidate, from_user, message):
    async with aiohttp.ClientSession() as session:
        headers = {
            'telegram-bot-token': config.output_api_settings['telegram_bot_token_for_req'],
            'accept-language': 'ru',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        data = json.dumps({'from_user': from_user, 'message': message})
        url = f"{config.output_api_settings['api_hostname']}/api/telegram-bot/offer/{candidate}"
        async with session.post(url=url, data=data, headers=headers) as resp:
            if resp.status == 200:
                return f'Сообщение доставлено'
            else:
                return f'Сообщение не доставлно'


# открываем контакты для вакансии которая пришла
async def open_contacts_to_company(website_id, company):
    async with aiohttp.ClientSession() as session:
        headers = {
            'telegram-bot-token': config.output_api_settings['telegram_bot_token_for_req'],
            'accept-language': 'ru'
        }
        url = f"{config.output_api_settings['api_hostname']}/api/telegram-bot/open-contacts/{website_id}/{company}"
        async with session.post(url=url, headers=headers) as resp:
            if resp.status == 200:
                return f'Контакты открыты'
            else:
                return f'Не удалось открыть контакты'
