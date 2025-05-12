# selection_agent.py

import random

def select_balanced_questions(questions, num_questions=20):
    """
    Selecciona y retorna un subconjunto balanceado de preguntas.
    
    En este ejemplo se barajan las preguntas y se toman las primeras 'num_questions'.
    """
    if len(questions) < num_questions:
        raise ValueError("No hay suficientes preguntas para seleccionar la cantidad deseada.")
    random.shuffle(questions)
    return questions[:num_questions]
