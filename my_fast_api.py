import json

import uvicorn
from fastapi import FastAPI, Response
from pydantic import BaseModel

from bot_send_message import send_message_new_candidate, send_message_new_vacancy, send_message_for_user
from models.db_api import data_api

app = FastAPI()


class Vacancy(BaseModel):
    to_user: int
    name: str
    url: str
    company_id: int
    vacancy_id: int


class NewMessage(BaseModel):
    room_id: int
    sender_id: int
    receiver_id: int
    sender_name: str
    text: str


class Candidate(BaseModel):
    to_user: int
    name: str
    url: str
    candidate_id: int


@app.post('/new-candidate')
async def new_candidate(candidate: Candidate):
    chat_ids = data_api.get_employer_telegram_id(candidate.to_user)
    if chat_ids:
        data_api.user_notification_counter_update(candidate.to_user)
        for chat_id in chat_ids:
            await send_message_new_candidate(chat_id=chat_id,
                                             candidate_id=candidate.candidate_id,
                                             name=candidate.name,
                                             url=candidate.url)

    data = {'status': True, 'error': 'no_errors'}
    data = json.dumps(data)

    return Response(content=data, media_type="application/xml", status_code=200)


@app.post('/new-vacancy')
async def new_vacancy(vacancy: Vacancy):
    chat_ids = data_api.get_candidate_telegram_id(vacancy.to_user)
    if chat_ids:
        for chat_id in chat_ids:
            data_api.user_notification_counter_update(vacancy.to_user)
            await send_message_new_vacancy(chat_id=chat_id,
                                           company_id=vacancy.company_id,
                                           vacancy_id=vacancy.vacancy_id,
                                           name=vacancy.name,
                                           url=vacancy.url)

    data = {'status': True, 'error': 'no_errors'}
    data = json.dumps(data)

    return Response(content=data, media_type="application/xml", status_code=200)


@app.post('/new-message')
async def new_message(message: NewMessage):
    chat_ids = data_api.get_user_telegram_id(message.receiver_id)
    if chat_ids:
        for chat_id in chat_ids:
            await send_message_for_user(chat_id=chat_id,
                                        room_id=message.room_id,
                                        sender_name=message.sender_name,
                                        text=message.text)

    data = {'status': True, 'error': 'no_errors'}
    data = json.dumps(data)

    return Response(content=data, media_type="application/xml", status_code=200)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

