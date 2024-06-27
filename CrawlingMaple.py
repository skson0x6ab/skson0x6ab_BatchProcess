import requests
from base64 import b64encode
import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os

token = os.environ.get('GITHUB_TOKEN')
owner = 'skson0x6ab'
repo = 'DataRepository'
file_path = 'Maplestory.json'
url = 'https://maplestory.nexon.com/News/Update'

if __name__ == "__main__":
    response = urlopen(url)
    soup = BeautifulSoup(response, "html.parser")
    tmpHTML = soup.find('div', class_='update_board').find_all('li')

    DictionaryData = []
    for item in range(len(tmpHTML)):
        tmpdata = {
            "Category": item,
            "Text": tmpHTML[item].find('span').get_text(strip=True),
            "Date": tmpHTML[item].find('dd').get_text(strip=True)
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
