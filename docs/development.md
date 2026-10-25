# 开发与测试

从仓库根目录安装开发依赖并运行测试：

```text
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

`tests/unit` 检查 V1.4/V2 规则；`tests/integration` 检查固定版本和原始证据覆盖；
`tests/release` 检查独立安装与包边界。打包检查会把 ZIP 解压至临时目录，脱离源码仓库运行。

评测工具与数据分开：

```text
python tools/calibration/calibrate_snapshots.py
python tools/calibration/summarize_codex_calibration.py
```

上述两条是离线规则回归与已保存结果的汇总，不会调用模型。
需要新模型评测时使用下面的入口，调用者自行登录 Codex CLI，运行会使用其账号配额：

```text
python tools/calibration/run_codex_calibration.py --private-run-dir ../private-codex-runs
python tools/calibration/run_v2_behavioral_probe.py --private-run-dir ../private-codex-runs --run-label NEW-RUN
```

已保存的首轮批次会跳过；V2 复测必须使用新标签。保留原始输出与协议快照，不以期望答案改写模型结果。
历史 JSON、提示词快照和证据数据的字节保持不变；原路径到新路径的完整对应见
[repository-layout.json](repository-layout.json)。历史文档中的旧命令以本页为准。

## 模块边界

- 运行时只读取技能目录内的资源，不依赖 `docs/`、`data/`、`tests/` 或 `legacy/`。
- 校准工具按需加载 `legacy/v1.4` 作对照，不进入当前交付包。
- 修改运行资源时同步核对 `release/manifest.json`；遗漏或额外文件会使构建失败。
- 调整目录后检查本地文档链接和解压后的运行情况。
