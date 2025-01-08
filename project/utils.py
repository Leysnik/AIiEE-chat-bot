import logging
import requests
import json
import config

# URL для API
URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

# История сообщений
message_history = [
    {"role": "system", "text": "Ты YandexGPT, виртуальный ассистент. Твоя задача - быть полезным диалоговым ассистентом."}
]

async def generate_text_yand(prompt: str):
    # Добавляем новое сообщение от пользователя в историю
    message_history.append({"role": "user", "text": prompt})
    
    # Ограничиваем историю последними 10 сообщениями (по желанию)
    if len(message_history) > 10:
        message_history.pop(0)

    body = {
        "modelUri": "gpt://b1gb4vtv137r76jho1b5/yandexgpt/rc",
        "completionOptions": {"maxTokens": 500, "temperature": 0.3},
        "messages": message_history,  # Используем всю историю сообщений
    }

    # Заголовки
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {config.API_KEY}",
        "x-folder-id": config.FOLDER_ID,
    }

    # Выполнение POST-запроса
    response = requests.post(URL, headers=headers, json=body)

    print("Status Code:", response.status_code)
    print("Response:", response.json())
    
    if response.status_code == 200:
        response_data = response.json()
        response_text = response_data['result']['alternatives'][0]['message']['text']
        # Добавляем ответ бота в историю
        message_history.append({"role": "assistant", "text": response_text})
        return response_text
    else:
        logging.error(f"Ошибка: {response.status_code}")
        return "Произошла ошибка при получении ответа."
