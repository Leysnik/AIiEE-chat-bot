import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import asyncio

# Инициализация модели и токенизатора
torch.manual_seed(42)
model_name = "t-tech/T-lite-it-1.0"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)

# Функция для генерации текста
async def generate_text(prompt) -> dict:
    try:
        # Формируем запрос
        messages = [
            {"role": "system", "content": "Ты T-lite, виртуальный ассистент в Т-Технологии. Твоя задача - быть полезным диалоговым ассистентом."},
            {"role": "user", "content": prompt}
        ]
        
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Подготовка входных данных для модели
        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        # Генерация текста
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=256
        )

        # Извлекаем сгенерированный текст
        generated_ids = [
            output_ids[len(model_inputs.input_ids[0]):] for output_ids in generated_ids
        ]
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        return response, len(response.split())  # Возвращаем сгенерированный текст и количество токенов
    except Exception as e:
        logging.error(e)
        return None, 0


'''
async def main():
    prompt = "Напиши стих про машинное обучение"
    response, token_count = await generate_text(prompt)
    if response:
        print(f"Ответ: {response}")
        print(f"Количество токенов: {token_count}")

# Запуск асинхронной функции
asyncio.run(main())
'''