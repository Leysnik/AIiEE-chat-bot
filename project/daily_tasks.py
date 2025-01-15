from utils import generate_text_yand

# Функция для генерации задания
def generate_daily_task():
    """
    Генерирует подробное интерактивное задание для тренировки памяти, которое можно выполнить вместе с ботом
    Задание включает следующие элементы: название задания, цель, материалы, этапы выполнения, время на выполнение
    и интерактивные элементы, которые бот будет использовать для вовлечения пользователя

    Возвращает:
        str: Текст задания для тренировки памяти, который будет отправлен пользователю через бота.
    """
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
    
    res = generate_text_yand(prompt)

    return res

def generate_words(count):
    """
    Генерирует случайный набор слов для интерактивного задания с ботом. Эти слова не должны быть связаны логически
    и не содержат знаков препинания. Слова могут быть использованы, например, для тренировки запоминания или других
    игр с ботом

    Аргументы:
        count (int): Количество слов, которое необходимо сгенерировать

    Возвращает:
        list: Список строк, где каждая строка представляет собой одно слово. Если слова не удалось сгенерировать,
              возвращается None
    """
    prompt = '''Составь {count} слов для интерактивного задания с ботом(эти слова не должны быть связаны нормами языка, просто {count} слов).
               Не используй знаки препинания, должны быть только слова, отделенные пробелом.
    '''
    content = generate_text_yand(prompt.format(count=count))
    if content is None:
        return None
    words = content.split()
    return words
