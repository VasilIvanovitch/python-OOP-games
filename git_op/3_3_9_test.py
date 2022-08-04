from random import choice
class TicTacToe:
    FREE_CELL = 0      # свободная клетка
    HUMAN_X = 1        # крестик (игрок - человек)
    COMPUTER_O = 2     # нолик (игрок - компьютер)
    def __init__(self):
        self._n = 3
        self.init()

    @property
    def is_human_win(self):
        return self.__is_human_win            
    @property
    def is_computer_win(self):
        return self.__is_computer_win        
    @property
    def is_draw(self):
        return self.__is_draw
    
    def init(self):
        self.__is_human_win, self.__is_computer_win, self.__is_draw = False, False, False
        self.pole = tuple(tuple(Cell() for j in range(self._n)) for i in range(self._n))
        self.total_lst = [(i, j) for j in range(self._n) for i in range(self._n) if self.pole[i][j].value == self.FREE_CELL]
        self.dict_comp_go = {}
        			
    def show(self):
        print("- - - - - - - - -")
        for i in range(self._n):
            for j in range(self._n):
                if self.pole[i][j].value == self.FREE_CELL: print(f'|{i} {j}|', end=' ')            
                if self.pole[i][j].value == self.HUMAN_X: print('| X |', end=' ')
                if self.pole[i][j].value == self.COMPUTER_O: print('| 0 |', end=' ')

            print()
            print("- - - - - - - - -")
        
    def human_go(self):
    	while True:
    		key = tuple(int(n) for n in input('Ваш ход- ').split() if n.isdigit())
    		if len(key) != 2 or not (0 <= key[0] < self._n) or not (0 <= key[1] < self._n) or self[key[0], key[1]] != 0:
    			continue
    		self.__setitem__(key, self.HUMAN_X)
    		break
    def computer_go(self):
        '''добавлена логика "победного"" хода и защиты клетки от "победного" хода соперника'''         
        key_warning = 0
        if self.dict_comp_go: 
            for key, value in self.dict_comp_go.items():                
                if sum(value) == 0:  #  поиск 'выйгрышного' хода
                    key1 = [n for n in key if n in self.total_lst]
                    if key1: self.__setitem__(*key1, self.COMPUTER_O)
                    return
                if sum(value) == 2:  #  защита от поражения
                    key_warning = [n for n in key if n in self.total_lst]
        if key_warning: key = key_warning[0]             
        else: key = choice(self.total_lst)
        self.__setitem__(key, self.COMPUTER_O)
	
    def __bool__(self):
        '''возвращает True, если игра не окончена (никто не победил и есть свободные клетки) и False - в противном случае'''
        return not any((self.is_human_win, self.is_computer_win, self.is_draw))
        
    def check_win(self):
        '''Проверка таблицы поля на выйгрыш или ничью'''
        self.dict_comp_go = {}	# для сбора вариантов защитных или выйгрышных ходов компа
        self.total_lst = [(i, j) for j in range(self._n) for i in range(self._n) if self.pole[i][j].value == self.FREE_CELL]  #  список свободных клеток
        humax = tuple(True if self.pole[i][i].value == self.HUMAN_X else False for i in range(self._n) if self.pole[i][i].value != self.FREE_CELL)
        if len(humax) == 3:
            if self.check_vs(humax): return False
        if len(humax) == 2 and sum(humax) != 1: self.dict_comp_go[((0,0), (1,1), (2,2))] = humax 
        humax = tuple(True if self.pole[i][self._n-1-i].value == self.HUMAN_X else False for i in range(self._n) if self.pole[i][self._n-1-i].value != self.FREE_CELL)
        if len(humax) == 3:
            if self.check_vs(humax): return False            
        if len(humax) == 2 and sum(humax) != 1: self.dict_comp_go[((2,0), (1,1), (0,2))] = humax
        for i in range(self._n):
            humax = tuple(True if value == self.HUMAN_X else False for value in self[i, :] if value != self.FREE_CELL)
            if len(humax) == 3:
                if self.check_vs(humax): return False              
            if len(humax) == 2 and sum(humax) != 1: self.dict_comp_go[((i,0), (i,1), (i,2))] = humax
        for j in range(self._n):
            humax = tuple(True if value == self.HUMAN_X else False for value in self[:, j] if value != self.FREE_CELL)
            if len(humax) == 3:
                if self.check_vs(humax): return False 
            if len(humax) == 2 and sum(humax) != 1: self.dict_comp_go[((0,j), (1,j), (2,j))] = humax
        if len(self.total_lst) == 0:
            self.__is_human_win, self.__is_computer_win, self.__is_draw  =  False, False, True 
            return False
        return True
    def check_vs(self, humax):
        '''вспомогательная функция для check_win'''
        if all(humax):
            self.__is_human_win, self.__is_computer_win, self.__is_draw  = True, False, False
            return True
        if sum(humax) == 0:
            self.__is_human_win, self.__is_computer_win, self.__is_draw  =  False, True, False
            return True
        return False
    def check_index(self, indx):
        if not isinstance(indx, (slice, tuple)) or not all(0 <= n <= 2 for n in indx if type(n) == int):
            raise IndexError('некорректно указанные индексы')
    def __getitem__(self, item):
        self.check_index(item)
        if type(item[1]) == slice:
            return tuple(n.value for n in self.pole[item[0]][item[1]])
        if type(item[0]) == slice:
            lst = [self.pole[i][item[1]] for i in range(3)][item[0]]			
            return tuple(n.value for n in lst)
        return self.pole[item[0]][item[1]].value

    def __setitem__(self, key, value):
        self.check_index(key)
        cell = self.pole[key[0]][key[1]]
        if not cell:
            raise ValueError('клетка уже занята')
        if self:
            cell.value = value
            self.check_win()
        

class Cell:
    def __init__(self, value=0):
        self.value = value      #  value - значение поля: 1 - крестик; 2 - нолик (по умолчанию 0).

    def __bool__(self):    #возвращает True, если клетка свободна (value = 0) и False - в противном случае.
        return not self.value

game = TicTacToe()
game.init()
step_game = 0
while game:
    game.show()

    if step_game % 2 == 0:
        game.computer_go() #  game.human_go()
    else:
        game.human_go()    #  game.computer_go()

    step_game += 1


game.show()

if game.is_human_win:
    print("Поздравляем! Вы победили!")
elif game.is_computer_win:
    print("Все получится, со временем")
else:
    print("Ничья.")