from utils import generate_text_yand

# Функция для генерации задания
async def generate_daily_task():
    prompt = """
        Составь интерактивное задание для тренировки памяти, которое можно выполнить вместе с ботом. При составлении задания не используй никакой разметки, пиши как обычный человек, без выделений и символов форматирования. Задание должно быть подробным и содержать следующие элементы:  

        1. Название задания. Придумай яркий и запоминающийся заголовок.  

        2. Цель задания. Объясни, какая часть памяти будет развиваться и зачем это важно.  

        3. Материалы для выполнения. Укажи, что понадобится для выполнения задания. Если ничего не нужно, уточни, что задание выполняется только с ботом.  

        4. Этапы выполнения задания. Опиши пошагово процесс выполнения задания. Каждый шаг должен содержать четкое описание действий и роли бота на этом этапе.  

        5. Время на выполнение. Укажи примерное время для выполнения каждого этапа.  

        6. Интерактивные элементы. Укажи, какие вопросы, проверки или задания бот будет задавать пользователю, чтобы сделать процесс увлекательным и полезным.  

        Напиши всё простым текстом, чтобы пользователь мог легко понять и следовать инструкциям.
    """
    
    res = await generate_text_yand(prompt)

    return res
