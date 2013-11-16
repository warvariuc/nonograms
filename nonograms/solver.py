__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"


PLACEHOLDER, FILLED, BLANK = ' @.'


class LineSolver():
    """
    """
    def __init__(self, line, numbers):
        """
        @param line: сканируемая линия
        @param numbers: числа линии
        """
        self.line = line

        self.layout_count = 0  # layout count
        self.layout_accumulator = [0] * len(line)

        # заполняем начальные позиции блоков
        # (выравненные влево, с одной пустой клеткой между ними)
        self.blocks = []
        block_start = -1
        for block_length in numbers:
            self.blocks.append((block_start, block_start + block_length))
            # одна пустая ячейка после предыдущего блока
            block_start += block_length + 1

    def accumulate(self):
        """Учесть в накопителе текущую ракладку блоков"""
        for block_start, block_end in self.blocks:
            for i in range(block_start, block_end):
                self.layout_accumulator[i] += 1
        self.layout_count += 1

    def result(self):
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

    def solve(self):
        # пытаемся сдвинуть первый блок на нулевую позицию -
        # есть ли хоть одна действительная раскладка?
        if self.push_block(0, 0) < 0:
            return ''.join(self.line)

        blocks = self.blocks
        # перебираем возможные раскладки
        while True:
            # учитываем возможную раскладку блоков в накопителе
            self.accumulate()
            # запоминаем текущую раскладку блоков, для возможности отката
            blocks_backup = blocks[:]
            # толкаем блоки один за другим с последнего по первый
            for first_block in reversed(range(len(blocks))):
                if self.push_block(first_block, first_block) > 0:
                    break  # еще есть раскладки - продолжим толкать
                # откат на последнюю валидную раскладку
                blocks[:] = blocks_backup[:]
            else:
                break  # прервать цикл while - больше нет возможных раскладок

        # анализируем результаты
        return self.result()

    def push_block(self, first_block_no, block_no):
        """Сдвинуть указанный блок вправо на следующую действительную позицию
        возвращает номер позвиции, если получилось сдвинуть,
        -1 - если нет следующей действительной позиции для блока.
        self.blocks при этом изменяется.
        """
        blocks = self.blocks
        line = self.line
        block_start, block_end = blocks[block_no]

        while True:

            # сдвигаем блок на одну позицию
            block_start += 1
            block_end += 1

            if block_end > len(line):
                # недействительная позиция - блок вышел за границы строки
                return -1

            if block_no + 1 < len(self.blocks):
                # есть следующий блок
                next_block_start = self.blocks[block_no + 1][0]  # начало следующего блока
                if block_end >= next_block_start:
                    # текущий блок уперся (пересекается) со следующим
                    # попытаемся сдвинуть следующий
                    next_block_start = self.push_block(first_block_no, block_no + 1)
                    if next_block_start < 0:
                        # не удалось успешно сдвинуть следующий блок
                        return -1
            else:
                # это последний блок
                next_block_start = len(self.line)

            if block_start > 0 and line[block_start - 1] == FILLED:
                # недействительная позиция - клетка перед началом блока закрашена
                if block_no == first_block_no:
                    # нельзя оставлять закрашенные клетки за первым толкаемым блоком
                    return -1
                continue

            if BLANK in line[block_start:block_end]:
                # недействительная позиция - блок попадает на пустую клетку
                continue

            if FILLED in line[block_end:next_block_start]:
                # недействительная позиция - между текущим и следующим блоком
                # есть закрашенная клетка
                continue

            # найдена подходящяя раскладка блоков
            blocks[block_no] = (block_start, block_end)  # новая позиция сдвинутого блока
            return block_start


def solve_line(line, numbers):
    return LineSolver(line, numbers).solve()
