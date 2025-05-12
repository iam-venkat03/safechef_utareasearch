
def format_exam(questions):
    """
    Da formato a las preguntas seleccionadas en un examen con clave de respuestas.
    """
    exam_text = "### Examen de Práctica de 20 Preguntas\n\n"
    answer_key_text = "\n### Clave de Respuestas\n\n"
    
    for i, q in enumerate(questions, start=1):
        exam_text += f"**Pregunta {i}:**\n{q['question']}\n"
        for letter in ["A", "B", "C", "D"]:
            exam_text += f"{letter}. {q['choices'][letter]}\n"
        exam_text += "\n"
        
        if q.get('answer'):
            answer_key_text += f"{i}. **{q['answer']}**\n"
        else:
            answer_key_text += f"{i}. Respuesta no proporcionada\n"
    
    return exam_text + answer_key_text

def parse_questions_and_answers(text):
    """
    Parsea el texto del examen diagnóstico para extraer las preguntas, opciones y la clave de respuestas.
    
    Se asume que las preguntas siguen un patrón similar a:
    "1. Texto de la pregunta A. Opción A B. Opción B C. Opción C D. Opción D"
    
    Retorna una lista de diccionarios con las claves: 'num', 'question', 'choices' y 'answer'.
    """
    import re

    question_pattern = re.compile(
        r"(?P<num>\d+)[\.\)]\s+(?P<question>.*?)\s+"
        r"A\.\s*(?P<A>.*?)\s+"
        r"B\.\s*(?P<B>.*?)\s+"
        r"C\.\s*(?P<C>.*?)\s+"
        r"D\.\s*(?P<D>.*?)(?=\d+[\.\)]|$)",
        re.DOTALL
    )
    
    answer_key_pattern = re.compile(
        r"(?P<num>\d+)[\.\):\-]+\s*(?P<ans>[A-D])", re.DOTALL
    )
    
    questions = []
    for match in question_pattern.finditer(text):
        qnum = match.group("num").strip()
        qtext = match.group("question").strip().replace("\n", " ")
        choices = {
            "A": match.group("A").strip().replace("\n", " "),
            "B": match.group("B").strip().replace("\n", " "),
            "C": match.group("C").strip().replace("\n", " "),
            "D": match.group("D").strip().replace("\n", " ")
        }
        questions.append({
            "num": qnum,
            "question": qtext,
            "choices": choices,
            "answer": None
        })
    
    answer_key = {}
    for match in answer_key_pattern.finditer(text):
        num = match.group("num").strip()
        ans = match.group("ans").strip()
        answer_key[num] = ans

    # Actualiza cada pregunta con su respuesta correspondiente si está disponible
    for q in questions:
        if q["num"] in answer_key:
            q["answer"] = answer_key[q["num"]]
    
    return questions
