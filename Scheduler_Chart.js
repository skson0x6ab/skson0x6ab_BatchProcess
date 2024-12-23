import { Octokit } from "@octokit/rest";

const githubToken = process.env.GITHUB_TOKEN;
const repoOwner = 'skson0x6ab';
const githubRepository = 'DataRepository';
const branchName = 'main'; // 특정 브랜치명

const octokit = new Octokit({
  auth: githubToken, // GitHub 토큰 인증
});

const updateChartJson = async (data) => {
  try {
    // 1. chart.json 파일 내용 확인 (없으면 새로 생성)
    const { data: existingFile } = await octokit.rest.repos.getContent({
      owner: repoOwner,
      repo: githubRepository,
      path: 'chart.json',
      ref: branchName,
    });

    // 2. chart.json이 이미 존재하는 경우 -> 파일을 수정하기 위해 base64로 인코딩된 내용을 받음
    const fileContent = Buffer.from(JSON.stringify(data, null, 2)).toString('base64');

    // 3. chart.json 파일을 푸시 (업데이트)
    const updateResponse = await octokit.rest.repos.createOrUpdateFileContents({
      owner: repoOwner,
      repo: githubRepository,
      path: 'chart.json',
      message: 'Update chart.json with new commit details',
      content: fileContent,  // 파일의 내용을 base64로 인코딩해서 전달
      sha: existingFile.sha, // 기존 파일의 SHA를 전달하여 덮어쓰기
      branch: branchName, // 브랜치 지정
    });

    console.log('chart.json 파일이 성공적으로 푸시되었습니다:', updateResponse.data);
  } catch (error) {
    console.error('chart.json 푸시 중 오류 발생:', error.message);
  }
};

// 예시 데이터 (최신 커밋 내용)
const commitData = [
  {
    Date: '2024-12-23T04:09:50Z',
    Text: 'genshinRedeemCode.json',
  },
  {
    Date: '2024-12-22T04:09:50Z',
    Text: 'newFeatureFile.js',
  },
];

// 파일 푸시 실행
updateChartJson(commitData);