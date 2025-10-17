import re 

def __init__(self): pass


def split_sentence(texte, ponctuations=None):

    if ponctuations is None:
        ponctuations = [".", "!", "?"]
    
    pattern = "|".join(re.escape(p) for p in ponctuations)
    
    phrases = re.split(f"([{pattern}])", texte)
    
    phrases_completes = []
    for i in range(0, len(phrases) - 1, 2):
        if phrases[i].strip():
            phrase_complete = phrases[i].strip() + phrases[i + 1]
            phrases_completes.append(phrase_complete)
    
    if len(phrases) % 2 == 1 and phrases[-1].strip():
        phrases_completes.append(phrases[-1].strip())
    
    return phrases_completes