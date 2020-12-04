from tetris_client import GameClient
import random
import logging
from typing import Text
from tetris_client import TetrisAction
from tetris_client import Board
from tetris_client import Element
import copy

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)

#все возможные варианты фигур после поворота
rotations_nedeed = {
    "O" : [0],
    "I": [0, 1],
    "J": [0, 1, 2, 3],
    "L": [0, 1, 2, 3],
    "S": [0, 1],
    "Z": [0, 1],
    "T": [0, 1, 2, 3],
}

def turn(gcb: Board) -> TetrisAction:
   
    print(gcb.get_current_figure_type())
    print(gcb.get_current_figure_point())
    
    board = gcb._line_by_line().split('\n')
    for i, line in enumerate(board):
        board[i] = list(line)
    board.reverse()
    print(remove_figure_from_board(gcb.get_current_figure_type(), gcb.get_current_figure_point(), board))


    
    actions = [x for x in TetrisAction if x.value != "act(0,0)"]
    return [TetrisAction.DOWN]
            
     # это те действия, которые выполнятся на игровом сервере в качестве вашего хода

#нужна для find_perimeter
def count_sides(x, y, board):
    neighbours_pos = [(x+1, y), (x, y+1), (x-1, y), (x, y-1)]
    sides = 0
    for neighbour_pos in neighbours_pos:
        x_n, y_n = neighbour_pos
        if 0 <= x_n < 18 and 0 <= y_n < 18:
            if board[y_n][x_n] == '.':
                sides+=1
        else:
            sides+=1
    return sides

#находит периметр фигур на поле
def find_perimeter(board):
    perimeter = 0
    for y, row in enumerate(board):
        for x, el in enumerate(row):
            if el != '.':
                perimeter += count_sides(x, y, board)
    return perimeter


#находит все возможные варианты нахождения фигуры
def predict_positions(figure_type, figure_point):
    positions = []
    rotations = rotations_nedeed.get(figure_type)
    figure = Element(figure_type)
    for rotation in rotations:
        position = [[point.get_x(), point.get_y()] for point in figure.get_all_coords_after_rotation(figure_point, rotation=rotation)]
        position.sort(key=lambda x: x[0])
        position_to_right = position
        offset = 0;
        positions.append([offset, rotation, position]) # middle position
        while position[0][0] != 0:
            offset -= 1
            for point in position:
                point[0] -= 1
            positions.append([offset, rotation, position]) # move to left positions
        while position_to_right[-1][0] != 17:
            offset += 1
            for point in position_to_right:
                point[0] += 1   
            positions.append([offset, rotation, position_to_right]) # move to left positions
    for position in positions:
        need_to_move_down = 0
        for point in position[2]:
            need_to_move_down = max([need_to_move_down, point[1]-17])
        if need_to_move_down != 0:
            for point in position[2]:
                point[1] -= need_to_move_down

    return sorted(positions, key=lambda x: x[0]);   


# все варианты падения фигуры
def predict_landing(figure_type, figure_point, board):
    positions = predict_positions(figure_type, figure_point)
    boards = []
    for position in positions:
        collapse = False
        while not collapse:
            for point in position[2]:
                if point[1] == 0:
                    collapse = True
                    break
                if board[point[1]-1][point[0]] != '.':
                    collapse = True
                    break
            if not collapse:
                for point in position[2]:
                    point[1] -= 1
        new_board = copy.deepcopy(board)
        for point in position[2]:
            new_board[point[1]][point[0]] = figure_type
        boards.append(new_board)
    return boards

# удаление фигуры с поля (нужно для упрощения дальнейшей обработки)
def remove_figure_from_board(figure_type, figure_point, board):
    figure = Element(figure_type)
    position = [[point.get_x(), point.get_y()] for point in figure.get_all_coords_after_rotation(figure_point, 0)]
    for point in position:
        if 0<=point[0]<18 and 0<=point[1]<18:
            board[point[1]][point[0]] = '.'
    return board

# высота фигур на поле
def get_height(board):
    return board.index(['.' for _ in range(18)])

# поиск дыр
def count_holes(board):
    pass

def main(uri: Text):
    """
    uri: url for codebattle game
    """
    gcb = GameClient(uri)
    gcb.run(turn)


if __name__ == "__main__":
    # в uri переменную необходимо поместить url с игрой для своего пользователя
    # put your game url in the 'uri' path 1-to-1 as you get in UI
    uri = "http://codebattle2020.westeurope.cloudapp.azure.com/codenjoy-contest/board/player/aw4jqc1cry0tzt658hvm?code=1595073418621740968&gameName=tetris#"
    main(uri)
