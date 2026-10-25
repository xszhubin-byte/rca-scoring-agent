# RCA Scoring Agent

面向日常软件缺陷的 RCA 审查技能。当前可打包版本为 **2.0.0-alpha.1（预发布）**：
六领域、24 个细项的诊断体系，证据状态与闭环阶段独立报告。尚未完成独立人工金标准校准。

## 使用者从哪里开始

- 安装及运行：[安装说明](docs/install.md)。
- 可直接安装的技能源码：[skills/rca-scoring](skills/rca-scoring/)。
- 当前版本内容及限制：[2.0.0-alpha.1 说明](release/notes/2.0.0-alpha.1.md)。
- 取证与模型实测记录：[实测报告](docs/reports/execution-2026-10-25.md)。

交付给使用者的是构建生成的 `rca-scoring-2.0.0-alpha.1.zip`，只包含独立技能及其运行资源。
GitHub 自动生成的 **Source code.zip** 是完整研发仓库，不是技能安装包。

## 仓库分类

| 目录 | 内容 | 放进技能版本包？ |
|---|---|---|
| `skills/rca-scoring/` | 技能入口、运行脚本、规则、输入 Schema 和示例 | 是，仅收录发布清单内的文件 |
| `tests/unit/` | 评分规则与证据门槛单元测试 | 否 |
| `tests/integration/` | 真实案例快照及版本一致性检查 | 否 |
| `tests/release/` | 包内容、可重复构建和独立安装测试 | 否 |
| `tools/calibration/` | Codex CLI 实测、复测与汇总工具 | 否 |
| `tools/release/` | 发布包构建工具 | 否 |
| `docs/research/` | 维度设计、方法调研及验证计划 | 否 |
| `docs/testing/`、`docs/reports/` | 实测方法、历史结论及失败记录 | 否 |
| `data/calibration/` | 公开证据、原始模型输出及合成测试数据 | 否 |
| `legacy/v1.4/` | 五维旧实现，供兼容性回归与历史对照 | 否 |
| `release/` | 当前版本、明确的文件清单和发布说明 | 仅生成版本与包清单信息 |

运行必需脚本跟随技能放在其 `scripts/` 内；采集、评测和打包脚本放在 `tools/`。
研发材料不会因为增加到仓库，就自动进入交付包。

## 开发与发布

```text
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python tools/release/build_release.py
```

生成的 `dist/` 包含技能 ZIP、`SHA256SUMS.txt` 和 `release-manifest.json`，不提交到源码目录。
完整步骤见[发布流程](docs/releasing.md)；目录迁移对照见 [repository-layout.json](docs/repository-layout.json)。
