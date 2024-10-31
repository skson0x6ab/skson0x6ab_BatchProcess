import requests
from base64 import b64encode
import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os

token = os.environ.get('GITHUB_TOKEN')
owner = 'skson0x6ab'
repo = 'DataRepository'
file_path = 'FF14.json'
url = 'https://www.ff14.co.kr/news/notice?category=3'

if __name__ == "__main__":
    response = urlopen(url)
    soup = BeautifulSoup(response, "html.parser")

    jsonText = soup.find('tbody').find_all('a')
    jsonDate = soup.find_all('td', class_='date')

    DictionaryData = []
    for i in range(len(jsonText)):
        tmpData = {
            "Category": "[소식]",
            "Text": jsonText[i].get_text(strip=True),
            "Date": jsonDate[i].get_text(strip=True)
        }
        DictionaryData.append(tmpData)

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
