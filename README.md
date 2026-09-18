本项目是一组面向 AI Coding 的独立 Agent Skills。

它不预设一条必须遵循的重型工作流。每个 skill 只解决一个明确问题，开发者可以根据任务自由选择、排序和组合。

## 设计原则

- **独立**：第一方 skill 都可以单独使用；第三方 skill 保留上游依赖，并随插件一并提供必需依赖。
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
│   ├── handoff/
│   ├── grill-me/
│   └── show-me/
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
    ├── grill-me/
    ├── grill-me.upstream.json
    ├── grilling/
    ├── grilling.upstream.json
    ├── show-me/
    ├── show-me.upstream.json
    └── licenses/
```

## 工程技能

| Skill | 职责 | 不负责 |
| --- | --- | --- |
| [write-plan](skills/engineering/write-plan/SKILL.md) | 将需求整理为可执行计划，包括目标、范围与约束、实现方向、可选技术方案、验收标准、可选 Tasks，以及测试与验收方式 | 实现代码、执行验证或审查 |
| [tdd-implement](skills/engineering/tdd-implement/SKILL.md) | 根据当前任务实现代码，并在高价值场景执行 test-first；测试强度由风险决定 | 需求规划、独立审查或最终验收 |
| [root-cause](skills/engineering/root-cause/SKILL.md) | 基于证据定位问题根因，区分现象、触发条件与根本原因 | 修改代码或代替修复决策 |
| [review](skills/engineering/review/SKILL.md) | 由上下文干净的 subagent 分别提供需求符合性、正确性与回归的审查意见 | 修改代码、替用户决定修复取舍或执行动态验收 |
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

### grill-me 与 grilling

[grill-me](third-party/grill-me/SKILL.md) 和 [grilling](third-party/grilling/SKILL.md) 由 Matt Pocock 维护，上游仓库为 [`mattpocock/skills`](https://github.com/mattpocock/skills)。`grill-me` 是用户显式调用的入口，委托 `grilling` 执行访谈。`grilling` 沿设计决策树分轮提问，每轮只询问前置条件已明确的问题，并给出建议答案；能从环境查明的事实交给 subagent 查证，决策由用户回答。

两个 skill 均保持上游原样，固定为引入时最新主分支 commit `3cca18b368ae95cdbdebbff572ccafa662551015`，作为同一个 `grill-me` 插件分发：

- `grill-me`：[来源与版本记录](third-party/grill-me.upstream.json)、[MIT 许可证](third-party/licenses/grill-me-MIT.txt)
- `grilling`：[来源与版本记录](third-party/grilling.upstream.json)、[MIT 许可证](third-party/licenses/grilling-MIT.txt)

单独复制 `grill-me` 无法提供完整访谈能力，需同时提供 `grilling`。二者不承担 ADR 或领域术语表维护；与其他 skill 的组合由用户决定。

更新时应将两个 skill 固定到同一明确的上游 commit、核对完整目录，并同步各自的来源与许可证记录。插件的 `UPSTREAM.json` 汇总两份记录，各 TRAE skill ZIP 则携带自己的 `UPSTREAM.json`。

### show-me

[show-me](third-party/show-me/SKILL.md) 由 HumanLayer 维护，上游仓库为 [`humanlayer/skills`](https://github.com/humanlayer/skills)。该 skill 用简洁图示、代码结构草图和聚焦的 HTML 产物解释当前话题，根据问题选择伪代码、调用树、组件树、文件树、差异或 Mermaid 图。

仓库中的副本保持上游原样，引入版本固定为 commit `3c2629142c5d437428269b1b722b08c0b87f574d`：

- [来源与版本记录](third-party/show-me.upstream.json)
- [MIT 许可证](third-party/licenses/show-me-MIT.txt)

更新时应重新固定明确的上游 commit、核对目录内容，并同步来源与许可证记录。

## Marketplace

仓库提供五个彼此独立的插件：

| Plugin | 内容 | 安装策略 |
| --- | --- | --- |
| `engineering` | `write-plan`、`tdd-implement`、`root-cause`、`review`、`verify` | Codex、Claude Code 均显式安装 |
| `baoyu-design` | vendored 的 `baoyu-design` skill | 始终显式安装 |
| `handoff` | vendored 的 `handoff` skill | 始终显式安装 |
| `grill-me` | vendored 的 `grill-me` 入口与 `grilling` 访谈规则 | 始终显式安装 |
| `show-me` | vendored 的 `show-me` skill | 始终显式安装 |

添加 marketplace 只注册可用插件，不会自动安装或启用任何插件。

### Codex

```sh
codex plugin marketplace add https://github.com/dengdi30/skills.git
codex plugin add engineering@skills
```

按需安装第三方插件：

```sh
codex plugin add baoyu-design@skills
codex plugin add handoff@skills
codex plugin add grill-me@skills
codex plugin add show-me@skills
```

也可以在 Codex CLI 中运行 `/plugins`，或在 Codex app 的 Plugins 页面中打开 `Skills` marketplace，再手动安装需要的插件。所有第三方插件保持可选。安装后新建会话，再通过 skill 选择器或任务描述使用对应能力。

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
claude plugin install grill-me@skills
claude plugin install show-me@skills
```

Claude Code 中的插件 skill 使用命名空间，例如 `/engineering:review`、`/baoyu-design:baoyu-design`、`/handoff:handoff`、`/grill-me:grill-me` 和 `/show-me:show-me`。

### TRAE 企业版

从仓库的 [v1.1.0 Release](https://github.com/dengdi30/skills/releases/tag/v1.1.0) 下载对应的 TRAE 附件。Release 版本标识整套分发，各插件保留自己的版本号：

```text
engineering-1.1.0.zip
baoyu-design-1.0.0.zip
handoff-1.0.0.zip
grill-me-1.0.0.zip
show-me-1.0.0.zip
SHA256SUMS
```

`engineering-1.1.0.zip` 是交付 bundle，需要先解压，再将其中五个独立 skill ZIP 分别上传到 TRAE 企业技能。`grill-me-1.0.0.zip` 也是 bundle，需先解压，再将其中的 `grill-me.zip` 与 `grilling.zip` 同时上传。`baoyu-design-1.0.0.zip`、`handoff-1.0.0.zip` 和 `show-me-1.0.0.zip` 可直接上传。

各第三方 skill ZIP 均包含许可证和固定上游版本记录。可使用 `SHA256SUMS` 校验下载文件的完整性；在本地运行 `python3 scripts/build_distribution.py` 可重新生成 `dist/trae/` 中的分发包。

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
