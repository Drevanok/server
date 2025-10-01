import socket
import threading
import logging
from commands import handle_ls, handle_get, show_help
from session import handle_session, log
from database import init_db

HOST = "127.0.0.1"
PORT = 65432

MAX_SESSIONS = 5
MAX_REQUESTS_PER_CLIENT = 10

active_connections = 0
requests_counter = {}
lock = threading.Lock()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def handle_client(conn, addr):
    global active_connections
    username = None

    log(f"Conexión entrante: {addr} (usuario aún no identificado)")
    conn.sendall(show_help().encode("utf-8"))
    requests_counter[addr] = 0

    while True:
        try:
            data = conn.recv(1024)
        except ConnectionResetError:
            break
        if not data:
            break

        try:
            msg = data.decode("utf-8").strip()
        except UnicodeDecodeError:
            conn.sendall("Error: mensaje inválido.\n".encode("utf-8"))
            continue

        if msg == "":
            continue

        tokens = msg.split(" ")
        command = tokens[0].lower()

        # Salir
        if command == "exit":
            conn.sendall("Conexión cerrada.".encode("utf-8"))
            break

        # Límite de solicitudes
        requests_counter[addr] += 1
        if requests_counter[addr] > MAX_REQUESTS_PER_CLIENT:
            conn.sendall("Has alcanzado el límite de peticiones. Conexión cerrada.".encode("utf-8"))
            break

        # Manejar sesión (register/login)
        response, new_username = handle_session(command, tokens, addr, username)
        if new_username and new_username != username:
            username = new_username
            log(f"Usuario '{username}' conectado: {addr}")

        # Comandos que requieren sesión
        if command in ["ls", "get"]:
            if username is None:
                response = "Debes registrarte o iniciar sesión primero."
            else:
                if command == "ls":
                    response = handle_ls(tokens, username)
                elif command == "get":
                    response = handle_get(tokens, username)

        # Comando de ayuda
        elif command == "help":
            response = show_help()

        # Comando desconocido
        elif command not in ["register", "login"]:
            response = f"Comando desconocido: {command}"

        conn.sendall(response.encode("utf-8"))

    # Cleanup al cerrar conexión
    with lock:
        active_connections -= 1
    if addr in requests_counter:
        requests_counter.pop(addr)
    conn.close()
    if username:
        log(f"Usuario '{username}' desconectado: {addr}")
    else:
        log(f"Desconectado: {addr}")

def main():
    global active_connections
    init_db()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        log(f"Servidor escuchando en {HOST}:{PORT}")
        try:
            while True:
                conn, addr = s.accept()
                with lock:
                    if active_connections >= MAX_SESSIONS:
                        conn.sendall("Servidor lleno. Intenta más tarde.".encode("utf-8"))
                        conn.close()
                        continue
                    active_connections += 1

                t = threading.Thread(target=handle_client, args=(conn, addr))
                t.daemon = True
                t.start()
        except KeyboardInterrupt:
            log("Servidor detenido manualmente.", level="warning")
        finally:
            s.close()

if __name__ == "__main__":
    main()
