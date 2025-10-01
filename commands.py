import os

BASE_PATH = "/home/snow/Documents/server_files/"

def list_files(path: str) -> str:
    try:
        entries = os.listdir(path)
        files = [entry for entry in entries if os.path.isfile(os.path.join(path, entry))]
        return ", ".join(files) if files else "(vacío)"
    except FileNotFoundError:
        return f"Error: Directorio '{path}' no encontrado."
    except Exception as e:
        return f"Error: {e}"

def handle_ls(tokens: list[str], username: str) -> str:
    if username is None:
        return "Debes iniciar sesión primero."
    received_path = tokens[1] if len(tokens) > 1 else ""
    return f"Archivos en {BASE_PATH}{received_path}:\n{list_files(BASE_PATH + received_path)}"

def handle_get(tokens: list[str], username: str) -> str:
    if username is None:
        return "Debes iniciar sesión primero."
    if len(tokens) < 2:
        return "Error: Debes especificar el archivo."
    received_path = tokens[1]
    try:
        with open(BASE_PATH + received_path, "r") as f:
            return f"Contenido del archivo {received_path}:\n{f.read()}"
    except FileNotFoundError:
        return f"Error: El archivo {received_path} no existe."
    except Exception as e:
        return f"Error: {e}"

def show_help():
    return """Comandos disponibles:
        - register <usuario> <contraseña> : Crear cuenta nueva
        - login <usuario> <contraseña>    : Iniciar sesión
        - ls [ruta]                        : Listar archivos
        - get <archivo>                    : Obtener contenido de un archivo
        - help                             : Mostrar esta ayuda
        - exit                             : Salir del cliente
        """
