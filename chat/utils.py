from asgiref.sync import sync_to_async
from django.http import Http404
from django.shortcuts import get_object_or_404

from accounts.models import MyUser
from chat.models import ChatRoom, SystemPromp, ChatHistory
from open_ai.models import SystemMessage, UserMessage, AssistantMessage
from open_ai.openai_setting import MyOpenAiClient


@sync_to_async
def get_chat_room(room_id: int) -> ChatRoom | None:
    try:
        return get_object_or_404(ChatRoom, pk=room_id)
    except Http404:
        return None


@sync_to_async
def get_all_system_prompts(room_id):
    system_prompts = SystemPromp.objects.filter(chat_room_id=room_id).all()
    return [SystemMessage(item.content) for item in system_prompts]


@sync_to_async
def get_all_chat_history(room_id):
    chat_history = ChatHistory.objects.filter(chat_room_id=room_id).all().order_by("created_at")
    history = []
    for item in chat_history:
        if item.role == 1:
            history.append(UserMessage(item.message))
        else:
            history.append(AssistantMessage(item.message))
    return history


async def ask_gpt(room_id, client: MyOpenAiClient) -> str:
    system_prompt = await get_all_system_prompts(room_id)
    history = await get_all_chat_history(room_id)
    client.set_system(*system_prompt)
    client.set_hitsory(history)

    res = await client.send()
    await add_chat_history(room_id, res.content, 2)
    return res.content


@sync_to_async
def convert_message(message: str):
    return UserMessage(message)


@sync_to_async
def add_chat_history(room_id: int, message: str, role: int) -> bool:
    chat_room = ChatRoom.objects.get(pk=room_id)
    user = MyUser.objects.get(id=chat_room.user.id)

    if role == 1:
        if user.chat_count >= 5:
            return False
        user.chat_count += 1
        user.save()

    ChatHistory.objects.create(chat_room_id=room_id, message=message, role=role).save()
    return True
