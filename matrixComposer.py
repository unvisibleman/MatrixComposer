#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import numpy as np

# add добавляет в список x если его в списке нет
def add(i):
	if i == 1:
		return
	if isinstance(i, int):
		if [i] not in coef:
			coef.append([i])
			return
	if i not in coef:
		coef.append(i)
		return

# функция gen добавляет значения в список coef для развертывания инструкций
def gen(x):
	s = []
	for i in xrange(1, x):
		gen(i)
		add([i, x])
		s.append(i)
	
	add(x);
	s.append(x);
	add(s)

# 1. Пытаемся открыть входной файл и считать основную информацию
if len(sys.argv) == 1:
	sys.exit( "Не указано имя входного файла.")
inputFile = sys.argv[1]
outputFile = inputFile.replace("table", "LPX")
try:
	methods = [line.rstrip('\n') for line in open(inputFile)]
except IOError:
	sys.exit("Ошибка открытия файла")
IS = methods[0].split(' ') # сохраним набор инструкций в отдельный массив
del methods[0] # и удалим его из рабочего
n = len(IS) # количество инструкций
k = len(methods)  # количество способов
m = n+k # количество строк в матрицах

# 2. Создаем и заполняем матрицы C и B по входному файлу
c= [[(1 if i == j else 0) for j in xrange(0, n)] for i in xrange(0, m)]
b= [[(1 if i == j else 0) for j in xrange(0, n)] for i in xrange(0, m)]
i = n # номер строки матриц, с которой начинаются методы
for met in methods:
	method = met.split(' ')
	if len(method) <= 1: # строка длиной в один символ, требуем следующую
		break
	method[0] = method[0][:-1] # удаляем последний символ из 1-ого слова
	b[i][IS.index(method[0])] = 1 # текущий метод представляет инструкцию, найденную по индексу
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
				sys.exit("Ошибка входных данных! Использованная в строке "+met+" инструкция "+p+" не найдена в наборе")
	i+=1

# 3. Развертка всех способов представления
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
			# 3. Определяем какие есть способы представить каждую инструкцию из текущего способа (кроме как через себя)
			for looking4presentation in xrange(n, len(b)):
				if b[looking4presentation][instrAtPresentation] == 1:
					numberOfUsedInstructions += 1
					methods = np.vstack([methods, c[looking4presentation]])
					instructionUsed = np.vstack([instructionUsed, np.logical_not(b[looking4presentation])])
	if len(methods) != 0: # если таковые инструкции нашлись
		coef = []
		gen(numberOfUsedInstructions)
		if len(coef) == 0: # если результат нулевого размера, то количествво комбинаций принять 1
			coef = [[1]]
		lines2write = numberOfUsedInstructions*(numberOfUsedInstructions-1)+1
		print "Необходимо развернуть инструкцию",IS[instrPresentation], "и добавить", lines2write, "способ(а)."
		for j in xrange(0, lines2write):
			newPart = [0]*n # массив перед операцией OR должен быть инициализирован кол-вом нулей, раным кол-ву инструкций
			iUsed = [True]*n
			for k in xrange(0, len(coef[j])):
				newPart = np.logical_or(methods[coef[j][k]-1], newPart) # новые методы
				iUsed = np.logical_and(iUsed, instructionUsed[coef[j][k]-1]) # исключение старых
			methodBasis = np.logical_and(c[i], iUsed) # основание для нового способа
			newMethod = np.logical_or(methodBasis, newPart) # окончательная его генерация
			c.append(newMethod) #добавляем новый способ в матрицу С
			b.append(b[i]) # а в м-цу B вектор, описывающий какую инструкцию, мы раскладывали 
		del coef

print "Всего инструкций: n=", n, ", способов представления (в т.ч. и полученных в результате развертывания): K=", len(b)-n
print "Количество строк матриц: n*(K+1)=", len(b)

# 4. Условный вывод матриц в файлы
outMatrix = raw_input("Чтобы сохранить матрицы C и B в файлы введите \"да\" или \"yes\" ")
if (outMatrix == 'да') or (outMatrix == 'yes'):
	c_table = open('c.table', 'w')
	b_table = open('b.table', 'w')
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
