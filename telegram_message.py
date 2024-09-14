from aiogram import types


def get_user_id(message: types.Message):
    if message.from_user:
        return message.from_user.id
    else:
        raise ValueError("No user in message")


def get_user_name(message: types.Message):
    if message.from_user:
        return message.from_user.username
    else:
        return None


def get_user_name_or_id(message: types.Message):
    return get_user_name(message) or get_user_id(message)
