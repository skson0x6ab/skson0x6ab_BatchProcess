import axios from 'axios';

const githubToken = process.env.GITHUB_TOKEN;
const repoOwner = 'skson0x6ab';
const githubRepository = 'DataRepository';
const branchName = "main";  // 특정 브랜치명

const getCommitDetails = async () => {
  try {
    const githubApiUrl = `https://api.github.com/repos/${repoOwner}/${githubRepository}/commits?sha=${branchName}&per_page=100`;

    const response = await axios.get(githubApiUrl, {
      headers: {
        Authorization: `Bearer ${githubToken}`,  // GitHub 토큰 인증
      },
    });

    const commitDetails = await Promise.all(response.data.map(async (commit) => {
      const commitSha = commit.sha;
      const commitDate = commit.commit.author.date;
      const dateObj = new Date(commitDate);
      dateObj.setHours(dateObj.getHours() + 9);  // UTC에서 KST로 변환
      const commitDateKST = dateObj.toISOString().split('T')[0]; // 'YYYY-MM-DD' 형식으로 반환

      // 개별 커밋의 상세 정보에서 변경된 파일 목록을 가져오기
      const commitDetailUrl = `https://api.github.com/repos/${repoOwner}/${githubRepository}/commits/${commitSha}`;
      const commitDetailResponse = await axios.get(commitDetailUrl, {
        headers: {
          Authorization: `Bearer ${githubToken}`,
        },
      });

      const filesChanged = commitDetailResponse.data.files ? commitDetailResponse.data.files.map(file => file.filename) : [];

      // filesChanged가 비어있으면 해당 커밋을 포함하지 않음
      if (filesChanged.length === 0) return null;

      return {
        date: commitDateKST,
        filesChanged: filesChanged,
      };
    }));

    // null 값이 아닌 커밋만 추가
    const validCommitDetails = commitDetails.filter(commit => commit !== null);

    // 중복 날짜 제거 및 출력
    const uniqueCommitDetails = validCommitDetails.filter((value, index, self) => {
      return self.findIndex(v => v.date === value.date && JSON.stringify(v.filesChanged) === JSON.stringify(value.filesChanged)) === index;
    });

    console.log("Commit details (KST) with changed files:", uniqueCommitDetails);  // 커밋 날짜와 변경된 파일 목록 출력

  } catch (error) {
    console.error("Error fetching commits:", error.message);
  }
};

// 커밋 날짜와 변경된 파일 목록 추출
getCommitDetails();