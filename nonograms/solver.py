__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"


PLACEHOLDER, FILLED, BLANK = ' @.'


class _LineSolver():
    """
    """
    def __init__(self, line, numbers):
        """
        @param line: сканируемая линия
        @param numbers: числа линии
        """
        assert isinstance(line, str)
        self.line = line
        # инициализация накопителя
        self.layout_count = 0
        self.layout_accumulator = [0] * len(line)

        # заполняем начальные позиции блоков
        # (выравненные влево, с одной пустой клеткой между ними)
        self.blocks = []
        block_start = -1
        for block_length in numbers:
            self.blocks.append((block_start, block_start + block_length))
            # одна пустая ячейка после предыдущего блока
            block_start += block_length + 1

        self.pushed_block_no = 0

    def solve(self):

        # пытаемся сдвинуть первый блок на нулевую позицию -
        # есть ли хоть одна действительная раскладка?
        if not self.push_block(self.pushed_block_no):
            return self.line

        # перебираем возможные раскладки
        while True:
            # учитываем возможную раскладку блоков в накопителе
            self.accumulate_layout()
            # запоминаем текущую раскладку блоков, для возможности отката
            blocks = self.blocks[:]
            # толкаем блоки один за другим с последнего по первый
            for self.pushed_block_no in reversed(range(len(blocks))):
                if self.push_block(self.pushed_block_no):
                    break  # еще есть раскладки - продолжим толкать
                # откат на последнюю валидную раскладку
                self.blocks = blocks[:]
            else:
                break  # прервать цикл while - больше нет возможных раскладок

        # анализируем результаты

        if not self.layout_count:
            # не было не одной возможной раскладки - все стираем
            return PLACEHOLDER * len(self.line)

        line = list(self.line)
        for i, (count, state) in enumerate(zip(self.layout_accumulator, line)):
            if count == 0:
                # ни в одной возможной раскладке ни один блок сюда не попадал - здесь чисто
                state = BLANK
            elif count == self.layout_count:
                # во всех возможных раскладках сюда попадал блок - здесь закрашено
                state = FILLED
            else:
                # точно не известно - не решено
                continue
            line[i] = state

        return ''.join(line)

    def push_block(self, block_no):
        """Сдвинуть указанный блок вправо на следующую действительную позицию
        возвращает True если получилось сдвинуть,
        False - если нет следующей действительной позиции для текущего блока.
        self.blocks при этом изменяется.
        """
        block_start, block_end = self.blocks[block_no]

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

            if block_no < len(self.blocks) - 1:
                # начало следующего блока
                next_block_start = self.blocks[block_no + 1][0]
            else:
                # последний фиктивный блок, к-й нельзя сдвинуть
                next_block_start = len(self.line) + 2

            # текущий блок уперся (пересекается) со следующим - попытаемся его сдвинуть
            if block_end >= next_block_start:
                # текущий блок уперся (пересекается) со следующим - попытаемся его сдвинуть
                if block_no + 1 >= len(self.blocks):
                    # это последний блок
                    return False

                if not self.push_block(block_no + 1):
                    # не удалось успешно сдвинуть следующий блок
                    return False

                if block_no < len(self.blocks) - 1:
                    # начало следующего блока
                    next_block_start = self.blocks[block_no + 1][0]
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
                # недействительная позиция - между текущим и следующим блоком
                # есть уже закрашенная клетка
                continue

            # найдена подходящяя раскладка блоков
            self.blocks[block_no] = (block_start, block_end)  # новая позиция сдвигаемого блока
            return True

    def accumulate_layout(self):
        """учесть в накопителе текущую ракладку блоков"""
        for block_start, block_end in self.blocks:
            for i in range(block_start, block_end):
                self.layout_accumulator[i] += 1
        self.layout_count += 1


def solve_line(line, numbers):
    return _LineSolver(line, numbers).solve()
