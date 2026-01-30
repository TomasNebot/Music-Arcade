from pythonosc import dispatcher
from pythonosc import osc_server
import threading
import time

# Variables comunicacion
server = 0
msgL = [0, 0]
msgR = [0, 0]


# Funciones para comunicacion
def osc_setup():
    global server

    # Creamos un cliente UDP para enviar mensajes OSC
    # client = udp_client.SimpleUDPClient("127.0.0.1", 12001)

    # Creamos un despachador para manejar los mensajes OSC entrantes
    dispatcher_instance = dispatcher.Dispatcher()
    dispatcher_instance.map("/pitchL", handle_msg)
    dispatcher_instance.map("/pitchR", handle_msg)

    # Configuramos el servidor OSC para escuchar en el puerto 12000
    server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 12000), dispatcher_instance)
    print("Servidor OSC iniciado en el puerto 12000")

    return server


def osc():
    global server
    # Iniciamos el servidor en un hilo separado
    server_thread = server.serve_forever()
    return


def handle_msg(address, *args):
    global pitch, amplitud, msgR, msgL
    pitch = args[0]
    amplitud = args[1]
    if(address == "/pitchL"):
        msgL = [pitch, amplitud]
    else:
        msgR = [pitch, amplitud]


def get_msgL():
    """Retorna el valor actual de msgL."""
    global msgL
    return msgL


def get_msgR():
    """Retorna el valor actual de msgL."""
    global msgR
    return msgR


def iniciar_osc():
    threading.Thread(target=osc, daemon=True).start()


def stop_osc():
    server.shutdown()

def var_com():
    # Var com
    global server
    global msgL
    global msgR

def main():
    var_com()

    # Setup servidor com
    osc_setup()

    # Inicializa hilo que "escucha" a Pd
    iniciar_osc()

    time.sleep(10)

    # Parar servidor de osc
    stop_osc()

if __name__ == "__main__":
    main()