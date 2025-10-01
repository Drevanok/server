import logging
from auth import register_user, authenticate

# Configuración logging
logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def log(message: str):
    """Loggea en consola y archivo"""
    print(message, flush=True)
    logging.info(message)

def handle_session(command, tokens, addr, current_user):
    """
    Maneja comandos de sesión: register y login
    """
    response = ""
    username = current_user

    if username is None:
        if command == "register":
            if len(tokens) < 3:
                response = "Uso: register <usuario> <contraseña>"
            else:
                u, p = tokens[1], tokens[2]
                if register_user(u, p):
                    response = f"Registro exitoso. Usuario '{u}' creado. Ahora haz login."
                else:
                    response = f"Error: el usuario '{u}' ya existe."

        elif command == "login":
            if len(tokens) < 3:
                response = "Uso: login <usuario> <contraseña>"
            else:
                u, p = tokens[1], tokens[2]
                if authenticate(u, p):
                    username = u
                    log(f"Usuario '{u}' inició sesión desde {addr}")
                    response = f"Login exitoso. Bienvenido {u}"
                else:
                    response = "Login fallido: credenciales inválidas"

        else:
            response = "Debes registrarte o iniciar sesión primero."

    return response, username
