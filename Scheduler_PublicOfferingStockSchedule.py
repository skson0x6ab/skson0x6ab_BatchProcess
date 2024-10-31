import requests
from base64 import b64encode
import json
from bs4 import BeautifulSoup
import os
import urllib3 
from urllib3.util.ssl_ import create_urllib3_context
import certifi

context = create_urllib3_context()
context.set_ciphers('DEFAULT@SECLEVEL=1')
# SSL 설정을 위한 PoolManager 객체 생성
http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where(),  # 최신 CA 인증서 목록 제공
    ssl_context=context
)
token = os.environ.get('GITHUB_TOKEN')
owner = 'skson0x6ab'
repo = 'DataRepository'
file_path = 'PublicOfferingStockSchedule.json'
url = 'https://www.38.co.kr/html/fund/'

DictionaryData = []

if __name__ == "__main__":

    tmp_response = http.request('GET', url)
    response = tmp_response.data
    soup = BeautifulSoup(response, "html.parser")
    tmp_1_HTML = soup.find('table', summary='공모주 청약일정').find_all('td', height='30')

    for i in tmp_1_HTML:
        tmp_a_href = i.a['href']
        tmp_url = f'https://www.38.co.kr{tmp_a_href}'
        sub_tmp_response = http.request('GET', tmp_url)
        tmp_response = sub_tmp_response.data
        tmp_soup = BeautifulSoup(tmp_response, "html.parser")

        tmp_2_HTML = tmp_soup.find('table', summary='공모청약일정').find_all('td')
        tmp_3_HTML = tmp_soup.find('table', summary='기업개요').find_all('td')
        tmp_4_HTML = tmp_soup.find('table', summary='공모정보').find_all('td')

        tmp_data = {
            "stockname": tmp_3_HTML[1].get_text(strip=True),
            "securities": tmp_4_HTML[15].get_text(strip=True),
            "schedule": tmp_2_HTML[4].get_text(strip=True),
            "buy": tmp_2_HTML[10].get_text(strip=True),
            "subscription": tmp_2_HTML[12].get_text(strip=True),
            "competiton": tmp_4_HTML[9].get_text(strip=True),
        }
        DictionaryData.append(tmp_data)

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
