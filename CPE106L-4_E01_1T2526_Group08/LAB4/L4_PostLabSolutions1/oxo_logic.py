import random
import os
import oxo_data

class Game:
    def __init__(self):
        """Initializes a new empty Tic-Tac-Toe game board."""
        self.board = list(" " * 9)
        self.winner = None
    
    def new_game(self):
        """Resets the game to a new empty state."""
        self.board = list(" " * 9)
        self.winner = None
    
    def save_game(self):
        """Saves the current game state to disk."""
        oxo_data.saveGame(self.board)
    
    def restore_game(self):
        """Restores a previously saved game."""
        try:
            game = oxo_data.restoreGame()
            if len(game) == 9:
                self.board = game
                return True
            else:
                self.new_game()
                return False
        except IOError:
            self.new_game()
            return False
    
    def _generate_move(self):
        """Generates a random move for the computer."""
        options = [i for i in range(len(self.board)) if self.board[i] == " "]
        if options:
            return random.choice(options)
        return -1
    
    def _is_winning_move(self):
        """Checks if the current board has a winning line."""
        wins = ((0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6))
        for a, b, c in wins:
            if self.board[a] == self.board[b] == self.board[c] != " ":
                self.winner = self.board[a]
                return True
        return False
    
    def user_move(self, cell):
        """Handles the user's move and checks for a win."""
        if self.board[cell] != " ":
            raise ValueError('Invalid cell')
        self.board[cell] = 'X'
        if self._is_winning_move():
            return 'X'
        return ""
    
    def computer_move(self):
        """Makes the computer's move and checks for a win."""
        cell = self._generate_move()
        if cell == -1:
            return 'D'  # Draw
        self.board[cell] = 'O'
        if self._is_winning_move():
            return 'O'
        return ""
    
    def __str__(self):
        """Returns the current state of the game as a string."""
        return f"{self.board[0]} | {self.board[1]} | {self.board[2]}\n" + \
               f"--------\n" + \
               f"{self.board[3]} | {self.board[4]} | {self.board[5]}\n" + \
               f"--------\n" + \
               f"{self.board[6]} | {self.board[7]} | {self.board[8]}\n"

def test():
    """Runs the Tic-Tac-Toe game with user and computer turns."""
    game = Game()
    result = ""
    
    while not result:
        print(game)
        try:
            result = game.user_move(game._generate_move())
        except ValueError:
            print("Oops, that shouldn't happen")
        
        if not result:
            result = game.computer_move()
        
        if result == 'D':
            print("It's a draw!")
        elif result:
            print(f"Winner is: {result}")
        print(game)

if __name__ == "__main__":
    test()
