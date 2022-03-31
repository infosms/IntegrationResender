from datetime import datetime, time
from os import listdir
import requests as requests
from lxml import etree
path = '/home/khandosaly/job/dump_documentolog/script'
needed = []

for x in listdir(path):
    try:
        if datetime.strptime(x.split('.')[0], '%H:%M:%S:%f').time() < time(hour=10, minute=18, second=52):
            if etree.parse(rf'{path}/{x}').getroot().xpath("//performers")[0].text == "1629005":
                needed.append(f'{path}/{x}')
    except Exception as e:
        print(e)

i = 0
for x in needed:
    i += 1
    response = requests.post(
        'https://esedo.isirius.kz/sirius-soap',
        data=etree.tostring(etree.parse(rf'{x}').getroot(), encoding='unicode').encode('utf-8'),
        headers={'content-type': 'application/xml'},
        verify=False)
    if response.status_code in [200, 201]:
        print(f'{i}/{len(needed)} Success')
    else:
        print(f'{i}/{len(needed)} {response.status_code} {response.text}')