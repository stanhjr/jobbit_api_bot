import json

import aiohttp

import config


# get user data in website
async def get_user_account_details(token):
    async with aiohttp.ClientSession() as session:
        headers = {
            'telegram-bot-token': config.output_api_settings['telegram_bot_token_for_req'],
            'accept-language': 'ru',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
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


# reply with a message for new vacancy
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


# get main list of skills
async def get_skills_for_website(type_id):
    async with aiohttp.ClientSession() as session:
        url = f"{config.output_api_settings['api_hostname']}/api/specializations"
        params = (
            ('type_id', type_id),
        )
        async with session.get(url=url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                data = data.get("data")
                list_skills = data.get("list")
                return list_skills
            else:
                return False


# get main list of skills
async def get_skills_for_type_id_for_website(type_id):
    async with aiohttp.ClientSession() as session:
        params = (
            ('type_id', type_id),
        )
        url = f"{config.output_api_settings['api_hostname']}/api/specializations"
        async with session.get(url=url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                data = data.get("data")
                list_skills = data.get("list")
                return list_skills
            else:
                return False


# list user subscriptions
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


# delete subscriptions for skills
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


# send a request for subscriptions to skills
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
                return {"response_code": response.status}


# send message
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


# send message to candidate
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


# open contacts for employer
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
