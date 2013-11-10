__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

import copy


PLACEHOLDER, FILLED, BLANK = ' @.'


class Block():
    """
    """
    def __init__(self, start, length):
        self.start = start
        self.length = length

    @property
    def end(self):
        return self.start + self.length


#class Blocks():
#    """Расположение блоков.
#    """
#    def __init__(self, numbers, line_length):
#        self._blocks = []  # [(block_start, block_length), (block_start, block_length),...]
#         # заполняем начальные позиции блоков
#         # (выравненные влево, с одной пустой клеткой между ними)
#        block_start = -1
#        for block_length in numbers:
#            self._blocks.append(Block(block_start, block_length))
#            block_start += block_length + 1
#        self._line_length = line_length
#
#    def __len__(self):
#        return len(self._blocks)
#
#    def start(self, block_no):
#        return self._blocks[block_no].start


class _LineSolver():
    """
    """
    def __init__(self, line, numbers):
        """line - сканируемая линия
        blockLengths - числа линии"""
        self.line = list(line)
        self.combinations = 0
        # инициализация накопителя
        self.accumulator = [0] * len(line)

         # заполняем начальные позиции блоков
         # (выравненные влево, с одной пустой клеткой между ними)
        self.blocks = []
        block = Block(-2, 0)
        for block_length in numbers:
            # одна пустая ячейка после предыдущего блока
            block = Block(block.end + 1, block_length)
            self.blocks.append(block)

        self.pushed_block_no = 0

    def solve(self):

        # пытаемся сдвинуть первый блок на нулевую позицию -
        # есть ли хоть одна действительная раскладка?
        if self.push_block(self.pushed_block_no):
            while True:
                # учитываем возможную раскладку блоков в накопителе
                self.accumulate()
                # запоминаем текущую раскладку блоков, для возможности отката
                blocks = copy.deepcopy(self.blocks)
                # толкаем блоки один за другим с последнего по первый
                for self.pushed_block_no in reversed(range(len(blocks))):
                    if self.push_block(self.pushed_block_no):
                        break  # еще есть раскладки - продолжим толкать
                    # откат на последнюю валидную раскладку
                    self.blocks = copy.deepcopy(blocks)
                else:
                    break  # прервать цикл while - больше нет возможных раскладок

            for i, (count, state) in enumerate(zip(self.accumulator, self.line)):
                if not self.combinations:
                    # не было не одной возможной раскладки - все стираем
                    state = PLACEHOLDER
                else:
                    if count == 0:
                        # ни в одной возможной раскладке ни один блок здесь не попадал - здесь чисто
                        state = BLANK
                    elif count == self.combinations:
                        # во всех возможных раскладках сюда попадал юлок - здесь закрашено
                        state = FILLED
                self.line[i] = state

        return ''.join(self.line)

    def push_block(self, block_no):
        """сдвинуть указанный блок вправо на следующую действительную позицию
        возвращает True если получилось сдвинуть,
        False - если нет следующей действительной позиции для текущего блока.
        """
        if block_no >= len(self.blocks):
            return False

        block = self.blocks[block_no]
        block_start = block.start  # начало толкаемого блока
        block_end = block.end  # конец толкаемого блока
        if block_no < len(self.blocks) - 1:
            # начало следующего блока
            next_block_start = self.blocks[block_no + 1].start
        else:
            # последний фиктивный блок, к-й нельзя сдвинуть
            next_block_start = len(self.line) + 2

        while True:
            block_start += 1
            block_end += 1

            if block_end > len(self.line):
                # недействительная позиция - блок вышел за границы строки
                return False

            if block_start > 0 and self.line[block_start - 1] == FILLED:
                # нельзя оставлять закрашенные клетки за первым толкаемым блоком
                if block_no == self.pushed_block_no:
                    return False

            # текущий блок уперся (пересекается) со следующим - попытаемся его сдвинуть
            if block_end >= next_block_start:
                if not self.push_block(block_no + 1):
                    # не удалось успешно сдвинуть следующий блок
                    return False
                if block_no < len(self.blocks) - 1:
                    # начало следующего блока
                    next_block_start = self.blocks[block_no + 1].start
                else:
                    # правая граница
                    next_block_start = len(self.line) + 2
            if block_start > 0 and self.line[block_start - 1] == FILLED:
                # невалидная позиция - клетка перед началом блока закрашена
                continue

            if BLANK in self.line[block_start:block_end]:
                # недействительная позиция - блок попадает на уже пустую клетку
                continue

            if FILLED in self.line[block_end:next_block_start]:
                # недействительная позиция - между текущим и следующим блоками
                # есть уже закрашенная клетка
                continue

            # найдена подходящяя раскладка блоков
            break

        block.start = block_start  # новая позиция сдвигаемого блока
        return True

    def accumulate(self):
        """учесть в накопителе текущую ракладку блоков"""
        for block in self.blocks:
            for i in range(block.start, block.end):
                self.accumulator[i] += 1
        self.combinations += 1


def solve_line(line, numbers):
    return _LineSolver(line, numbers).solve()
