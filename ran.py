# -*- coding: utf-8 -*-
import os
import re
import datetime

exfiles = []
weightList = [{'date': datetime.datetime.now(), 'val': 0.0}]
exerciseList = []

tcxTemplate = '<?xml version="1.0" encoding="UTF-8"?>\n\
<TrainingCenterDatabase version="1.0" creator="runtastic - makes sports funtastic, http://www.runtastic.com" \
xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd" \
xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1" xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2" \
xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2" xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1">\n\
<Activities>\n\t<Activity Sport="{Activity}">\n\t\t<Id>{StartTime}</Id>\n\t\t<Lap StartTime="{StartTime}">\n\t\t\t<TotalTimeSeconds>{TotalTimeSeconds}</TotalTimeSeconds> \
\n\t\t\t<DistanceMeters>{DistanceMeters}</DistanceMeters>\n\t\t\t<Calories>{Calories}</Calories>\n\t\t\t<AverageHeartRateBpm><Value>{AverageHeartRateBpm}</Value>\
</AverageHeartRateBpm>\n\t\t\t<MaximumHeartRateBpm><Value>{MaximumHeartRateBpm}</Value></MaximumHeartRateBpm>\n\t\t</Lap>\n\t</Activity>\n</Activities>\n</TrainingCenterDatabase>'

hrmpathRE = re.compile ('(.+\/).+\.pdd', re.DOTALL)
exerRE = re.compile ('\[ExerciseInfo(\d)\](.+?)(\d{8}\.hrm)', re.DOTALL)
weightRE = re.compile ('.+Weight=(\d+).+', re.DOTALL)
datetimeRE = re.compile ('.+Date=(\d{4})(\d{2})(\d{2}).+StartTime=(\d{1,2}):(\d{2}):(\d{2}).+', re.DOTALL)
lengthRE = re.compile ('.+Length=(.+?)\n', re.DOTALL)

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
    trlength = ''
    date_object = None
    exerciseInfo = None
    hrmPath = None
    
    # Читам имя файла и суммарную запись о тренировке
    exerciseInfo = match.group(2)
    hrmPath = '%s%s' % (rootpath, match.group(3))
    
    sport = (int)(exerciseInfo.split('\n')[3].split('\t')[0])
    if sport == 1:
      sport = 'running'
    elif sport == 2:
      sport = 'cycling'
    else:
      sport = None
    
    calories = (int)(exerciseInfo.split('\n')[3].split('\t')[5])
    distance = (int)(exerciseInfo.split('\n')[4].split('\t')[0])
    averageHeartRateBpm = (int)(exerciseInfo.split('\n')[10].split('\t')[0])
    maximumHeartRateBpm = (int)(exerciseInfo.split('\n')[10].split('\t')[1])
    
    # Читаем содержимое файла тренировки
    hrm_f = open(hrmPath, 'r')
    hrm_content = hrm_f.read()
    
    # Вытаскиваем дату занятия
    res = datetimeRE.match (hrm_content)
    date_object = datetime.datetime.strptime('%s/%s/%s %s:%s:%s' 
    % (res.group(1),res.group(2),res.group(3), res.group(4),res.group(5),res.group(6)),
    '%Y/%m/%d %H:%M:%S')
    
    # Вытаскиваем вес
    res = weightRE.match (hrm_content)
    weight = res.group(1)
    if weightList[-1]['val'] != float(weight):
      weightList.append ({'date': date_object, 'val': float(weight)})

    # Вытаскиваем продолжительность занятия
    res = lengthRE.match (hrm_content)
    trlength = res.group(1)[:-3]
    tmp = trlength.split(':')
    trlength_sec = ((int)(tmp[0]) * 60 * 60) + ((int)(tmp[1]) * 60) + (int)(tmp[2])
    
            
    # Заполняем даные о тренировке
    if sport:
      exerciseList.append ({'date' : date_object,
                          'length' : trlength_sec,
                          'sport' : sport,
                          'calories' : calories,
                          'distance' : distance,
                          'averageHeartRateBpm' : averageHeartRateBpm,
                          'maximumHeartRateBpm' : maximumHeartRateBpm,
      })
    
    #Закрываем hrm-файл
    hrm_f.close()
  #Закрываем pdd-файл
  pdd_f.close()
  
  
# Выводим тренировки
print '### Показатели тренировок:'
for i in exerciseList:
  print '%s - %s %ds %dm %dc %dBpm/%dBpm' % ((i['date'] - datetime.timedelta(hours = 4)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
  i['sport'], i['length'], i['distance'], i['calories'], i['averageHeartRateBpm'], i['maximumHeartRateBpm'])
  out_f = open('out/%s-%s.tcx' % (i['sport'], i['date'].strftime("%Y%m%d%H%M")), 'w')
  out_content = tcxTemplate
  out_content = out_content.replace('{Activity}', i['sport']).replace('{StartTime}', (i['date'] - datetime.timedelta(hours = 4)).strftime('%Y-%m-%dT%H:%M:%S.000Z'))
  out_content = out_content.replace('{TotalTimeSeconds}', str(i['length'])).replace('{DistanceMeters}', str(i['distance'])).replace('{Calories}', str(i['calories']))
  out_content = out_content.replace('{AverageHeartRateBpm}', str(i['averageHeartRateBpm'])).replace('{MaximumHeartRateBpm}', str(i['maximumHeartRateBpm']))
  out_f.write( out_content)
  out_f.close()
  
# Выводим вес
print '### Изменение веса:'
for i in weightList[1:]:
  print '%.1f %.2d.%.2d.%s, %.2d:%.2d' % (i['val'], i['date'].day, i['date'].month, i['date'].year, i['date'].hour, i['date'].minute)
