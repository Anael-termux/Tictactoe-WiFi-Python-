import socket

# Configuración del cliente
HOST = "192.168.1.2"  # IP del servidor
PORT = 5555

# Conectar al servidor
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Recibir el símbolo del jugador (X o O)
simbolo = client_socket.recv(1024).decode("utf-8")
print(simbolo)

while True:
    # Recibir el estado del tablero y el turno actual
    data = client_socket.recv(1024).decode("utf-8")
    print(data)

    if "ganado" in data or "empate" in data:
        break

    # Si es el turno del jugador, enviar un movimiento
    if f"Turno del jugador {simbolo[-1]}" in data:
        movimiento = input("Elige una posición (1-9): ")
        client_socket.send(movimiento.encode("utf-8"))

# Cerrar la conexión
client_socket.close()