import axios from 'axios';
import { Octokit } from "@octokit/rest";
const githubToken = process.env.GITHUB_TOKEN;
const repoOwner = 'skson0x6ab';
const githubRepository = 'DataRepository';
const filePath = 'starrailRedeemCode.json';
const branchName = "main";
const genshinUrl = "https://api.ennead.cc/mihoyo/starrail/codes";

(async () => {
  try {
    const apiResponse = await axios.get(genshinUrl);
    const data = apiResponse.data;

    const octokit = new Octokit({ auth: githubToken });

    let sha;
    try {
      const { data: fileData } = await octokit.repos.getContent({
        owner: repoOwner,
        repo: githubRepository,
        path: filePath,
        ref: branchName,
      });
      sha = fileData.sha;
    } catch (error) {
      if (error.status !== 404) throw error;
    }

    await octokit.repos.createOrUpdateFileContents({
      owner: repoOwner,
      repo: githubRepository,
      path: filePath,
      message: `Update Starrail RedeemCode: ${filePath}`,
      content: Buffer.from(JSON.stringify(data, null, 2)).toString("base64"),
      sha,
      branch: branchName,
    });

    console.log(`File successfully committed to GitHub at ${filePath}`);
  } catch (error) {
    console.error("Error:", error.message);
  }
})();