def divide_text_into_parts(text : str, maximum_length : int= 13000):
    text_parts = []
    start = 0
    while start < len(text):
        end = start + maximum_length

        if end >= len(text):
            text_parts.append(text[start:].strip())
            break

        cutting = text.rfind(". ", start, end + 1)
        if cutting == -1 or cutting <= start:
            cutting = end
        else:
            cutting += 2  

        text_parts.append(text[start:cutting])
        start = cutting

    return text_parts

