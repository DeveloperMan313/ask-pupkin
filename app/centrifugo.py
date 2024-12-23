from cent import Client, PublishRequest
from ask_pupkin.settings import (
    CENTRIFUGO_SECRET_KEY,
    CENTRIFUGO_API_KEY,
    CENTRIFUGO_WS_URL,
    CENTRIFUGO_API_URL,
)
from .models import Answer
from .templatetags.pfp import get_pfp_url
import jwt
import time


def get_centrifugo_user_info(user_id: int):
    claims = {'sub': str(user_id), 'exp': int(time.time()) + 10 * 60}
    token = jwt.encode(claims, CENTRIFUGO_SECRET_KEY, algorithm='HS256')
    return {'token': token, 'ws_url': CENTRIFUGO_WS_URL}


def publish_answer(question_id: int, answer: Answer):
    client = Client(CENTRIFUGO_API_URL, CENTRIFUGO_API_KEY)
    request = PublishRequest(
        channel=str(question_id),
        data={
            'question_id': question_id,
            'answer_id': answer.pk,
            'pfp_url': get_pfp_url(answer.user.profile.picture),
            'answer_text': answer.text,
        },
    )
    client.publish(request)
