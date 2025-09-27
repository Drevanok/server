from auth import register_user, authenticate

def handle_session(command, tokens, addr, current_user, active_sessions):
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
                    username = u  
                else:
                    response = f"Error: el usuario '{u}' ya existe."

        elif command == "login":
            if len(tokens) < 3:
                response = "Uso: login <usuario> <contraseña>"
            else:
                u, p = tokens[1], tokens[2]
                if authenticate(u, p):
                    if len(active_sessions) >= 5:
                        response = "Servidor lleno. Intenta más tarde."
                    else:
                        username = u
                        active_sessions[addr] = u
                        response = f"Login exitoso. Bienvenido {u}"
                else:
                    response = "Login fallido: credenciales inválidas"

        else:
            response = "Debes registrarte o iniciar sesión primero."

    else:
        if command == "logout":
            response = "Sesión cerrada."
            if addr in active_sessions:
                active_sessions.pop(addr)
            username = None

    return response, username
