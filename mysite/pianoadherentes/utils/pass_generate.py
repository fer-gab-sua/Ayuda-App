import secrets
import string

def generate_random_password(length=10):
    # Definimos los caracteres que se usarán para generar la contraseña
    characters = string.ascii_letters 
    # Generamos una contraseña aleatoria
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password