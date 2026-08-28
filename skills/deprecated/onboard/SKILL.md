---
name: onboard
description: "Use when first interacting with a new repo — discovers conventions, codifies them into wyrd structures, and primes working memory for the session."
---

# Onboard

第一次接触新仓库时使用：发现约定、把约定编码进 wyrd 结构、为本次 session 预热工作记忆。后续正常使用代码搜索与读取即可——只在显式"onboard 这个仓库 / 切到新仓库"时才再次调用。

**启动时公告：** "使用 onboard skill 把仓库约定编码进 wyrd 结构。"

---

## 三个产物

onboard 永远输出这三个文件（无则创建，有则更新）：

| 文件 | 角色 | SSOT 边界 |
|------|------|-----------|
| `AGENTS.md` | 铁律 + 路由 + 行为纪律 | 行为约束 SSOT，**不是**项目知识 SSOT |
| `.trae/rules/project_rules.md` | 项目事实 + 命令 | 命令 + 事实 SSOT（lint/typecheck/build/test） |
| `docs/specs/FEATURE-CATALOG.md` | capability 索引 + Components 段 | capability → feature 映射 SSOT |

### 分工原则

- **铁律 / 行为纪律 / 调用纪律** → `AGENTS.md`（已存在则只追加"项目特定红线"，不重写铁律）
- **可执行命令（lint / typecheck / build / test / dev）** → `.trae/rules/project_rules.md`
- **项目事实（框架版本、目录约定、测试框架、CI）** → `.trae/rules/project_rules.md`
- **capability / feature / component 索引** → `docs/specs/FEATURE-CATALOG.md`

### 追加原则

- 若 `AGENTS.md` 已存在（如本次 wyrd 迁移场景），onboard 只追加"项目特定红线"段，不重写铁律
- 若 `project_rules.md` 已存在，onboard 只追加缺失命令/事实，不重写已有内容
- 若 `FEATURE-CATALOG.md` 已存在，onboard 只追加缺失 capability / feature / component 条目

---

## 流程

### Step 0: 判定 SSOT 冲突

onboard 不假设起点是空仓库。先扫描三个 SSOT 是否存在：

```
AGENTS.md
.trae/rules/project_rules.md
docs/specs/FEATURE-CATALOG.md
```

| 场景 | 行动 |
|------|------|
| 三个 SSOT 都不存在 | 走完整流程，从 Step 1 开始创建 |
| 部分存在 | 已存在的不重写，只补缺失部分 |
| 都存在但仍需 onboard | 仅追加"项目特定红线"到 AGENTS.md；其余两个保持现状 |

### Step 1: 仓库扫描

并行收集信息：

1. **README / docs/**：项目自我描述、约定文档
2. **`package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod`**：技术栈、scripts、依赖
3. **CI 配置**（`.github/workflows/`、`.gitlab-ci.yml` 等）：CI 跑的命令 = 事实命令
4. **目录结构**：源码组织方式（src/lib/scripts/test/docs）
5. **lint / formatter 配置**（`.eslintrc*`、`.prettierrc*`、`ruff.toml`、`.rubocop.yml` 等）：实际执行的命令
6. **`tsconfig.json` / `pyrightconfig.json`**：类型检查配置
7. **测试目录与框架**：测试组织方式、测试框架、测试命令
8. **既有 `AGENTS.md` / `CLAUDE.md` / `.cursor/rules/*`**：既有 AI 协作约定
9. **`docs/specs/`**：既有 capability spec / FEATURE-CATALOG

### Step 2: 编码到 SSOT

按"分工原则"把扫描结果写入对应文件。

**`AGENTS.md`（追加"项目特定红线"段，不重写铁律）：**

```markdown
## 项目特定红线

- <项目独有的行为约束，例如：
  - "本仓库不提交 .env*，所有环境变量走 dotenv-vault"
  - "API handler 必须用 tRPC procedure，禁止裸 express handler"
  - "数据库迁移必须用 prisma migrate，禁止手写 SQL 迁移">
```

**`.trae/rules/project_rules.md`（命令 + 事实）：**

```markdown
# Project Rules

## 命令

| 操作 | 命令 |
|------|------|
| lint | `<实际 lint 命令>` |
| typecheck | `<实际 typecheck 命令>` |
| build | `<实际 build 命令>` |
| test | `<实际 test 命令>` |
| test (single file) | `<实际单文件测试命令>` |
| dev | `<实际 dev 命令>` |

## 事实

- **框架**：<框架名 + 版本>
- **语言**：<语言 + 版本>
- **包管理**：<npm/pnpm/yarn/pip/uv/cargo>
- **测试框架**：<测试框架名>
- **CI**：<CI 平台 + 主要 job>
- **目录约定**：
  - 源码：`<path>`
  - 测试：`<path>`
  - 文档：`<path>`
```

**`docs/specs/FEATURE-CATALOG.md`（capability + feature 索引）：**

```markdown
# Feature Catalog

> 由 onboard skill 初始化。后续由 brainstorm skill（新增 capability）和 design-workflow skill（新增 component）维护。

## Capability 索引

| Capability | Spec 文件 | Features |
|------------|----------|----------|
| <capability 名> | `docs/specs/<capability>-spec.md` | <feature 列表> |

## Components

| Component | Feature | Base Component | Status |
|-----------|---------|----------------|--------|
| <ComponentName> | <feature> | <shadcn/Custom> | <Done/In Progress/Planned> |
```

### Step 3: 工作记忆预热

把扫描结果提炼成 3-5 条本 session 必须记住的关键事实，在对话中明示：

> **Onboard 完成。本 session 关键事实：**
> 1. 技术栈：Next.js 15 + React 19 + Tailwind v4 + shadcn/ui
> 2. 测试：Vitest + Playwright
> 3. Lint：`pnpm lint`（ESLint flat config）
> 4. Typecheck：`pnpm typecheck`（tsc --noEmit）
> 5. 目录：源码 `src/`、测试 `tests/`、设计 `docs/designs/`、capability spec `docs/specs/`

---

## 与其他 skill 的衔接

| 衔接 | 触发 | 动作 |
|------|------|------|
| brainstorm | 用户提出新需求 | onboard 完成后，capability spec 已在 FEATURE-CATALOG 索引；brainstorm 直接读 catalog 定位 capability |
| design-workflow | UI 需求 | onboard 已确认 `DESIGN.md` 是否存在；design-workflow V2-1 直接读 DESIGN.md |
| writing-plans | 实现需求 | onboard 已记录命令；writing-plans 在 plan 中引用实际命令 |
| subagent-driven-development | 执行 plan | implementer subagent 通过 `.trae/rules/project_rules.md` 获得命令 |
| doc-ops | 写产物 | onboard 已创建 `docs/specs/` 目录结构；doc-ops 在此结构下写入 |

---

## Red Flags

**NEVER：**
- 重写既有 `AGENTS.md` 铁律段（只追加"项目特定红线"）
- 把可执行命令写入 `AGENTS.md`（命令走 `project_rules.md`）
- 把项目事实写入 `AGENTS.md`（事实走 `project_rules.md`）
- 跳过仓库扫描直接套模板（每个仓库的命令/事实不同）
- 创建空 `FEATURE-CATALOG.md`（至少扫一个 capability 或标注"待 brainstorm 初始化"）

**ALWAYS：**
- 实际执行 lint/typecheck 命令验证可用性（若环境允许）
- 在对话中明示 onboard 产出的 3-5 条关键事实
- 区分"AI 协作约定"（AGENTS.md）和"项目事实"（project_rules.md）
