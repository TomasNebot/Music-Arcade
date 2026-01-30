import os
import json
import numpy as np
import music21 as m21
from tensorflow import keras


SEQUENCE_LENGTH = 64
current_dir = os.path.dirname(__file__)
model_path = os.path.join(current_dir, "mel_model", "model_melody.h5")
MAPPING_PATH = os.path.join(current_dir, "mel_model", "mel_mapping_POP.json")

class MelodyGenerator:

    def __init__(self, model_path=model_path):

        self.model_path = model_path
        self.model = keras.models.load_model(model_path)

        with open(MAPPING_PATH, "r") as fp:
            self._mappings = json.load(fp)

        self._start_symbols = ["/"] * SEQUENCE_LENGTH

    def generate_melody(self, seed, num_steps, max_sequence_length, temperature):

        # Create seed with start symbols
        seed = seed.split()
        melody = seed
        seed = self._start_symbols + seed

        # map seed to int
        seed = [self._mappings[symbol] for symbol in seed]

        for _ in range(num_steps):

            # limit the seed to max_sequence_length
            seed = seed[-max_sequence_length:]

            # one-hot encode the seed
            onehot_seed = keras.utils.to_categorical(seed, num_classes=len(self._mappings))
            # (1, max_sequence_length, num of symbols in vocabulary)
            onehot_seed = onehot_seed[np.newaxis, ...]

            # make a prediction
            probabilities = self.model.predict(onehot_seed)[0]
            # [0.1, 0.2, 0.1, 0.6] -> 1
            output_int = self._sample_with_temperature(probabilities, temperature)

            # update seed
            seed.append(output_int)

            # map to our encoding
            output_symbol = [k for k, v in self._mappings.items() if v == output_int][0]

            # check if we are at the end of a melody
            if output_symbol == "/":
                break

            # update the melody
            melody.append(output_symbol)

        # Eliminar silencios
        nuevo_vector = []
        skip = 0
        for i in range(len(melody)):
            if skip > 0:
                skip -= 1
                continue
            if melody[i] == 'r' and i <= len(melody) - 4:
                if melody[i:i + 4] == ['r', '_', '_', '_']:
                    skip = 3
                else:
                    nuevo_vector.append(melody[i])
            else:
                nuevo_vector.append(melody[i])

        return nuevo_vector

    def _sample_with_temperature(selfself, probabilities, temperature):
        # temperature -> infinity //La distribucion de prob se vuelve homogennea
        # temperature -> 0 //El simbolo con mayor prob tiene prob 1, muy deterministico
        # temperature = 1 //La distribucion de prob es la normal
        predictions = np.log(probabilities) / temperature
        probabilities = np.exp(predictions) / np.sum(np.exp(predictions))

        choices = range(len(probabilities)) # [0, 1, 2, 3]
        index = np.random.choice(choices, p=probabilities)

        return index


    def save_melody(selfself, melody, step_duration=0.25, format="midi", file_name="mel.mid"):

        # create a music21 stream
        stream = m21.stream.Stream()  # Juega con m21 para crear mas de una melodia o otros tiempos

        # parse all the symbols in the melody and create note/rest objects
        # 60 _ _ _ r _ 62 _
        start_symbol = None
        step_counter = 1

        for i, symbol in enumerate(melody):

            # evento cuando tenemos nota/silencio
            if symbol != "_" or i + 1 == len(melody):

                # nos aseguramos que no estamos al principio
                if start_symbol is not None:

                    quarter_length_duration = step_duration * step_counter  # 0.25 * 4 = 1

                    # silencio
                    if start_symbol == "r":
                        m21_event = m21.note.Rest(quarterLength=quarter_length_duration)

                    # nota
                    else:
                        m21_event = m21.note.Note(int(start_symbol), quarterLength=quarter_length_duration)

                    stream.append(m21_event)

                    # resetear el contador y el simbolo
                    step_counter = 1

                start_symbol = symbol

            # evento cuando tenemos "_"
            else:
                step_counter += 1

        # write the m21 stream to a midi file
        stream.write(format, file_name)


if __name__ == "__main__":
    mg = MelodyGenerator()
    seed1 = "64 67 69 _ 69"
    seed2 = "60 _"
    melody = mg.generate_melody(seed1, 200, SEQUENCE_LENGTH, 0.8)
    print(melody)
    mg.save_melody(melody)