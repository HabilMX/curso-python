# fig05_05.py
LIMITE = 400


def es_error(codigo: int) -> bool:
    match codigo:
        case LIMITE:
            return True
        case _:
            return False
