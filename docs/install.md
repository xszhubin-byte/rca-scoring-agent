# 安装与使用

当前交付版本：`2.0.0-alpha.5`，供试用和反馈，尚未证明评分准确率或维度最优性。

## 1. 获取正确的文件

获取发布资产 `rca-scoring-2.0.0-alpha.5.zip` 与同一版本的 `SHA256SUMS.txt`。
校验 ZIP 的 SHA-256 与清单一致。清单用于检查文件完整性，不是数字签名。
不要把 GitHub 自动生成的整个源码压缩包当作技能安装包。

## 2. 放入目标项目

ZIP 内有一层 `rca-scoring/`。将该文件夹放入目标项目的 `.agents/skills/`，结果应为：

```text
YOUR_PROJECT/
  .agents/skills/rca-scoring/
    SKILL.md
    requirements.txt
    scripts/
    references/
    examples/
    VERSION
    PACKAGE_MANIFEST.json
```

Codex 会从项目的 `.agents/skills` 发现本地技能，可显式使用 `$rca-scoring`。
如果未显示，重启 Codex 后检查 `/skills`。[官方本地技能说明](https://learn.chatgpt.com/docs/build-skills)

## 3. 安装依赖并自检

需要 Python 3.10+。在目标项目目录运行：

```text
python -m pip install -r .agents/skills/rca-scoring/requirements.txt
python .agents/skills/rca-scoring/scripts/assess_v2.py .agents/skills/rca-scoring/examples/result.example.json
```

结构示例没有真实证据，预期返回 `needs_evidence`、综合分为 null。这说明安装及校验器运行正常，
不代表已经完成某个真实缺陷的评估。

## 4. 使用技能

当前版本先用随包的 `scripts/review_contract.py` 生成每项审查对象与来源可用性表，
再由 Codex 评分。完整报告需要关联一条 `author_statement` 来源记录。
来源表不预填质量分，也不把未知事实变成已核验事实。

在 Codex 输入：

```text
使用 $rca-scoring 审查这份日常软件缺陷 RCA。
按 owner_rca 模式保留我的原文，核对固定版本代码和相关测试，
输出诊断 JSON、关键反证、缺失证据及优先改进项。
```

只有 PR 或补丁时，明确选择 `pr_author_proxy` 或 `artifact_review`；不要把它自动当作原作者的 RCA。
私有代码、日志和凭据留在自己的授权环境，发布包不附带任何 GitHub/Gerrit 密钥。

需要做方法研究或重跑公开案例评测时，再克隆完整研发仓库，见[开发说明](development.md)。


## 与稳定性测试一致的模型设置

固定结构化输入的重复性验收使用显式模型标识 `gpt-6-astra` 与 `medium` 推理设置。
切换模型、规则、证据或输入约定后，应重新测试，而不是沿用该配置的结论。
CLI 未暴露精确后端 snapshot ID，因此本结论不承诺未来服务版本永远不变。

可以用以下命令进入对应 Codex 会话，再调用技能：

```text
codex --model gpt-6-astra --config 'model_reasoning_effort="medium"'
```
