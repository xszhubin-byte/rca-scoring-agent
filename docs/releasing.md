# 如何把版本交给别人

目前版本是 `2.0.0-alpha.1`，应标记为 **Pre-release**。目录重构没有把研究候选升级成稳定标准。

## 构建交付物

在与待发布提交一致的源码目录运行：

```text
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python tools/release/build_release.py
```

构建器只接受 `release/manifest.json` 中列出的运行文件；检查包内链接、字节、ZIP 完整性和常见密钥标记。
当前 9 个源文件加上生成的 `VERSION`、`PACKAGE_MANIFEST.json`，共 11 个文件。
同样的运行文件生成相同 ZIP 字节，不把本机路径和当前时间写入包内。

`dist/` 的三个交付物：

1. `rca-scoring-2.0.0-alpha.1.zip`：交给使用者安装。
2. `SHA256SUMS.txt`：下载完整性校验。
3. `release-manifest.json`：版本、运行文件 hash、包大小及包 hash。

可先直接把这三个文件交给试用者；对方不必下载整个研发仓库。

## 发布到 GitHub Releases

源码提交、Git tag 和 GitHub Release 是不同对象。把源码推送到 `main` 不会自动生成 Release。

1. 在仓库的 **Releases → Draft a new release** 中选择待发布源码提交作为目标。
2. 创建 tag `v2.0.0-alpha.1`，填写同名标题。
3. 将 [版本说明](../release/notes/2.0.0-alpha.1.md) 的正文复制到说明框。
4. 上传 `dist/` 中上述三个资产，勾选 **This is a pre-release**。
5. 核对目标提交与三个资产后发布。将 Release 页面发给使用者，安装步骤链接到 [install.md](install.md)。

GitHub 提供的自动 **Source code.zip** 是全仓库快照，使用者应下载手动上传的技能 ZIP。
这些操作及预发布标记的定义见 [GitHub 官方发布说明](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)。

使用已安装并登录的 GitHub CLI 时，也可执行以下等价操作。将 `SOURCE_COMMIT_SHA` 替换成已经核实的提交：

```text
gh release create v2.0.0-alpha.1 dist/rca-scoring-2.0.0-alpha.1.zip dist/SHA256SUMS.txt dist/release-manifest.json --repo xszhubin-byte/rca-scoring-agent --target SOURCE_COMMIT_SHA --prerelease --title "RCA Scoring 2.0.0-alpha.1" --notes-file release/notes/2.0.0-alpha.1.md
```

## 后续版本

后续修订更新 `release/manifest.json` 的版本、技能中的版本声明及对应说明；生成新文件名和新 tag。
已发布的版本不覆盖。生产稳定版的判断仍需独立专家校准及留出数据，不能只以打包成功为依据。
