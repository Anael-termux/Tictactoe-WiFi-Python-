import socket
import threading

# Configuración del servidor
HOST = "192.168.1.2"  # Escucha en todas las interfaces
PORT = 5555

# Estado inicial del juego
tablero = [" "] * 9
jugador_actual = "X"
jugadores = {}  # Almacena los sockets de los jugadores
lock = threading.Lock()  # Para sincronizar el acceso al tablero

# Función para mostrar el tablero
def mostrar_tablero(tablero):
    return (
        f"{tablero[0]} | {tablero[1]} | {tablero[2]}\n"
        "--+---+--\n"
        f"{tablero[3]} | {tablero[4]} | {tablero[5]}\n"
        "--+---+--\n"
        f"{tablero[6]} | {tablero[7]} | {tablero[8]}"
    )

# Función para verificar si hay un ganador
def verificar_ganador(tablero):
    combinaciones_ganadoras = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Filas
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columnas
        (0, 4, 8), (2, 4, 6)               # Diagonales
    ]
    for combinacion in combinaciones_ganadoras:
        if tablero[combinacion[0]] == tablero[combinacion[1]] == tablero[combinacion[2]] != " ":
            return True
    return False

# Función para manejar a cada jugador
def manejar_jugador(client_socket, addr, jugador):
    global jugador_actual

    # Enviar al jugador su símbolo (X o O)
    client_socket.send(f"Eres el jugador {jugador}".encode("utf-8"))

    while True:
        try:
            # Recibir el movimiento del jugador
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                break

            movimiento = int(data) - 1  # Convertir a índice del tablero

            with lock:
                if tablero[movimiento] == " " and jugador == jugador_actual:
                    tablero[movimiento] = jugador

                    # Verificar si hay un ganador
                    if verificar_ganador(tablero):
                        for jugador_socket in jugadores.values():
                            jugador_socket.send(f"¡Jugador {jugador} ha ganado!\n{mostrar_tablero(tablero)}".encode("utf-8"))
                        break

                    # Verificar si hay un empate
                    if " " not in tablero:
                        for jugador_socket in jugadores.values():
                            jugador_socket.send(f"¡Es un empate!\n{mostrar_tablero(tablero)}".encode("utf-8"))
                        break

                    # Cambiar al siguiente jugador
                    jugador_actual = "O" if jugador_actual == "X" else "X"

                    # Enviar el estado actual del tablero a ambos jugadores
                    for jugador_socket in jugadores.values():
                        jugador_socket.send(f"Turno del jugador {jugador_actual}\n{mostrar_tablero(tablero)}".encode("utf-8"))
                else:
                    client_socket.send("Movimiento inválido. Intenta de nuevo.".encode("utf-8"))
        except:
            break

    # Cerrar la conexión
    client_socket.close()
    del jugadores[jugador]
    print(f"Jugador {jugador} ({addr}) se ha desconectado.")

# Iniciar el servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)  # Solo dos jugadores
print(f"Servidor escuchando en {HOST}:{PORT}")

# Esperar a que se conecten dos jugadores
while len(jugadores) < 2:
    client_socket, addr = server.accept()
    jugador = "X" if len(jugadores) == 0 else "O"
    jugadores[jugador] = client_socket
    print(f"Jugador {jugador} ({addr}) se ha conectado.")

    # Iniciar un hilo para manejar al jugador
    thread = threading.Thread(target=manejar_jugador, args=(client_socket, addr, jugador))
    thread.start()

    # Enviar el estado inicial del tablero a ambos jugadores
    if len(jugadores) == 2:
        for jugador_socket in jugadores.values():
            jugador_socket.send(f"Turno del jugador {jugador_actual}\n{mostrar_tablero(tablero)}".encode("utf-8"))
