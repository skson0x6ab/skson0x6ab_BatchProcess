from base64 import b64encode
import requests
import json
from bs4 import BeautifulSoup
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time

token = os.environ.get('GITHUB_TOKEN')
owner = 'skson0x6ab'
repo = 'DataRepository'
file_path = 'StarRail.json'
url = 'https://hsr.hoyoverse.com/ko-kr/news'
#url = 'https://www.38.co.kr/html/fund/'

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    WebDriverWait(driver, 600).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )

    time.sleep(60)

    response = driver.page_source

    print(response)
    soup = BeautifulSoup(response, "html.parser")

    #테스트용 html 읽기
    #with open('starrail2.html', 'r', encoding='utf-8') as file:
    #    soup = BeautifulSoup(file, "html.parser")
    right = soup.find_all('div', class_='right')
    DictionaryData = []
    for i in right:

        news_title = i.find('div', class_='news-title').get_text().replace('\n', '')
        date_time = i.find('div', class_='date-time').get_text().replace('\n', '')

        tmpdata = {
            "Category": "[소식]",
            "Text": news_title,
            "Date": date_time
        }
        DictionaryData.append(tmpdata)

    jsonData = json.dumps(DictionaryData, ensure_ascii=False)

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{file_path}'
    
    response = requests.get(url, headers=headers)

    # base64로 파일 내용 인코딩
    encoded_jsonData = b64encode(jsonData.encode('utf-8')).decode('utf-8')

    # 파일 추가 또는 업데이트
    data = {
        'content': encoded_jsonData,
        'branch': 'main'  # 원하는 브랜치명 사용
    }

    if response.status_code == 200:
        # 파일이 이미 존재하면 SHA 값 가져오기
        sha = response.json()['sha']
        print(f"File exists with SHA: {sha}")
        data['sha'] = sha
        data['message'] = "update json file"
    else:
        # 파일이 존재하지 않으면 SHA 값은 None
        sha = None
        data['message'] = "new json file"
        print("File does not exist.")
    # API 요청

    response = requests.put(url, headers=headers, data=json.dumps(data))

    if response.status_code in [201, 200]:
        print(response.status_code)
        print("File added/updated successfully!")
    else:
        print(f"Error: {response.json()}")

