import socket
import threading
from commands import handle_ls, handle_get, show_help
from session import handle_session
from database import init_db

HOST = "127.0.0.1"
PORT = 65432

MAX_SESSIONS = 5               
MAX_REQUESTS_PER_CLIENT = 10   

active_connections = 0          
active_sessions = {}            
requests_counter = {}           

lock = threading.Lock()         

def handle_client(conn, addr):
    global active_connections
    username = None

    # Show commands on new connection
    conn.sendall(show_help().encode("utf-8"))

    # request count per client
    requests_counter[addr] = 0

    while True:
        try:
            data = conn.recv(1024)
        except ConnectionResetError:
            break 
        if not data:
            break

        # Securely decode message
        try:
            msg = data.decode("utf-8").strip()
        except UnicodeDecodeError:
            conn.sendall("Error: mensaje inválido.\n".encode("utf-8"))
            continue

        if msg == "":
            continue  # Ignore empty messages
        
        tokens = msg.split(" ")
        command = tokens[0].lower()

        # Close connection on exit command
        if command == "exit":
            conn.sendall("Conexión cerrada.".encode("utf-8"))
            break

        # Limit requests per client
        requests_counter[addr] += 1
        if requests_counter[addr] > MAX_REQUESTS_PER_CLIENT:
            conn.sendall("Has alcanzado el límite de peticiones. Conexión cerrada.".encode("utf-8"))
            break

    
        # Manage session (register/login/logout)
        response, username = handle_session(command, tokens, addr, username, active_sessions)

        if response == "":
            if username is None:
                response = "Debes registrarte o iniciar sesión primero."
            else:
                match command:
                    case "ls":
                        response = handle_ls(tokens)
                    case "get":
                        response = handle_get(tokens)
                    case "logout":
                        response = "Sesión cerrada."
                        if addr in active_sessions:
                            active_sessions.pop(addr)
                        username = None
                    case "help":
                        response = show_help()
                    case _:
                        response = f"Comando desconocido: {command}"

        conn.sendall(response.encode("utf-8"))

    # Cleanup to close connection
    with lock:
        active_connections -= 1
    if addr in active_sessions:
        active_sessions.pop(addr)
    if addr in requests_counter:
        requests_counter.pop(addr)
    conn.close()
    print(f"Desconectado: {addr}")

def main():
    global active_connections
    init_db()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor escuchando en {HOST}:{PORT}")
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
            print("\nServidor detenido manualmente.")
        finally:
            s.close()

if __name__ == "__main__":
    main()
