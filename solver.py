from board import BOX, SPACE, CELL
import copy

class Block(): 
    def __init__(self):
        self.length = 0
        self.begin = 0
    
    def end(self):
        return self.begin + self.length



class Solver():

    def scanLine(self, line, blockLengths):
        '''line - сканируемая линия
        blockLengths - числа линии'''
        #print(blockLengths)
        #print('"' + ''.join(line) + '"')
        self.line = list(line)
        self.combinations = 0
        self.accumulator = [0] * len(line) # инициализация накопителя
        
        self.blocks = []
        blockBegin = -1
        for blockLen in blockLengths: # заполняем начальные позиции блоков (выравненные влево, с одной пустой клеткой между ними)
            block = Block()
            block.length = blockLen
            block.begin = blockBegin
            blockBegin += blockLen + 1
            self.blocks.append(block)

        self.pushedBlockNo = 0
        if self.pushBlock(self.pushedBlockNo): # пытаемся сдвинуть первый блок на нулевую позицию - есть ли хоть одна действительная раскладка?
            while True:
                self.accumulate() # учитываем возможную раскладку (комбинацию) блоков в накопителе
                #print(self.accumulator)
                tmp = copy.deepcopy(self.blocks) # запоминаем текущую раскладку блоков, для возможности отката
                for self.pushedBlockNo in reversed(range(len(self.blocks))): # пробегаемся по блокам с последнего по первый
                    if self.pushBlock(self.pushedBlockNo):
                        break # продолжить цикл while
                    else:
                        self.blocks = copy.deepcopy(tmp) # откат на последнюю валидную раскладку
                else:
                    break # прервать цикл while



            for i, count in enumerate(self.accumulator):
                newState = self.line[i]
                if not self.combinations:
                    newState = CELL
                else:
                    if count == 0:
                        newState = SPACE
                    if count == self.combinations:
                        newState = BOX
                self.line[i] = newState

        #print('"' + ''.join(self.line) + '"')
        #print(self.accumulator, self.combinations)
            
        return ''.join(self.line)


    def pushBlock(self, blockNo): # сдвинуть указанный блок вправо на следующую действительную позицию
        '''возвращает True если получилось сдвинуть, 
        False - если нет следующей действительной позиции для текущего блока.'''
        
        if blockNo >= len(self.blocks):
            return False

        block = self.blocks[blockNo]
        blockBegin = block.begin # начало толкаемого блока
        blockEnd = block.end() # конец толкаемого блока
        if blockNo < len(self.blocks) - 1:
            nextBlockBegin = self.blocks[blockNo + 1].begin # начало следующего блока
        else:
            nextBlockBegin = len(self.line) + 2 # последний фиктивный блок, к-й нельзя сдвинуть

        while True:
            blockBegin += 1
            blockEnd += 1

            if blockEnd > len(self.line):
                return False # недействительная позиция - блок вышел за границы строки

            if blockBegin > 0 and self.line[blockBegin - 1] == BOX:
                if blockNo == self.pushedBlockNo: return False # нельзя оставлять закрашенные клетки за первым толкаемым блоком

            if blockEnd >= nextBlockBegin: # текущий блок уперся (пересекается) со следущим - попытаемся его сдвинуть
                if not self.pushBlock(blockNo + 1): 
                    return False # не удалось успешно сдвинуть следующий блок
                else: 
                    if blockNo < len(self.blocks) - 1:
                        nextBlockBegin = self.blocks[blockNo + 1].begin # начало следующего блока
                    else:
                        nextBlockBegin = len(self.line) + 2 # последний фиктивный блок, к-й нельзя сдвинуть
                    
            if blockBegin > 0 and self.line[blockBegin - 1] == BOX: # невалидная позиция  - клетка перед началом блока закрашена
                continue

            if SPACE in self.line[blockBegin:blockEnd]:
                continue # недействительная позиция - блок попадает на уже пустую клетку
            
            if BOX in self.line[blockEnd:nextBlockBegin]:
                continue # недействительная позиция - между текущим и следующим блоками есть уже закрашенная клетка
                
            break

        block.begin = blockBegin # новая позиция сдвигаемого блока
        return True

        
    def accumulate(self): # учесть в накопителе текущую ракладку блоков
        for block in self.blocks:
            for i in range(block.begin, block.end()):
                self.accumulator[i] += 1
        self.combinations += 1
            


if __name__ == '__main__': # some tests
    solver = Solver()
    #solver.scanLine('                         ', [15])
    #solver.scanLine('###### #   ', [6, 1])
    solver.scanLine('#..............   ##.## #', [1, 4, 4])
    line = '   .      '
    line = '      #   '


#class Solver(): # старый алгоритм - слишком медленный для большого количества цифр
#
    #def scanLine(self, line, blockLengths):
        #'''line - сканируемая линия
        #blockLengths - числа линии'''
        #self.line = line
        #self.combinations = 0
        #self.accumulator = [0] * len(line) # инициализация накопителя
        #
        #self.blocks = []
        #blockBegin = len(line) + 1
        #for blockLen in reversed(blockLengths): # заполняем крайние правые возможные позиции блоков
            #block = Block()
            #block.length = blockLen
            #blockBegin -= blockLen
            #block.rightMostPos = blockBegin
            #blockBegin -= 1
            #self.blocks.append(block)
        #self.blocks.reverse()
        #
        #self.moveBlock(0)
#
#
    #def moveBlock(self, blockNo):
        #'Двигать указанный блок в пределах от предыдущего блока до краней правой возможной позиции.' 
        #if blockNo >= len(self.blocks):
            #self.checkBlocks()
        #else:
            #if blockNo:
                #prevBlockEnd = self.blocks[blockNo - 1].end()
            #else:
                #prevBlockEnd = -1
            #block = self.blocks[blockNo]
            #for i in range(prevBlockEnd + 1, block.rightMostPos):
                #block.begin = i
                #self.moveBlock(blockNo + 1)
#
    #def checkBlocks(self):
        #'Проверить, если указанная раскладка блоков допустима в строке'
        #blocksLine = [BOX] * len(self.line)
        #for block in self.blocks:
            #for i in range(block.begin, block.end()):
                #blocksLine[i] = SPACE
        #for i in range(len(self.line)):
            #if blocksLine[i] == self.line[i]:
                #return
        ##print(''.join(blocksLine))
        #
        #for i in range(len(self.line)):
            #if blocksLine[i] == SPACE:
                #self.accumulator[i] += 1
        #self.combinations += 1
