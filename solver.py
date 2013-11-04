__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"

import copy

from board import FILLED, BLANK, PLACEHOLDER


class Block():
    """
    """
    def __init__(self, length, begin):
        self.length = length
        self.begin = begin

    @property
    def end(self):
        return self.begin + self.length


class Solver():
    """
    """
    def scanLine(self, line, blockLengths):
        """line - сканируемая линия
        blockLengths - числа линии"""
        self.line = list(line)
        self.combinations = 0
        # инициализация накопителя
        self.accumulator = [0] * len(line)

        self.blocks = []
        blockBegin = -1
        # заполняем начальные позиции блоков
        # (выравненные влево, с одной пустой клеткой между ними)
        for blockLen in blockLengths:
            self.blocks.append(Block(blockLen, blockBegin))
            blockBegin += blockLen + 1

        self.pushedBlockNo = 0
        # пытаемся сдвинуть первый блок на нулевую позицию -
        # есть ли хоть одна действительная раскладка?
        if self.pushBlock(self.pushedBlockNo):
            while True:
                # учитываем возможную раскладку блоков в накопителе
                self.accumulate()
                # запоминаем текущую раскладку блоков, для возможности отката
                tmp = copy.deepcopy(self.blocks)
                # пробегаемся по блокам с последнего по первый
                for self.pushedBlockNo in reversed(range(len(self.blocks))):
                    if self.pushBlock(self.pushedBlockNo):
                        break  # продолжить цикл while
                    # откат на последнюю валидную раскладку
                    self.blocks = copy.deepcopy(tmp)
                else:
                    break  # прервать цикл while

            for i, count in enumerate(self.accumulator):
                state = self.line[i]
                if not self.combinations:
                    state = PLACEHOLDER
                else:
                    if count == 0:
                        state = BLANK
                    if count == self.combinations:
                        state = FILLED
                self.line[i] = state

        return ''.join(self.line)

    def pushBlock(self, blockNo):
        """сдвинуть указанный блок вправо на следующую действительную позицию
        возвращает True если получилось сдвинуть,
        False - если нет следующей действительной позиции для текущего блока.
        """
        if blockNo >= len(self.blocks):
            return False

        block = self.blocks[blockNo]
        blockBegin = block.begin  # начало толкаемого блока
        blockEnd = block.end  # конец толкаемого блока
        if blockNo < len(self.blocks) - 1:
            # начало следующего блока
            nextBlockBegin = self.blocks[blockNo + 1].begin
        else:
            # последний фиктивный блок, к-й нельзя сдвинуть
            nextBlockBegin = len(self.line) + 2

        while True:
            blockBegin += 1
            blockEnd += 1

            if blockEnd > len(self.line):
                # недействительная позиция - блок вышел за границы строки
                return False

            if blockBegin > 0 and self.line[blockBegin - 1] == FILLED:
                # нельзя оставлять закрашенные клетки за первым толкаемым блоком
                if blockNo == self.pushedBlockNo:
                    return False

            # текущий блок уперся (пересекается) со следущим -
            # попытаемся его сдвинуть
            if blockEnd >= nextBlockBegin:
                if not self.pushBlock(blockNo + 1):
                    # не удалось успешно сдвинуть следующий блок
                    return False
                else:
                    if blockNo < len(self.blocks) - 1:
                        # начало следующего блока
                        nextBlockBegin = self.blocks[blockNo + 1].begin
                    else:
                        # последний фиктивный блок, к-й нельзя сдвинуть
                        nextBlockBegin = len(self.line) + 2
                # невалидная позиция  - клетка перед началом блока закрашена
            if blockBegin > 0 and self.line[blockBegin - 1] == FILLED:
                continue

            if BLANK in self.line[blockBegin:blockEnd]:
                # недействительная позиция - блок попадает на уже пустую клетку
                continue

            if FILLED in self.line[blockEnd:nextBlockBegin]:
                # недействительная позиция - между текущим и следующим блоками
                # есть уже закрашенная клетка
                continue

            break

        block.begin = blockBegin  # новая позиция сдвигаемого блока
        return True

    def accumulate(self):
        """учесть в накопителе текущую ракладку блоков"""
        for block in self.blocks:
            for i in range(block.begin, block.end):
                self.accumulator[i] += 1
        self.combinations += 1


if __name__ == '__main__':  # some tests
    solver = Solver()
    assert (solver.scanLine('                         ', [15]) ==
            '          #####          ')
    assert (solver.scanLine('###### #   ', [6, 1]) ==
            '######.#...')
    assert (solver.scanLine('#..............   ##.## #', [1, 4, 4]) ==
            '#...............####.####')
