'''
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from IPython.display import display, Markdown


# Инициализация модели и токенизатора
torch.manual_seed(42)
model_name = "t-tech/T-lite-it-1.0"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name, 
    torch_dtype="auto",
    device_map="auto",
)

# Функция для генерации задания
def generate_daily_task():
    prompt = """
    Напиши задание для развития памяти. Задание должно включать:

    - Заголовок задания
    - Цель задания
    - Материалы для выполнения
    - Пошаговое описание задания (с подзаголовками для каждого этапа)
    - Время на каждый этап

    Задание должно быть связано с развитием памяти, например, с упражнением на запоминание деталей.
    """

    # Формируем запрос к модели
    messages = [
        {"role": "system", "content": "Ты T-pro, виртуальный ассистент в Т-Технологии. Твоя задача - быть полезным диалоговым ассистентом."},
        {"role": "user", "content": prompt}
    ]
    
    # Преобразуем в формат модели
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
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
    
    return response

# Получение сгенерированного задания
daily_task = generate_daily_task()

# Отображение сгенерированного задания с использованием Markdown
display(Markdown(daily_task))
'''