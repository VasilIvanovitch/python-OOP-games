from random import *
#  v 1.5.2
class ShipDefender:
    '''менеджер контекстов для защиты объекта Ship при неудачном изменении его координат'''
    def __init__(self, ship):
        self._ship = ship
        self._x_copy , self._y_copy = ship.get_start_coords()
        
    def __enter__(self):
        return self._ship

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self._ship.set_start_coords(self._x_copy , self._y_copy)            
            return True

class Ship:
    '''x, y - координаты начала расположения корабля (целые числа)
    length - длина корабля (число палуб: целое значение: 1, 2, 3 или 4)
    tp - ориентация корабля (1 - горизонтальная; 2 - вертикальная)
    '''
    def __init__(self, length, tp=1, x=None, y=None):  #  (length, tp, x, y)
        if not (0 < length <= 4) or not 1 <= tp <= 2:
            raise ValueError("Таких кораблей не существует")
        self._length = length
        self._tp = tp   
        self._x = x
        self._y = y
        self._is_move = True
        self._cells = [1] * length   # 1- попадания не было, а если стоит значение 2, то произошло попадание
  

    def set_start_coords(self, x, y, size=14):
        '''установка начальных координат (запись значений в локальные атрибуты _x, _y), значение по умолчанию
        size=14 ограничивает максимальный размер поля, при использовании class ShipDefender'''
        #print(f'set_start_coords - {size}')
        if x != None and y != None:
            self._x = x
            self._y = y
            if self.is_out_pole(size):
                self._x = None
                self._y = None
                raise ValueError("Корабль вышел за игровое поле")

    def get_start_coords(self):
        return self._x, self._y

    def is_collide(self, ship):
        '''проверка на столкновение с другим кораблем ship, метод возвращает True, если столкновение есть'''
        return not set(self.ship_area).isdisjoint(set(ship.ship_hull))
    
    def move(self, go, size=10):
        '''перемещение корабля в направлении его ориентации на go клеток; движение возможно только если флаг _is_move = True'''
        if self._is_move:
            if self._tp == 1:
                ship = self 
                with ShipDefender(ship) as ship:
                    x, y = ship.get_start_coords()
                    ship.set_start_coords(x+go, y, size)
                    
            if self._tp == 2:
                ship = self 
                with ShipDefender(ship) as ship:
                    x, y = ship.get_start_coords()
                    ship.set_start_coords(x, y+go, size)
                    
    
    @property
    def ship_area(self):
        '''область в которой не должно быть других кораблей вокруг текущего корабля'''
        j, i = self.get_start_coords()
        if self._tp == 1:
            return tuple((x, y) for x in range(i - 1, i+2) if 0 <= x for y in range ( j-1, j+self._length+1) if 0 <= y)
        if self._tp == 2:
            return tuple((x, y) for x in range(i - 1, i+self._length+1) if 0 <= x for y in range (j-1, j+2) if 0 <= y)
	
    @property
    def ship_hull(self):
        '''текущие координаты всего корабля на поле, вложенный кортеж вида (i(y), j(x) для каждой "палубы")'''
        j, i = self.get_start_coords()
        if self._tp == 1: return tuple((x, y) for x in range(i, i+1) if 0 <= x for y in range ( j, j+self._length) if 0 <= y)
        if self._tp == 2: return tuple((x, y) for x in range(i, i+self._length) if 0 <= x for y in range (j, j+1) if 0 <= y)

    @property 
    def ship_condition(self):
        '''Формирует словарь - ключ: кортеж с координатами палуб, значение - состояние палуб (1 или 2)'''
        return dict(zip(self.ship_hull, self._cells))

    def is_out_pole(self, size=10):
        '''проверка на выход корабля за пределы игрового поля (size - размер игрового поля, обычно, size = 10)
        возвращается булево значение True, если корабль вышел из игрового поля и False - в противном случае
		'''
        x, y = self.get_start_coords()
        if self._tp ==1:
            return not (0 <= x <= size - self._length) or (not 0 <= y < size)
        if self._tp ==2:
            return (not 0 <= x < size) or (not 0 <= y <= size - self._length) 
  
    def __getitem__(self, item):
        '''считывание значения из _cells по индексу indx (индекс отсчитывается от 0)'''
        if 0 <= item < self._length:
            return self._cells[item]
    
    def __setitem__(self, key, value):
        '''запись нового значения в коллекцию _cells'''
        if 0 <= key < self._length and value in (1, 2):
            self._cells[key] = value
            if value == 2: self._is_move = False

class GamePole:
    def __init__(self, size):
        self._size = size
        self._ships = []

    def init(self):
        '''начальная инициализация игрового поля'''
        ships_list = (4, 3, 3, 2, 2, 2, 1, 1, 1, 1)
        self._ships = list(Ship(n, tp=randint(1, 2)) for n in ships_list)
        self.ship_positioning()
    
    def get_ships(self):
        '''возвращает коллекцию _ships'''
        return self._ships

    def get_pole(self):
        '''получение текущего игрового поля в виде двумерного (вложенного) кортежа размерами size x size'''
        pole = [[0 for j in range(self._size)] for i in range(self._size)]
        for ship in self.get_ships():
            for n, a in enumerate(ship.ship_hull):
                #print(f"n= {n}, a= {a}")
                i, j = a
                pole[i][j] = ship._cells[n]
        for i in range(self._size):
            pole[i] = tuple(pole[i])
        return tuple(pole)
    def show(self):
        '''отображение игрового поля в консоли 
        (корабли должны отображаться значениями из коллекции _cells каждого корабля, вода - значением 0)'''
        pole = self.get_pole()
        for i in range(self._size):
            for j in range(self._size):
                print(pole[i][j], end=' ')
            print()
            
    def move_ships(self):
        '''пробуем двигать корабли'''
        for obj in self.get_ships():
            go = (-1, 1)[randint(0,1)]
            a = obj.get_start_coords()
            obj.move(go, self._size)
            if a != obj.get_start_coords():
                for n in self.get_ships():
                    if n != obj:
                        if obj.is_collide(n):
                            x, y = a 
                            obj.set_start_coords(x, y, self._size) 
                            break 
                if a == obj.get_start_coords():
                    obj.move(-go, self._size)
                    if a != obj.get_start_coords():
                        for n in self.get_ships():
                            if n != obj:
                                if obj.is_collide(n):
                                    x, y = a 
                                    obj.set_start_coords(x, y, self._size)
                                    break                   
                    

    def ship_positioning(self):
        '''метод для расстановки кораблей '''
        for n in range(len(self.get_ships())):
            count = 0
            while count<200:
                count += 1
                try:
                    self._ships[n].set_start_coords(randint(0, self._size - 1), randint(0, self._size - 1), self._size)
                    for ship in self._ships[:n]:
                        if self._ships[n].is_collide(ship):
                            raise ValueError("недопустимое сближение короблей ")                                       
                except ValueError as a:                 
                    continue                    
                else:                   
                    break
            if count > 199: raise ValueError("Корабли не удалось расставить, попробуйте еще раз, или увеличте размеры поля")

class SeaBattle:
    '''управление игровым процессом в целом'''
    _symbol_human = ['~', '□', 'X', '*']
    _symbol_comp = ['~', '~', 'X', '*']
    def __init__(self, size=10, move_ships = False):
        """Инициализируем рандомные игровые поля для человека и ИИ(ПК)"""
        self._move_ships = move_ships  # флаг разрешения двигать корабли, если True. По умолчанию False
        self._size = size
        self._human_p = GamePole(self._size)
        self._human_p.init()
        self._comp_p = GamePole(self._size)
        self._comp_p.init()
        self._pole_comp = self.pole_comp() # таблица для обстрела ячеек ИИ
        self._pole_comp_special = self._pole_comp[:]  # вспомогательная таблица для обстрела вокруг поврежденных палуб компом      
        self._shot_hum = []  # база залпов человека
        self._shot_comp = [] # база залпов компа
        self._ships_conditions_hum = self.ships_conditions(self._human_p)  # состояние кораблей человека
        self._ships_conditions_comp = self.ships_conditions(self._comp_p) # состояние кораблей компа
        self._ship_domaged = []          # повреждения корабля
        self._game_over = 0  # 0 ( False) - игра идет, 1 - выйграл человек, 2 -выйграл ПК
       
    def pole_comp(self):
        '''генерирует область для обстрела ПК'''
        return [(i, j) for j in range(self._size) for i in range(self._size)]
    def re_pole_comp(self):
        '''повторно генерирует область для обстрела ПК, исключая 
        "мертвые зоны" вокруг потопленных кораблей'''
        self._pole_comp = self.pole_comp()
        for ship in self._human_p._ships:
            if sum(ship._cells) == len(ship._cells) * 2: self.dead_zone(ship)
    
    def show(self):
        """отображение игрового поля, слева  ваше поле, справа ПК
        Если использовании варианта 2 появляется возможность отслеживать движение
        корабля противника. Обозначение "*" меняется на '~' на траектории прохода коробля. 
        дизайн отображения игрового поля "by П.Сарафанников"
        """
        s = ' '.join(str(i) for i in range(self._size))
        l = 10
        if self._size > 9: l = 11 
        print()
        print('Ваше поле:'," "*self._size*2, 'Поле ИИ:')              
        print(s + " "*l + s)
        for i in range(self._size):
            for j in range(self._size):
                cell = (i, j)                
                a = self._ships_conditions_hum.get(cell, 0)
                #if cell in self._shot_comp and cell not in self._ships_conditions_hum: a = 3 # Вариат 2
                if cell in self._shot_comp and self._ships_conditions_hum.get(cell, 0) == 0: a = 3
                if j > 8: print(self._symbol_human[a], end='  ')
                else: print(self._symbol_human[a], end=' ')
            print('  ', str(i).ljust(2), '   ', end='')
            for j in range(self._size):
                cell = (i, j)
                a = self._ships_conditions_comp.get(cell, 0)
                #if cell in self._shot_hum and (cell not in self._ships_conditions_comp): # Вариат 2
                if cell in self._shot_hum and self._ships_conditions_comp.get(cell, 0) != 2:
                    a = 3 
                if j > 8: print(self._symbol_comp[a], end='  ')
                else: print(self._symbol_comp[a], end=' ')
            print()
        print()
        self.info_game_over()

    def ships_conditions(self, game_pole):
        '''возвращает сводный словарь состояния кораблей'''
        res = {}
        for ship in game_pole.get_ships():
            res.update(ship.ship_condition)
        return res
    
    def game_over(self, ships_conditions):
        '''проверяет состояние кораблей и возвращает True если все корабли уничтожены'''
        return sum(ships_conditions.values()) >= 40      
        
    
    def human_shot(self):
        """Ход человека"""
        a = self.input_coords()
        i, j = a
        self._shot_hum.append(a)
        if a not in self._ships_conditions_comp:            
            print(f'Вы: {i}, {j}: Мимо', end='\n')
        else:
            for ship in self._comp_p._ships:
                if a in ship.ship_hull:
                    indx = ship.ship_hull.index(a)
                    ship[indx] = 2           # вспомнил про про __setitem__
                    if sum(ship._cells) < len(ship._cells) * 2:

                        print(f'Вы: {i}, {j}: Ранен', end='\n')
                        self._ships_conditions_comp[a] = 2
                    else:
                        print(f'Вы: {i}, {j}: Потоплен', end='\n')
                        self._ships_conditions_comp[a] = 2                        
                        self.dead_zone_2(ship)
                        if self.game_over(self._ships_conditions_comp):
                            self._game_over = 1
                    if not self.end: self.human_shot()
        if self._move_ships: self._comp_p.move_ships()
        self._ships_conditions_comp = self.ships_conditions(self._comp_p)                            

    def input_coords(self):
        '''При размере поля не более 10 координаты можно вводить без пробела'''
        try:
            a = input(f'Введите координаты клетки для выстрела i(y), j(x): i j или ij: ')
            if len(a) >= 3: i, j = map(int, a.split())
            else: i, j = int(a[0]), int(a[1])    
        except:
            print('Неправильные координаты, попробуйте снова')
            i, j = self.input_coords()
        if type(i) is not int or not (0 <= i <= self._size-1) or type(j) is not int or not (0 <= j <= self._size-1):
            print('Неправильные координаты, попробуйте снова')
            i, j = self.input_coords()
        return i, j

    def comp_shot(self):
        """Ход ИИ"""
        if len(self._ship_domaged) == 1: a = self.ship_domaged_1()
        elif len(self._ship_domaged) > 1: a = self.ship_domaged_2()
        else:
            if len(self._pole_comp) <= 1:
                self.re_pole_comp()
            a = choice(self._pole_comp)    
        i, j = a
        self._shot_comp.append(a)
        if a in self._pole_comp:
            self._pole_comp.remove(a)
        if a not in self._ships_conditions_hum:            
            print(f'ИИ: {i}, {j}: Мимо', end='\n')    
        else:
            for ship in self._human_p._ships:
                if a in ship.ship_hull:
                    if a in self._pole_comp_special: self._pole_comp_special.remove(a)
                    indx = ship.ship_hull.index(a)
                    ship[indx] = 2  # ship._cells[indx] = 2
                    if sum(ship._cells) < len(ship._cells) * 2:
                        print(f'ИИ: {i}, {j}: Ранен', end='\n')
                        self._ships_conditions_hum[a] = 2 
                        self._ship_domaged.append(a)
                        self._ship_domaged.sort()
                        
                    else:
                        print(f'ИИ: {i}, {j}: Потоплен', end='\n')
                        self._ships_conditions_hum[a] = 2
                        self._ship_domaged =[]
                        #print(self.game_over(self._ships_conditions_hum)                                               
                        self.dead_zone(ship)
                        if self.game_over(self._ships_conditions_hum):
                            self._game_over = 2
                    if not self.end: self.comp_shot()
        if self._move_ships: self._human_p.move_ships()
        self._ships_conditions_hum = self.ships_conditions(self._human_p)
        
    def ship_domaged_1(self):
        '''формирует методику обстрела поврежденного корабля (одна палуба)'''
        pole_comp = self._pole_comp
        if self._move_ships: pole_comp = self._pole_comp_special
        shot = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        if len(self._ship_domaged) == 1:
            a = 0
            while a not in pole_comp:
                i, j = self._ship_domaged[0]
                i_a, j_a = shot[randint(0, 3)]
                a = (i + i_a, j + j_a)
            if a in pole_comp: pole_comp.remove(a)
            return a
    
    def ship_domaged_2(self):
        '''формирует методику обстрела поврежденного корабля (две и более палуб)'''
        pole_comp = self._pole_comp
        if self._move_ships: pole_comp = self._pole_comp_special
        if len(self._ship_domaged) > 1:
            i, j =  self._ship_domaged[0]
            i1, j1 = self._ship_domaged[1]
            i_a, j_a = i1 - i, j1 - j
            a = (i - i_a, j - j_a)
            if a not in pole_comp:
                i, j =  self._ship_domaged[-1]
                a = (i + i_a, j + j_a)
            if a in pole_comp: pole_comp.remove(a)
            return a     
    
    def dead_zone(self, ship):
        '''формирует зону вокруг потопленных кораблей, которую не имеет смысла обстреливать для ПК'''       
        for n in ship.ship_area:
            if n in self._pole_comp: self._pole_comp.remove(n)
            #if n not in self._shot_comp: self._shot_comp.append(n)  

    def dead_zone_2(self, ship):
        '''формирует зону вокруг потопленных кораблей, которую не имеет смысла обстреливать для игрока'''
        for n in ship.ship_area:
            #if n in self._pole_comp: self._pole_comp.remove(n)
            if n not in self._shot_hum: self._shot_hum.append(n)  

    def info_game_over(self):
        if self._game_over == 2: print('''Игра окончена!
            Ничего страшного, в следующий раз получится, поработайте над точностью залпов''')
        if self._game_over == 1: print('''Игра окончена!
            Поздравляю, Вы победили!''')
     

    @property    
    def end(self):
        '''возвращает True если игра закончена'''
        return self._game_over > 0
   
def input_param():
    while True:
        try:
            size = input("Введите размер игрового поля (от 8 до 14): ")
            if not size.isdigit() or not 8 <= int(size) <= 14:
                raise ValueError("Неверный размер игрового поля")
            move_ships = input('''Хотите, что бы корабли двигались после каждого промоха противника?
Если да введите: Y/y, если нет нажмите любую клавишу- ''')
            if move_ships.lower() == 'y': move_ships = True
            else: move_ships = False
        except ValueError as s:
            print(s)
            continue
        else:
            #break
            return int(size), move_ships

def battle(size=10, move_ships=True):
    """Можно указать размер поля и опцию движения кораблей (move_ships) во время боя
    по умолчанию размер size = 10, move_ships = False
    """
    size, move_ships = input_param()
    game = SeaBattle(size, move_ships) # game = SeaBattle(size, move_ships = False)
    game.show()
    while not game.end:
        game.human_shot()
        if not game.end:
            game.comp_shot()
        game.show()
                 
if __name__ == '__main__':
    battle()
    pass
