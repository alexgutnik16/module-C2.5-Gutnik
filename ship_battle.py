import time
from random import randint


class BoardException(Exception):
    pass


class BoardWrongShipException(BoardException):
    pass


class OutBoardException(BoardException):
    def __str__(self):
        return "Вы хотите выстрелить за доску!"


class BusyDotException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, length, orientation):
        self.length = length
        self.bow = bow
        self.orientation = orientation
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.orientation == 0:
                cur_x += i

            elif self.orientation == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]
        self.ships = []
        self.busy = []

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.busy.append(dot)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [(-1, 1), (0, 1), (1, 1),
                (-1, 0), (0, 0), (1, 0),
                (-1, -1), (0, -1), (1, -1)]
        for dot in ship.dots:
            for dotx, doty in near:
                cur = Dot(dot.x + dotx, dot.y + doty)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):
        res = "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"
        if self.hid:
            res = res.replace("■", "0")
        return res

    def out(self, dot):
        return not((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def shot(self, dot):
        if self.out(dot):
            raise OutBoardException()
        if dot in self.busy:
            raise BusyDotException()

        self.busy.append(dot)

        for ship in self.ships:
            if dot in ship.dots:
                ship.lives -= 1
                self.field[dot.x][dot.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль потоплен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[dot.x][dot.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        dot = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {dot.x+1, dot.y+1}")
        return dot


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()
            if len(cords) != 2:
                print("Введиите 2 координаты! ")
                continue
            x, y = cords
            if not((x.isdigit()) and (y.isdigit())):
                print("Введите числа! ")
                continue
            x, y = int(x), int(y)
            return Dot(x-1, y-1)


class Game:
    def __init__(self, size=6):
        self.ship_lens = [3, 2, 2, 1, 1, 1, 1]
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.user = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        board = Board(size=self.size)
        attempts = 0
        for length in self.ship_lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    @staticmethod
    def greet():
        print("---------------------")
        print("   Добро пожаловать  ")
        print("        в игру       ")
        print("     Морской Бой     ")
        print("---------------------")
        print("  Формат ввода: x y  ")
        print("  x - номер строки   ")
        print("  y - номер столбца  ")

    def loop(self):
        time.sleep(1)
        num = 0
        while True:
            print("-"*21)
            print("Доска пользователя")
            print(self.user.board)
            print("-"*21)
            print("Доска компьютера")
            print(self.ai.board)
            if num % 2 == 0:
                print("-"*21)
                print("Ходит пользователь")
                repeat = self.user.move()
            else:
                print("-"*21)
                print("Ходит компьютер")
                time.sleep(3)
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 21)
                print("Пользователь победил!")
                break
            if self.user.board.count == 7:
                print("-" * 21)
                print("Компьютер победил!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
