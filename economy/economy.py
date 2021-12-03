import os
import pandas as pd

from .constants import ECON_FILE

class Economy:
    def __init__(self, server):
        # Parse the server name before creating or accessing the file for it
        parsed_server_name = ' '.join(server.split())
        parsed_server_name = parsed_server_name.replace(' ', '-')
        parsed_server_name = ''.join(char for char in parsed_server_name if char.isalnum())

        self.econ_file = ECON_FILE.replace('SERVER', parsed_server_name)
        self.scores = self.load(self.econ_file) if os.path.exists(self.econ_file) else {}

    def update(self, name, score):
        self.scores[name] = score

    def add(self, name, score):
        if name not in self.scores.keys():
            self.scores[name] = score
        else:
            self.scores[name] += score

    def remove(self, name, score):
        if name not in self.scores.keys():
            print('Cannot remove score from a user with no score')
            return None
        self.scores[name] -= score

    def load(self, fp):
        scores_df = pd.read_csv(fp, index_col=0)
        scores = scores_df.to_dict(orient='index')
        scores = {name: score['Score'] for name, score in scores.items()}
        return scores

    def save(self):
        scores_df = pd.DataFrame([{'Name': name, 'Score': score} for name, score in self.scores.items()])
        scores_df.set_index('Name')

        # Generate the necessary file structure if it does not exist
        out_folder = self.econ_file[:self.econ_file.rfind('/')]
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        scores_df.to_csv(self.econ_file, index=False)

    def get_sorted_scores(self):
        sorted_scores = sorted([(name, score) for name, score in self.scores.items()], key=lambda x:x[1], reverse=True)
        for score in sorted_scores:
            yield score

    def get_rankings(self, limit : int = 10):
        # Get the actual rank numbers for the users up to the given limit
        rank = 1
        num_tied = 0
        prev_score = None
        for i, score in enumerate(self.get_sorted_scores()):
            if i == limit:
                raise StopIteration
            # Only increment the rank when the next ranked is actually lower and not tied
            if prev_score and score[1] < prev_score:
                rank += 1 + num_tied
                num_tied = 0
            elif score[1] == prev_score:
                num_tied += 1
            yield (rank, *score)
            prev_score = score[1]