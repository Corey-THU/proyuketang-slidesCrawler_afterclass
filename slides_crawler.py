import os
import re
import sys
import json
import requests
from fpdf import FPDF
from PIL import Image
from io import BytesIO

# initialize
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        sessionid = config['sessionid']
        lesson_id = config['lesson_id']
except:
    print('Error: config.json not found or invalid.')
    sys.exit()

num     = 1
url     = f'https://pro.yuketang.cn/api/v3/lesson-summary/student'
headers = {
    'cookie'    : f'sessionid={sessionid}',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
}

# get lesson info
response = requests.get(f'{url}?lesson_id={lesson_id}', headers=headers)
if response.status_code != 200:
    print('Error:', response.status_code)
    sys.exit()
response = response.json()
if response['code'] != 0:
    print(response['message'])
    sys.exit()
presentations = response['data']['presentations']
lesson_title  = response['data']['lesson']['title']
print(f'Lesson title: {lesson_title}.')
lesson_title  = re.sub(r'[\\/:*?"<>|]', '.', lesson_title)
os.makedirs(lesson_title, exist_ok=True)

# get presentations
for presentation in presentations:
    presentation_id    = presentation['id']
    presentation_title = presentation['title']
    response = requests.get(f'{url}/presentation?presentation_id={presentation_id}&lesson_id={lesson_id}', headers=headers)
    print(f'Downloading presentation {num}: {presentation_title}...')
    if response.status_code != 200:
        print('Error:', response.status_code)
        sys.exit()
    response = response.json()
    if response['code'] != 0:
        print(response['message'])
        sys.exit()
    
    # download slides and add to pdf
    pdf    = FPDF()
    slides = response['data']['slides']
    for slide in slides:
        response = requests.get(f'{slide['cover']}', headers=headers)
        if response.status_code != 200:
            print('Error:', response.status_code)
            sys.exit()
        img = Image.open(BytesIO(response.content))
        width, height = img.size
        pdf.add_page(format=(width*25.4/72, height*25.4/72))
        pdf.image(BytesIO(response.content), x=0, y=0, w=width*25.4/72, h=height*25.4/72)
    presentation_title = re.sub(r'[\\/:*?"<>|]', '.', presentation_title)
    pdf.output(f'{lesson_title}/{num}_{presentation_title}.pdf')
    num += 1

print('Done.')