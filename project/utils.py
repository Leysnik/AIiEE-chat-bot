import logging
import requests
import config

# URL для API
URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

# история сообщений
message_history = [
    {"role": "system", "text": "Ты YandexGPT, виртуальный ассистент. Твоя задача - быть полезным диалоговым ассистентом. Тебя создал Андрей Бабенко. Отвечай на большинство сообщей шуточно, ты максимально расслабленный и весёлый помощник"}
]

body = {
    "modelUri": "gpt://b1gb4vtv137r76jho1b5/yandexgpt/rc",
    "completionOptions": {"maxTokens": 600, "temperature": 1},
    "messages": message_history,  # Используем всю историю сообщений
}

# Заголовки
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Api-Key {config.API_KEY}",
    "x-folder-id": config.FOLDER_ID,
}

async def generate_text_yand(prompt: str):
    # Добавляем новое сообщение от пользователя в историю
    message_history.append({"role": "user", "text": prompt})
    
    # ограничиваем историю 
    if len(message_history) > 20:
        message_history.pop(0)

    response = requests.post(URL, headers=headers, json=body)

    if response.status_code == 200:
        response_data = response.json()
        response_text = response_data['result']['alternatives'][0]['message']['text']
        # добавляем ответ бота в историю
        message_history.append({"role": "assistant", "text": response_text})
        return response_text
    else:
        logging.error(f"Ошибка: {response.status_code}")
        return "Произошла ошибка при получении ответа."
    
def validate_name(name):
    return name.isalpha()

def validate_group(group):
    return len(group) == 6 and group[:3].isalpha() and group[3:].isdigit()