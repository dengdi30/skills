---
name: feedback
description: "Use when user explicitly asks to send feedback about wyrd itself — creates a GitHub issue at https://github.com/dengdi30/wyrd with structured frontmatter for triage."
---

# Feedback

用户**显式**要求发送 wyrd 反馈时使用。在 https://github.com/dengdi30/wyrd 创建 issue，带结构化 frontmatter 便于分诊。

非用户主动发起不进入此 skill——避免把"抱怨"自动归档为 issue 噪音。

**启动时公告：** "使用 feedback skill 在 wyrd 仓库创建反馈 issue。"

---

## 前置确认

收集以下信息（用户未提供则主动询问）：

| 字段 | 必填 | 说明 |
|------|------|------|
| 标题 | ✅ | 简明描述，≤80 字符 |
| 类型 | ✅ | `bug` / `enhancement` / `question` / `workflow` |
| 严重度 | 类型=bug 必填 | `critical` / `high` / `medium` / `low` |
| 复现步骤 | 类型=bug 必填 | 编号列表 |
| 期望行为 | ✅ | 用户期望发生什么 |
| 实际行为 | ✅ | 实际发生什么 |
| 涉及 skill | 类型=workflow 必填 | skill 名列表 |
| 环境信息 | ✅ | Trae 版本、OS、模型（如可知） |

---

## Issue 模板

```markdown
---
type: <bug|enhancement|question|workflow>
severity: <critical|high|medium|low>  # 仅 bug
skills: [<skill-name>, ...]            # 仅 workflow
trae_version: <version>
os: <macos|linux|windows>
model: <model-name|unknown>
reporter: <user>
created: <YYYY-MM-DD>
---

# <标题>

## 期望行为
<用户期望>

## 实际行为
<实际发生>

## 复现步骤
1. ...
2. ...
3. ...

## 上下文
<任何有助于分诊的额外信息>
```

---

## 流程

### Step 1: 收集信息

按"前置确认"表收集字段。用户已口头说明的部分直接采纳，未说明的主动询问——**不猜测、不编造**。

### Step 2: 确认内容

把渲染好的 issue 正文（含 frontmatter）展示给用户：

> "即将在 wyrd 仓库创建以下 issue，确认提交？"
> 
> ```markdown
> <完整 issue 正文>
> ```

用户确认后才进入 Step 3。

### Step 3: 创建 Issue

通过 `gh` CLI 创建 issue：

```bash
gh issue create \
  --repo "https://github.com/dengdi30/wyrd" \
  --title "<标题>" \
  --body "<issue 正文>"
```

如果 `gh` 未认证或仓库不可达，降级为：

1. 把 issue 正文保存到 `docs/feedback/<YYYY-MM-DD>-<slug>.md`
2. 告知用户手动提交到 wyrd 仓库
3. 提供仓库链接

### Step 4: 返回链接

issue 创建成功后，把链接返回给用户：

> 反馈已提交：https://github.com/dengdi30/wyrd/issues/<number>

降级场景则返回本地文件路径 + 仓库链接。

---

## Red Flags

**NEVER：**
- 未获用户确认就创建 issue
- 猜测复现步骤或环境信息
- 把一般性抱怨自动转为 issue（必须用户显式要求）
- 修改 issue frontmatter 模板字段

**ALWAYS：**
- 用户确认后才提交
- 标注涉及的具体 skill（便于 workflow 类分诊）
- 提供降级路径（gh 不可用时本地保存）
