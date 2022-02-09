# Integration Resender

## Инструкция по настройке cron:
```
crontab -e
```

Добавляем в конец строчку:
```
0 */2 * * * cd /log && /usr/bin/env python3 /log/resender.py 1 current >> /log/cron_log.txt
```

## Инструкция по одиночному запуску:
```
python3 resender.py -h
```