# -*- coding: utf-8 -*-
import  os
import  re
from datetime import datetime

exfiles = []
weightList = [{'date': datetime.now(), 'val': 0.0}]
exerciseList = []

hrmpathRE = re.compile ('(.+\/).+\.pdd', re.DOTALL)
exerRE = re.compile ('\[ExerciseInfo(\d)\](.+?)(\d{8}\.hrm)', re.DOTALL)
weightRE = re.compile ('.+Weight=(\d+).+', re.DOTALL)
datetimeRE = re.compile ('.+Date=(\d{4})(\d{2})(\d{2}).+StartTime=(\d{1,2}):(\d{2}):(\d{2}).+', re.DOTALL)

# Получаем список файлов с тренировками 
for dirname, dirnames, filenames in os.walk('data/'):
  for filename in filenames:
    if filename[-3:] in ['pdd']:
      exfiles.append (os.path.join(dirname, filename))

# Сортируем список со списком файлов
exfiles.sort()

for fpath in exfiles:
  # Читаем содержимое файла
  pdd_f = open(fpath, 'r')
  pdd_content = pdd_f.read()
  
  res = hrmpathRE.match (fpath)
  rootpath = res.group(1)
  
  iterator = exerRE.finditer (pdd_content)
  for match in iterator:
    # Обнуляем временные значения
    weight = 0
    date_object = None
    exerciseInfo = None
    hrmPath = None
    
    # Читам имя файла и суммарную запись о тренировке
    exerciseInfo = match.group(2)
    hrmPath = '%s%s' % (rootpath, match.group(3))
    
    # Читаем содержимое файла тренировки
    hrm_f = open(hrmPath, 'r')
    hrm_content = hrm_f.read()
    
    # Вытаскиваем дату занятия
    res = datetimeRE.match (hrm_content)
    date_object = datetime.strptime('%s/%s/%s %s:%s:%s' 
    % (res.group(1),res.group(2),res.group(3), res.group(4),res.group(5),res.group(6)),
    '%Y/%m/%d %H:%M:%S')
    
    # Вытаскиваем вес
    res = weightRE.match (hrm_content)
    weight = res.group(1)
    if weightList[-1]['val'] != float(weight):
      weightList.append ({'date': date_object, 'val': float(weight)})
      
    # Заполняем даные о тренировке
    exerciseList.append ({'date' : date_object,
    })
    
    #Закрываем hrm-файл
    hrm_f.close()
    
  #Закрываем pdd-файл
  pdd_f.close()
  
  
# Выводим тренировки
print '### Показатели тренировок:'
for i in exerciseList:
  print '%.2d.%.2d.%s, %.2d:%.2d' % (i['date'].day, i['date'].month, i['date'].year, i['date'].hour, i['date'].minute)
  
# Выводим вес
print '### Изменение веса:'
for i in weightList[1:]:
  print '%.1f %.2d.%.2d.%s, %.2d:%.2d' % (i['val'], i['date'].day, i['date'].month, i['date'].year, i['date'].hour, i['date'].minute)
