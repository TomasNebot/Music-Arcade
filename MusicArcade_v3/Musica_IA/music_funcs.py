import os
import time
import random
import threading
import mido
from mido import Message
import fluidsynth

from Musica_IA.song_generator import SongGenerator
from Musica_IA.melodygenerator import MelodyGenerator

from Musica_IA.song_generator import SEQUENCE_LENGTH

# #--------------MUSICA--------------# #

# Variables musica
acordes = [[60, 64, 67], [62, 65, 69], [60, 64, 67], [62, 65, 69]]
# melodia = [60, 62, 64, '_', 65, 67, 60, '_', 64, '_', 65, 67]
melodia = []
tempo = 60
crear_melodia = False
melodia_generada = False
nota_manipulada = False
note_mel = 0

ultima_deteccion_nota = 0
ultima_nota_detectada = 0
tiempo_ultima_deteccion = 0

sg = SongGenerator()
mg = MelodyGenerator()


# Funciones musica
# Función para generar y reproducir la melodía en un hilo separado ----------------------------------------------------
def notas_tutorial(tempo_deseado, nota, repeat):
    while repeat > 0:
        # Abre un puerto MIDI de salida (ajusta el nombre del puerto según tu sistema)
        with mido.open_output('Microsoft GS Wavetable Synth 0') as outport:
            # Envía una nota MIDI (nota 60 es C4, valor de 64 es velocidad o intensidad de la nota)
            note_on = Message('note_on', note=nota, velocity=100)
            outport.send(note_on)
            # Mantén la nota durante un segundo
            time.sleep(2)
            # Envía la señal de nota apagada (para detener la nota)
            note_off = Message('note_off', note=nota, velocity=100)
            outport.send(note_off)
        print("Nota enviada.")
        repeat -= 1
    print("Se murio el thread")


# Funciones para mandar semilla a la IA y crear acordes ---------------------------------------------------------------
def midi_a_nota(numero_midi):
    # Definir un diccionario que mapee los valores MIDI a notas
    midi_a_nota_dict = {
        0: "C3 G4 E5",
        1: "C#",
        2: "D4 F4 A4 D5",
        3: "D#",
        4: "E3 B3 E4 G4",
        5: "F3 A2 F2",
        6: "F#",
        7: "G2 D3 G3 B3",
        8: "G#",
        9: "A3 A4 C5",
        10: "A#",
        11: "B4 D5"
    }

    # Calcular el índice de la nota en el diccionario
    indice_nota = numero_midi % 12

    # Obtener la nota correspondiente al número MIDI
    nota = midi_a_nota_dict[indice_nota]

    return nota


def seed_gen(nota_colisionada):
    if nota_colisionada != 0:
        # Convertir valor MIDI a su nota correspondiente
        seed = midi_a_nota(nota_colisionada)
        return seed

    else:
        return None


# Funcion para convertir acordes a midi
def acordes_a_midi(notas_texto):
    # Diccionario para las notas y sus valores MIDI en la primera octava
    diccionario_notas = {
        'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4,
        'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
    }

    # Resultado para almacenar cada conjunto de notas en formato MIDI
    notas_midi = []

    for acorde in notas_texto:
        # Lista temporal para almacenar las notas MIDI del acorde actual
        acorde_midi = []
        # Divide el acorde en notas individuales
        notas = acorde.split()

        for nota in notas:
            # Extraer la nota y la octava
            base_nota = nota[:-1]  # Parte de la nota (e.g., 'C', 'G#')
            octava = int(nota[-1])  # Octava (e.g., '3' para C3)
            # Calcular el valor MIDI: (octava + 1) * 12 nos lleva al comienzo de la octava
            valor_midi = (octava + 1) * 12 + diccionario_notas[base_nota]
            acorde_midi.append(valor_midi)

        # Agrega el acorde convertido a la lista de resultados
        notas_midi.append(acorde_midi)

    return notas_midi


# Funcion de logica de creación de melodia ----------------------------------------------------------------------------
def logic_gen_mel(mg, pitch, notas_progresivas):
    global melodia
    global crear_melodia
    global melodia_generada
    global ultima_nota_detectada
    global tiempo_ultima_deteccion
    global ultima_deteccion_nota
    global nota_manipulada

    # Actualizar el valor del pitch
    for i, note_value in enumerate(notas_progresivas):
        if i < len(notas_progresivas):
            if note_value - 0.5 < pitch < note_value + 0.5:
                ultima_deteccion_nota = note_value
                if ultima_nota_detectada == ultima_deteccion_nota:
                    tiempo_actual = time.time()  # Obtener el tiempo actual
                    if tiempo_actual - tiempo_ultima_deteccion > 2:  # Verificar si ha pasado más de dos segundos
                        if not nota_manipulada:  # Verificar si la nota no ha sido manejada aún
                            gen_melodia_ia_paralelo(mg, note_value)
                            print("GENERO MELODIA")
                            melodia_generada = True
                            nota_manipulada = True  # Marcar la nota como manejada
                        else:
                            melodia_generada = False

                else:
                    ultima_nota_detectada = ultima_deteccion_nota
                    tiempo_ultima_deteccion = time.time()  # Actualizar el tiempo de la última detección de la nota
                    nota_manipulada = False  # Reiniciar la variable de control
    return melodia_generada


# Funcion para generar melodias con IA --------------------------------------------------------------------------------

def gen_melodia_ia(mg, nota):
    global melodia
    global melodia_generada
    seed = str(nota)
    melodia = mg.generate_melody(seed, 32, 64, random.uniform(0.6, 1))
    print(melodia)
    melodia_generada = True


# Funcion para generar acordes con IA ---------------------------------------------------------------------------------

def gen_acordes_ia(sg, nota, n_acordes):
    global acordes
    seed = seed_gen(nota)
    temperature = random.uniform(0.6, 1)
    # Generar acordes
    acordes_abc = sg.generate_song(seed, n_acordes, SEQUENCE_LENGTH, temperature)
    # acordes = self.sg.generate_song(seed, 4, SEQUENCE_LENGTH, temperature)
    print('GENERO ACORDES')
    print(acordes_abc)
    acordes = acordes_a_midi(acordes_abc)


# Configuración de FluidSynth con el soundfont ------------------------------------------------------------------------
current_dir = os.path.dirname(__file__)
soundfont_path = os.path.join(current_dir, "soundfont", "Arachno_SoundFont_Version_1.0.sf2")  # Cambia a la ruta de tu soundfont .sf2
fs_chords = fluidsynth.Synth()
fs_mel = fluidsynth.Synth()
fs_chords.start(driver="dsound")  # Cambia el controlador si es necesario (e.g., 'alsa' en Linux)
fs_mel.start(driver="dsound")
sfid1 = fs_chords.sfload(soundfont_path)
sfid2 = fs_mel.sfload(soundfont_path)

fs_chords.program_select(0, sfid1, 0, 0)  # Canal 0, banco 0, preset 0
fs_mel.program_select(0, sfid2, 0, 0)


# Función para reproducir acordes usando FluidSynth
def reproducir_acordes_fluidsynth(tempo, start_event=None, stop_event=None):
    global acordes
    print('Reproduciendo los nuevos acordes...')
    if start_event:
        start_event.wait()  # Espera a que se dé la señal de inicio
    while not stop_event.is_set():
        sync_event.wait()  # Sincroniza con el evento compartido
        for acorde in acordes:
            if stop_event.is_set():
                return  # Salir del bucle si se activa el stop_event
            for nota in acorde:
                fs_chords.noteon(0, nota, 100)  # Canal 0, nota, velocidad
            time.sleep(60*4 / tempo)
            for nota in acorde:
                fs_chords.noteoff(0, nota)


# Función para reproducir melodía usando FluidSynth
def reproducir_melodia_fluidsynth(tempo, start_event=None, stop_event=None):
    global melodia
    if start_event:
        start_event.wait()  # Espera a que se dé la señal de inicio
    while not stop_event.is_set():
        sync_event.wait()  # Sincroniza con el evento compartido
        print('Reproduciendo la nueva melodia...')
        print(melodia)
        for nota in melodia:
            if stop_event.is_set():
                return  # Salir del bucle si se activa el stop_event
            if nota != '_' and nota != 'r':
                fs_mel.noteon(0, int(nota), 100)  # Canal 0, nota, velocidad
                time.sleep(60 / tempo)
                fs_mel.noteoff(0, int(nota))
            else:
                time.sleep(60 / tempo)


def hilo_sincronizador(tempo, stop_event):
    while not stop_event.is_set():
        sync_event.set()  # Desbloquea los hilos sincronizados
        time.sleep(60 / tempo)  # Ajusta el tiempo según el tempo
        sync_event.clear()  # Reinicia el evento


# Funciones para ejecutar en paralelo
def iniciar_sincronizacion(tempo, stop_event):
    threading.Thread(target=hilo_sincronizador, args=(tempo, stop_event), daemon=True).start()


def iniciar_acordes_en_paralelo(tempo, start_event, stop_event):
    threading.Thread(target=reproducir_acordes_fluidsynth, args=(tempo, start_event, stop_event), daemon=True).start()


def iniciar_melodia_en_paralelo(tempo, start_event, stop_event):
    threading.Thread(target=reproducir_melodia_fluidsynth, args=(tempo, start_event, stop_event), daemon=True).start()


def gen_acordes_ia_paralelo(sg, nota, n_acordes):
    threading.Thread(target=gen_acordes_ia, args=(sg, nota, n_acordes), daemon=True).start()


def gen_melodia_ia_paralelo(mg, nota):
    threading.Thread(target=gen_melodia_ia, args=(mg, nota), daemon=True).start()


# Configuracion de notas del juego
def cambiar_notas(text):
    notas_texto = text.split()  # Separar el string en notas individuales
    notas_numeros = []  # Lista para almacenar los números MIDI de las notas

    for nota in notas_texto:
        # Extraer el número MIDI de la nota
        octava = int(nota[-1])  # Obtener la octava de la nota
        nota_base = nota[:-1]   # Obtener la nota sin la octava
        nota_midi = (octava + 1) * 12  # Calcular el valor MIDI base de la octava
        # Mapear la nota base al valor MIDI
        if nota_base == 'C':
            nota_midi += 0
        elif nota_base == 'C#':
            nota_midi += 1
        elif nota_base == 'D':
            nota_midi += 2
        elif nota_base == 'D#':
            nota_midi += 3
        elif nota_base == 'E':
            nota_midi += 4
        elif nota_base == 'F':
            nota_midi += 5
        elif nota_base == 'F#':
            nota_midi += 6
        elif nota_base == 'G':
            nota_midi += 7
        elif nota_base == 'G#':
            nota_midi += 8
        elif nota_base == 'A':
            nota_midi += 9
        elif nota_base == 'A#':
            nota_midi += 10
        elif nota_base == 'B':
            nota_midi += 11
        notas_numeros.append(nota_midi)

    return notas_texto, notas_numeros


# Ejemplo de uso en el juego:


# Evento para sincronizar el inicio de los hilos
start_chords = threading.Event()
start_mel = threading.Event()
# Evento para detener los hilos
stop_chords = threading.Event()
stop_mel = threading.Event()
# Evento para sincronizar los hilos
sync_event = threading.Event()

# Ejemplo con melodia dada
# iniciar_melodia_en_paralelo([60, 62, 64, '_', 65, 67], tempo, start_mel, stop_mel)
# iniciar_acordes_en_paralelo([[60, 64, 67], [62, 65, 69]], tempo, start_chords, stop_chords)

def main():
    iniciar_melodia_en_paralelo(tempo, start_mel, stop_mel)
    iniciar_acordes_en_paralelo(tempo, start_chords, stop_chords)

if __name__ == "__main__":
    main()
    sg = SongGenerator()
    mg = MelodyGenerator()
    print(acordes)
    start_chords.set()
    start_mel.set()
    time.sleep(1)
    gen_acordes_ia_paralelo(sg,48,11)
    time.sleep(20)
    print(acordes)
    stop_chords.set()
    stop_chords.clear()
    time.sleep(3)