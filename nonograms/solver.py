__author__ = "Victor Varvariuc <victor.varvariuc@gmail.com>"


PLACEHOLDER, FILLED, BLANK = ' @.'


class LayoutAccumulator():
    def __init__(self, line):
        self.line = line
        self.count = 0  # layout count
        self.accumulator = [0] * len(line)

    def accumulate(self, blocks):
        """Учесть в накопителе текущую ракладку блоков"""
        for block_start, block_end in blocks:
            for i in range(block_start, block_end):
                self.accumulator[i] += 1
        self.count += 1

    def result(self):
        # анализируем результаты
        if not self.count:
            # не было не одной возможной раскладки - все стираем
            return PLACEHOLDER * len(self.line)

        line = list(self.line)
        for i, (count, state) in enumerate(zip(self.accumulator, line)):
            if count == 0:
                # ни в одной возможной раскладке ни один блок сюда не попадал - здесь чисто
                state = BLANK
            elif count == self.count:
                # во всех возможных раскладках сюда попадал блок - здесь закрашено
                state = FILLED
            else:
                # точно не известно - не решено
                continue
            line[i] = state

        return ''.join(line)


def solve_line(line, numbers):
    """
    @param line: сканируемая линия
    @param numbers: числа линии
    """
    assert isinstance(line, str)

    # заполняем начальные позиции блоков
    # (выравненные влево, с одной пустой клеткой между ними)
    blocks = []
    block_start = -1
    for block_length in numbers:
        blocks.append((block_start, block_start + block_length))
        # одна пустая ячейка после предыдущего блока
        block_start += block_length + 1

    # пытаемся сдвинуть первый блок на нулевую позицию -
    # есть ли хоть одна действительная раскладка?
    if not push_block(line, blocks, 0, 0):
        return line

    layout_accumulator = LayoutAccumulator(line)

    # перебираем возможные раскладки
    while True:
        # учитываем возможную раскладку блоков в накопителе
        layout_accumulator.accumulate(blocks)
        # запоминаем текущую раскладку блоков, для возможности отката
        blocks_backup = blocks[:]
        # толкаем блоки один за другим с последнего по первый
        for first_block in reversed(range(len(blocks))):
            if push_block(line, blocks, first_block, first_block):
                break  # еще есть раскладки - продолжим толкать
            # откат на последнюю валидную раскладку
            blocks = blocks_backup[:]
        else:
            break  # прервать цикл while - больше нет возможных раскладок

    # анализируем результаты
    return layout_accumulator.result()


def push_block(line, blocks, first_block, block_no):
    """Сдвинуть указанный блок вправо на следующую действительную позицию
    возвращает True если получилось сдвинуть,
    False - если нет следующей действительной позиции для текущего блока.
    blocks при этом изменяется.
    """
    block_start, block_end = blocks[block_no]

    while True:

        block_start += 1
        block_end += 1

        if block_end > len(line):
            # недействительная позиция - блок вышел за границы строки
            return False

        if block_start > 0 and line[block_start - 1] == FILLED:
            # нельзя оставлять закрашенные клетки за первым толкаемым блоком
            if block_no == first_block:
                return False

        if block_no < len(blocks) - 1:
            # начало следующего блока
            next_block_start = blocks[block_no + 1][0]
        else:
            # последний фиктивный блок, к-й нельзя сдвинуть
            next_block_start = len(line) + 2

        # текущий блок уперся (пересекается) со следующим - попытаемся его сдвинуть
        if block_end >= next_block_start:
            # текущий блок уперся (пересекается) со следующим - попытаемся его сдвинуть
            if block_no + 1 >= len(blocks):
                # это последний блок
                return False

            if not push_block(line, blocks, first_block, block_no + 1):
                # не удалось успешно сдвинуть следующий блок
                return False

            if block_no < len(blocks) - 1:
                # начало следующего блока
                next_block_start = blocks[block_no + 1][0]
            else:
                # правая граница
                next_block_start = len(line) + 2

        if block_start > 0 and line[block_start - 1] == FILLED:
            # невалидная позиция - клетка перед началом блока закрашена
            continue

        if BLANK in line[block_start:block_end]:
            # недействительная позиция - блок попадает на уже пустую клетку
            continue

        if FILLED in line[block_end:next_block_start]:
            # недействительная позиция - между текущим и следующим блоком
            # есть уже закрашенная клетка
            continue

        # найдена подходящяя раскладка блоков
        blocks[block_no] = (block_start, block_end)  # новая позиция сдвигаемого блока
        return True
