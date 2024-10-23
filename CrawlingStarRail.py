import requests
from base64 import b64encode
import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os
from requests_html import HTMLSession

token = os.environ.get('GITHUB_TOKEN')
owner = 'skson0x6ab'
repo = 'DataRepository'
file_path = 'StarRail.json'
url = 'https://hsr.hoyoverse.com/ko-kr/news'
#url = 'https://www.38.co.kr/'
#os.environ['PYPPETEER_CHROMIUM_REVISION'] = '1263111'
if __name__ == "__main__":
    #response = urlopen(url)

    session = HTMLSession()
    response = session.get(url)
    response.html.render()

    soup = BeautifulSoup(response.html.html, "html.parser")

    #테스트용 html 읽기
    #with open('starrail.html', 'r', encoding='utf-8') as file:
    #    soup = BeautifulSoup(file, "html.parser")
    subParsingRule = ["sTitle:", "\"", "dtStartTime:"]
    tmpHTML = soup.find_all('script')
    keyword = "NUXT"
    tmpHTML_2 = ""

    for i in tmpHTML:
        if keyword in str(i):
            tmpHTML_2 = str(i)
            break

    parts = tmpHTML_2.split(subParsingRule[0])

    DictionaryData = []
    for j in range(2, len(parts)):
        tmpString = parts[j].split(subParsingRule[1])

        if len(tmpString[1]) <= 7:
            break

        text1 = tmpString[1].replace("\"", "")
        tmpString2 = parts[j].split(subParsingRule[2])
        timestamp1 = tmpString2[1].split(subParsingRule[1])
        timestamp2 = timestamp1[1].replace("\"", "")

        tmpdata = {
            "Category": "[업데이트]",
            "Text": text1,
            "Date": timestamp2
        }

        DictionaryData.append(tmpdata)

    jsonData = json.dumps(DictionaryData, ensure_ascii=False)
    #임시추가
    jsonData = soup

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