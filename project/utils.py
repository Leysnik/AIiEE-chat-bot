import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

torch.manual_seed(42)

model_name = "t-tech/T-lite-it-1.0"

tokenizer = AutoTokenizer.from_pretrained(model_name)

# инициализация модели с загрузкой на GPU
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,  #  16-битная точность для экономии памяти
).to('cuda')  # принудительная отправка модели на GPU

# функция генерации текста
async def generate_text(prompt: str) -> str:
    try:
        messages = [
            {"role": "system", "content": "Ты T-lite, виртуальный ассистент в Т-Технологии. Твоя задача - быть полезным диалоговым ассистентом."},
            {"role": "user", "content": prompt}
        ]

        input_text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # перенос данных на GPU
        model_inputs = tokenizer([input_text], return_tensors="pt").to('cuda')

        # генерация ответа
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=512,
            pad_token_id=tokenizer.eos_token_id
        )

        response = tokenizer.decode(generated_ids[0], skip_special_tokens=True)

        return response.strip()
    
    except Exception as e:
        logging.error(f"Ошибка при генерации текста: {e}")
        return "Произошла ошибка при генерации ответа."