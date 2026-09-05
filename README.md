本项目是一组面向 AI Coding 的独立 Agent Skills。

它不预设一条必须遵循的重型工作流。每个 skill 只解决一个明确问题，开发者可以根据任务自由选择、排序和组合。

## 设计原则

- **独立**：每个 skill 都可以单独使用，不依赖其他 skill 才能成立。
- **可组合**：skill 通过计划、代码差异、测试证据、审查报告等通用产物协作，而不是相互硬编码调用。
- **按需使用**：任务需要什么就使用什么，不为流程完整而调用无价值的步骤。
- **证据优先**：计划写清可验收结果，实现强调有价值的测试，诊断追求根因证据，审查与验证给出可复核结论。
- **上游隔离**：第三方 skill 保持独立并固定版本，方便追踪来源和更新。

## 目录结构

```text
.
├── .agents/plugins/marketplace.json
├── .claude-plugin/marketplace.json
├── AGENTS.md
├── README.md
├── distribution/catalog.json
├── plugins/                         # 生成的 Codex / Claude Code 插件
│   ├── engineering/
│   ├── baoyu-design/
│   └── handoff/
├── scripts/build_distribution.py
├── skills/
│   ├── engineering/
│   │   ├── root-cause/
│   │   ├── review/
│   │   ├── tdd-implement/
│   │   ├── verify/
│   │   └── write-plan/
│   └── deprecated/
└── third-party/
    ├── baoyu-design/
    ├── baoyu-design.upstream.json
    ├── handoff/
    ├── handoff.upstream.json
    └── licenses/
```

## 工程技能

| Skill | 职责 | 不负责 |
| --- | --- | --- |
| [write-plan](skills/engineering/write-plan/SKILL.md) | 将需求整理为可执行计划，包括目标、范围与约束、实现方向、可选技术方案、验收标准、可选 Tasks，以及测试与验收方式 | 实现代码、执行验证或审查 |
| [tdd-implement](skills/engineering/tdd-implement/SKILL.md) | 根据当前任务实现代码，并在高价值场景执行 test-first；测试强度由风险决定 | 需求规划、独立审查或最终验收 |
| [root-cause](skills/engineering/root-cause/SKILL.md) | 基于证据定位问题根因，区分现象、触发条件与根本原因 | 修改代码或代替修复决策 |
| [review](skills/engineering/review/SKILL.md) | 由上下文干净的 subagent 对当前工作区差异进行独立、对抗性审查 | 修改代码、给出修复实现或执行动态验收 |
| [verify](skills/engineering/verify/SKILL.md) | 通过集成测试、E2E、自动化操作或 Playwright CLI 等方式验证结果是否符合预期 | 实现功能或把一次性验收自动转化为永久回归测试 |

每个 skill 的完整规则与边界以对应的 `SKILL.md` 为准。

## 三方 Skill

### baoyu-design

[baoyu-design](third-party/baoyu-design/SKILL.md) 由 Jim Liu（宝玉）维护，上游仓库为 [`JimLiu/baoyu-design`](https://github.com/JimLiu/baoyu-design)。该 skill 用于从需求到 UI 设计的工作，包括页面视觉、设计系统约束、原型和实现交接。它可以读取团队提供的设计规范，并据此产出符合约束的设计方案。

仓库中的副本保持上游原样，引入版本固定为 commit `026d4ea012bdd5cada72ac8cc13f21ba4edf2245`：

- [来源与版本记录](third-party/baoyu-design.upstream.json)
- [MIT 许可证](third-party/licenses/baoyu-design-MIT.txt)

更新时应重新固定明确的上游 commit、核对目录内容，并同步来源与许可证记录。

### handoff

[handoff](third-party/handoff/SKILL.md) 由 Matt Pocock 维护，上游仓库为 [`mattpocock/skills`](https://github.com/mattpocock/skills)。该 skill 用于在切换会话或窗口前，将当前对话压缩成可供另一个 Agent 接续的交接文档。它会要求引用已有产物、移除敏感信息，并根据下一会话的目标调整交接内容。

仓库中的副本保持上游原样，引入版本固定为 commit `3cca18b368ae95cdbdebbff572ccafa662551015`：

- [来源与版本记录](third-party/handoff.upstream.json)
- [MIT 许可证](third-party/licenses/handoff-MIT.txt)

更新时应重新固定明确的上游 commit、核对目录内容，并同步来源与许可证记录。

## Marketplace

仓库提供三个彼此独立的插件：

| Plugin | 内容 | 安装策略 |
| --- | --- | --- |
| `engineering` | `write-plan`、`tdd-implement`、`root-cause`、`review`、`verify` | Codex、Claude Code 均显式安装 |
| `baoyu-design` | vendored 的 `baoyu-design` skill | 始终显式安装 |
| `handoff` | vendored 的 `handoff` skill | 始终显式安装 |

添加 marketplace 只注册可用插件，不会自动安装或启用 `engineering`、`baoyu-design`、`handoff`。

### Codex

```sh
codex plugin marketplace add https://github.com/dengdi30/skills.git
codex plugin add engineering@skills
```

按需安装第三方插件：

```sh
codex plugin add baoyu-design@skills
codex plugin add handoff@skills
```

也可以在 Codex CLI 中运行 `/plugins`，或在 Codex app 的 Plugins 页面中打开 `Skills` marketplace，再手动安装 `engineering`。`baoyu-design` 和 `handoff` 保持可选。安装后新建会话，再通过 skill 选择器或任务描述使用对应能力。

Codex IDE extension 当前不支持 plugins；需要在 IDE extension 中使用时，仍应把所需 skill 安装到项目的 `.agents/skills/`。

### Claude Code

```sh
claude plugin marketplace add https://github.com/dengdi30/skills.git
claude plugin install engineering@skills
```

按需安装第三方插件：

```sh
claude plugin install baoyu-design@skills
claude plugin install handoff@skills
```

Claude Code 中的插件 skill 使用命名空间，例如 `/engineering:review`、`/baoyu-design:baoyu-design` 和 `/handoff:handoff`。

### TRAE 企业版

从仓库的 [Releases](https://github.com/dengdi30/skills/releases) 下载对应版本的 TRAE 附件。`v1.0.0` 提供：

```text
engineering-1.0.0.zip
baoyu-design-1.0.0.zip
handoff-1.0.0.zip
SHA256SUMS
```

`engineering-1.0.0.zip` 是交付 bundle，需要先解压，再将其中五个独立 skill ZIP 分别上传到 TRAE 企业技能。`baoyu-design-1.0.0.zip` 和 `handoff-1.0.0.zip` 都可以直接上传，并包含各自的许可证和固定上游版本记录。可使用 `SHA256SUMS` 校验下载文件的完整性。

不要发布或自动加载 `skills/deprecated/`。

## 组合示例

下面只是常见组合，不是固定流程：

- 复杂功能：先用 `write-plan` 明确范围，再按需要使用 `tdd-implement`、`review` 或 `verify`。
- 未知故障：先用 `root-cause` 收集证据并定位原因，再由开发者决定如何实现和验证修复。
- Web UI：先用 `baoyu-design` 形成设计产物，再选择合适的实现与验收方式。
- 会话或窗口切换：使用 `handoff` 生成脱敏的交接文档，再在新会话中引用该文档继续工作。
- 已有明确方案的小改动：可以直接使用 `tdd-implement`，无需为了形式补写计划。
- 只需验收已有结果：可以单独使用 `verify`。

组合时，前一个 skill 的产物应被视为通用输入，而不是触发下一个 skill 的强制信号。

## 历史归档

`skills/deprecated/` 保存历史 skills，仅用于审计、比较和迁移参考。它们不属于当前推荐能力集，也不应被默认安装或调用。

如需恢复某项历史能力，应重新评估其职责与边界，并将整理后的版本作为独立 skill 放入 `skills/engineering/`。

## 维护约定

- 第一方 skill 应保持单一职责和独立可用。
- 不在 skill 内规定完整开发流水线，也不强制调用其他 skill。
- 新增字段或步骤前，先判断它是否会实质提高结果正确性。
- 第三方目录优先保持上游原样；本地适配应另行维护并清楚记录。
- 文档应描述当前真实结构，不保留已经不存在的命令、目录或质量门禁。

仓库级维护规则见 [AGENTS.md](AGENTS.md)。
