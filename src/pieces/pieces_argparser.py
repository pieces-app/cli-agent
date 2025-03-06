import argparse
import sys
from pieces.settings import Settings


# subclassing the ArgumentParser class to modify the error messages
class PiecesArgparser(argparse.ArgumentParser):
    parser: "PiecesArgparser"

    def error(self, message):
        if 'invalid choice' in message:
            try:
                invalid_command = message.split("'")[1]
                similar_command = self.find_most_similar_command(
                    list(self._subparsers._group_actions[0].choices.keys()),
                    invalid_command)
                suggestion_text = (
                    f"Did you mean {similar_command}?"
                )
                # Custom error message for invalid command choices
                print(f"Invalid command "
                      f"'{invalid_command}'\n{suggestion_text}")
            except IndexError:
                suggestion_text = ""
                invalid_command = "Unknown"
                # Custom error message for invalid command choices
                print(f"Invalid command "
                      f"'{invalid_command}'\n{suggestion_text}")
            except AttributeError:
                Settings.show_error("Error occured", message)

        else:
            # Default error message for other types of errors
            Settings.show_error("Error occured", message)
        sys.exit(2)

    @classmethod
    def levenshtein_distance(cls, s1, s2):
        # If s1 is shorter than s2, swap them to minimize the number of operations
        if len(s1) < len(s2):
            return cls.levenshtein_distance(s2, s1)

        # If one of the strings is empty, the distance is the length of the other string
        if len(s2) == 0:
            return len(s1)

        # Initialize the previous row of distances
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            # Initialize the current row, starting with the deletion distance
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Calculate the cost of insertions, deletions, and substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                # Append the minimum cost of the operations to the current row
                current_row.append(min(insertions, deletions, substitutions))
            # Set the current row as the previous row for the next iteration
            previous_row = current_row

        # The last element of the previous row contains the levenshtein distance
        return previous_row[-1]

    @classmethod
    def find_most_similar_command(cls, valid_commands, user_input):
        # Calculate the Levenshtein distance between the user input and each valid command
        distances = {cmd: cls.levenshtein_distance(
            user_input, cmd) for cmd in valid_commands}
        # Find the command with the smallest Levenshtein distance to the user input
        most_similar_command = min(distances, key=distances.get)
        return most_similar_command
