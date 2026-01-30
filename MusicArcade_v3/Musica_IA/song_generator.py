import os
import json
import numpy as np
from tensorflow import keras

SEQUENCE_LENGTH = 16

current_dir = os.path.dirname(__file__)
model_path = os.path.join(current_dir, "POP909_model", "model_POP909.h5")
MAPPING_PATH = os.path.join(current_dir, "POP909_model", "mapping_POP909.json")

class SongGenerator:

    def __init__(self, model_path=model_path):

        self.model_path = model_path
        self.model = keras.models.load_model(model_path)

        with open(MAPPING_PATH, "r") as fp:
            self._mappings = json.load(fp)

        self._start_symbols = ["/"] * SEQUENCE_LENGTH

    def generate_song(self, seed, num_steps, max_sequence_length, temperature):

        # Create seed with start symbols
        # Encuentra todas las coincidencias de elementos entre paréntesis
        seed = seed.split('|')
        song = seed
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
            if output_symbol == '/':
                break

            # update the song
            song.append(output_symbol)

        # Convertir elementos de cadena a tuplas
        #song = [eval(note) for note in song]

        return song


    def _sample_with_temperature(self, probabilities, temperature):
        # temperature -> infinity //La distribucion de prob se vuelve homogennea
        # temperature -> 0 //El simbolo con mayor prob tiene prob 1, muy deterministico
        # temperature = 1 //La distribucion de prob es la normal
        predictions = np.log(probabilities) / temperature
        probabilities = np.exp(predictions) / np.sum(np.exp(predictions))

        choices = range(len(probabilities)) # [0, 1, 2, 3]
        index = np.random.choice(choices, p=probabilities)

        return index
