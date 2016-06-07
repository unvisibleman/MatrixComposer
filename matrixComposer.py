#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import numpy as np

def clearMatrix():
	forDel = set()
	for i in xrange(n, len(b)):
		for j in xrange(n, len(b)):
			if i!=j and b[i] == b[j]:
#				print list(np.nonzero(b[i])[0]), list(np.nonzero(c[j])[0]), list(np.nonzero(c[i])[0])
				if subSet(c[j], c[i]): # если c_j в c_i, то с_i - избыточен
					forDel.add(i)
#					print "-"
	for i in sorted(forDel, reverse = True):
		del c[i], b[i]
	del forDel

def subSet(one, two):
	oneSet = set( list(np.nonzero(one)[0]) )
	twoSet = set( list(np.nonzero(two)[0]) )
	if oneSet<=twoSet: # если one подмножество two
		return True
	else:
		return False

# включает ли в себя способ newMethod представления инструкции instrPresentation какой-либо из имеющихся способов для этой инструкции
def alreadyNotPresented(instrPresentation, newMethod):
	it = 0
	for i in list(np.nonzero(b)[1]):
		if i == instrPresentation: # для способа, который представляет выбранную инструкцию
			if subSet(c[it], newMethod): # если имеющийся способ подмножество нового
				return False # то вернуть ложь (и не добавлять этот способ в матрицу)
		it+=1
	return True # вернуть истину (и добавить в таблицу)

# функция gen добавляет значения в список coef для развертывания инструкций
def gen(x, length):
	try:
		arr = np.array([list(np.binary_repr(x, length))], dtype=int)
#		print arr
	except MemoryError:
		sys.exit("Слишком много комбинаций при разложении:"+str(2**x))
	temp = list(np.nonzero(arr)[1])
	return temp

# 1. Пытаемся открыть входной файл и считать основную информацию
if len(sys.argv) == 1:
	sys.exit("Не указано имя входного файла.")
inputFile = sys.argv[1]
outputFile = inputFile.replace("table", "LPX")
if inputFile == outputFile:
	sys.exit("Входной файл имеет расширение, отличное от .table")
try:
	givenMethods = [line.rstrip('\n') for line in open(inputFile)]
except IOError:
	sys.exit("Ошибка открытия файла")
IS = givenMethods[0].split(' ') # сохраним набор инструкций в отдельный массив
del givenMethods[0] # и удалим его из рабочего
n = len(IS) # количество инструкций
k = len(givenMethods)  # количество способов
m = n+k # количество строк в матрицах

# 2. Создаем и заполняем матрицы C и B по входному файлу
c= [[(1 if i == j else 0) for j in xrange(0, n)] for i in xrange(0, m)]
b= [[(1 if i == j else 0) for j in xrange(0, n)] for i in xrange(0, m)]
i = n # номер строки матриц, с которой начинаются методы
for met in givenMethods:
	method = met.split(' ')
	if len(method) <= 1: # строка длиной в один символ, требуем следующую
		continue
	method[0] = method[0][:-1] # удаляем последний символ из 1-ого слова
	try:
		b[i][IS.index(method[0])] = 1 # текущий метод представляет инструкцию, найденную по индексу
	except ValueError:
		sys.exit("Неверная инструкция "+repr(method[0])+" в способе "+repr(met))
	del method[0] # удаляем из вектора первый элемент - остаются только названия инструкций, которые используются в методе
	for p in method:
		# если строка нулевого размера, то пропускаем
		if len(p) == 0:
			continue
		# если строка начинается с пробела, то перебор аргументом завершить, иначе ... 
		if p[0] == "#":
			break
		else:
			try:
				c[i][IS.index(p)] = 1 # ставим единицы для используемых инструкций
			except ValueError:
				sys.exit("Неверная инструкция "+repr(p)+" в способе "+repr(met))
	i+=1

# 3. Развертка всех способов представления
flag = True
while flag:
	
	b[n:len(b)], c[n:len(c)] = (list(t) for t in zip(*sorted(zip(b[n:len(b)], c[n:len(c)]))))
	
	totalAdded = 0 # суммарное количество добавленных инструкций на итерации
	# для каждого способа представления в матрицах
	for i in xrange(n, len(b)):
		# массив номеров инструкций
		instructionUsed = np.empty((0, n), bool)
		# массив способов
		methods = np.empty((0, n), bool)
		# количество инструкций, для которых также нашлись способы
		numberOfUsedInstructions = 0;
		# 1. определяем какую инструкцию представляет текущий способ
		for instrPresentation in xrange(0, n):
			if b[i][instrPresentation] == 1:
				break;
		# 2. Определяем какие инструкции участвуют в текущем способе
		for instrAtPresentation in xrange(0, n):
			if c[i][instrAtPresentation] == 1:
				# 3. Определяем какие есть способы представить каждую инструкцию из текущего способа 
				for looking4presentation in xrange(n, len(b)):
					if b[looking4presentation][instrAtPresentation] == 1 and c[looking4presentation][instrPresentation] != 1:
						numberOfUsedInstructions += 1
						methods = np.vstack([methods, c[looking4presentation]])
						instructionUsed = np.vstack([instructionUsed, np.logical_not(b[looking4presentation])])
		if len(methods) != 0: # если таковые инструкции нашлись
			actuallyAdded = 0 # количество действительно добавленных инструкций
			lines2write = numberOfUsedInstructions*(numberOfUsedInstructions-1)+1
			for j in xrange(1, lines2write+1):
				coef = []
#				print j, numberOfUsedInstructions
				coef = gen(j, numberOfUsedInstructions)
				newPart = [0]*n # массив перед операцией OR должен быть инициализирован кол-вом нулей, раным кол-ву инструкций
				iUsed = [True]*n
				for k in xrange(0, len(coef)):
					newPart = np.logical_or(methods[coef[k]], newPart) # новые методы
					iUsed = np.logical_and(iUsed, instructionUsed[coef[k]]) # исключение старых
				methodBasis = np.logical_and(c[i], iUsed) # основание для нового способа
				newMethod = np.logical_or(methodBasis, newPart) # окончательная его генерация
#				print methodBasis, newMethod
				# если полученный способ не подмножество имеющихся, то
				if alreadyNotPresented(instrPresentation, newMethod) :
					c.append(list(newMethod.astype(int))) #добавляем новый способ в матрицу С
					b.append(b[i]) # а в м-цу B вектор, описывающий какую инструкцию, мы раскладывали
					actuallyAdded += 1
				del coef
			if actuallyAdded>0:
				print "Инструкция",IS[instrPresentation], "развернута, добавлено", actuallyAdded, "способ(а), перебрано",lines2write
				totalAdded += actuallyAdded # учтем кол-во добавленных инструкций
			else:
				print "Инструкция", IS[instrPresentation], "рассмотрена, перебрано ", lines2write
	
	clearMatrix()

	print "Итерация принесла",totalAdded,"кобинаций. После удаления избыточных способов матрицы содержат",len(c),"строк"
	
	if totalAdded == 0: # если ни одной инструкции за итерацию
		flag = False
	
	

print "Всего инструкций: n=", n, ", способов представления (в т.ч. и полученных в результате развертывания): K=", len(b)-n
print "Количество строк матриц: n*(K+1)=", len(b)

# 4. Вывод матриц в файлы
c_table = open(inputFile.replace(".table", "_c.table"), 'w')
b_table = open(inputFile.replace(".table", "_b.table"), 'w')
c_table.write(
	'\n'.join(
		[''.join(['{:2}'.format(item) for item in row]) for row in c]
	)
)
b_table.write(
	'\n'.join(
		[''.join(['{:2}'.format(item) for item in row]) for row in b]
	)
)

bc_table = open(inputFile.replace(".table", "_bc.table"), 'w')
for i in xrange(0, len(c)):
	for j in xrange(0, n):
		if b[i][j] == 1:
			bc_table.write(" *")
		else:
			bc_table.write('{:2}'.format(c[i][j]))
	bc_table.write('\n')

# 5. Вывод в файл задачи ЛП
plx_file = open(outputFile, 'w')
plx_file.write("min: ")
for i in xrange(1, n):
	plx_file.write("X"+str(i)+"+")
plx_file.write("X"+str(n)+";\n")
# первый набор ограничений V
Vindex = 1
for i in xrange(0, n):
	for j in xrange(0, len(b)): # 0..m
		if c[j][i] == 1: # there was b-matrix
			plx_file.write("v"+str(Vindex)+": X"+str(i+1)+"-Y"+str(j+1)+">=0;\n")
			Vindex += 1
# второй набор ограничений W
Windex = 1
for i in xrange(0, n):
	limitation = ""
	for j in xrange(0, len(b)): # 0...m
		if b[j][i] == 1:
			limitation += "Y"+str(j+1)+"+"
	if limitation != "":
		# удалить лишний плюс с конца строки
		limitation = limitation[:-1]
		plx_file.write("w"+str(Windex)+": "+limitation+">=1;\n") 
	# рассмотрим следующее ограничение
	Windex += 1
# ограничения на тип: целое число
plx_file.write("int ")
for i in xrange(1, n):
	plx_file.write("X"+str(i)+", ")
plx_file.write("X"+str(n)+";\n")
