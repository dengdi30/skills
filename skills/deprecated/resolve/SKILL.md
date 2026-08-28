---
name: resolve
description: "Use when an external blocker (API limit, dependency conflict, permission, environment) prevents progress and the user wants to choose how to unblock — gathers options, surfaces trade-offs, lets the user decide."
---

# Resolve

外部阻塞（API 限额、依赖冲突、权限不足、环境异常）阻碍进度时使用。该 skill 不解决问题本身——它**收集选项、暴露权衡、让用户决策**。

**启动时公告：** "使用 resolve skill 收集解阻塞选项，由用户决策。"

---

## 适用判定

| 场景 | 用 resolve？ | 原因 |
|------|-------------|------|
| GitHub API 限额 | ✅ | 外部不可控，需选策略 |
| 依赖版本冲突 | ✅ | 多解法（升级/降级/锁版本/换库），各有权衡 |
| 权限不足 | ✅ | 需用户决定是否申请权限或换路径 |
| 环境变量缺失 | ✅ | 需用户决定补齐方式 |
| 代码 bug | ❌ | 走 investigate skill |
| 设计方向分歧 | ❌ | 走 brainstorm Scale Gate |
| skill 调用失败 | ❌ | 先 investigate，确认为外部阻塞才转 resolve |

---

## 流程

### Step 1: 描述阻塞

明确陈述：

> **阻塞：** <一句话描述>
> 
> **影响：** <对当前任务的具体影响>
> 
> **触发条件：** <什么操作触发了阻塞>

例：

> **阻塞：** GitHub REST API 返回 403 rate limit exceeded
> 
> **影响：** 无法继续批量读取 issue 列表，PR 模板生成停滞
> 
> **触发条件：** 调用 `gh issue list --repo ...` 第三次时返回 403

### Step 2: 收集选项

列出所有可行解法，每个选项包含：

| 字段 | 说明 |
|------|------|
| 选项名 | 简短标识 |
| 描述 | 怎么做 |
| 优点 | 收益 |
| 缺点 | 代价 / 风险 |
| 前置条件 | 需要什么才能选这个 |
| 不可逆性 | 可逆 / 半可逆 / 不可逆 |

**选项来源：**

1. **官方文档**：阻塞对象（API / 工具 / 平台）的官方建议
2. **社区实践**：Stack Overflow / GitHub Issues / 论坛常见解法
3. **绕过路径**：换工具 / 换接口 / 换时机
4. **降级路径**：减少功能 / 推迟实现 / 手动替代

**最少 2 个、最多 5 个选项。** 少于 2 个说明调研不足；多于 5 个说明没收敛。

### Step 3: 推荐与权衡

在选项中标注**推荐项**（仅 1 个），并说明推荐理由。推荐基于：

- 不可逆性最低
- 前置条件最容易满足
- 缺点影响范围最小
- 与 wyrd 工作流最契合（例如优先选不破坏 TDD 流程的选项）

**不替用户做最终决定**——推荐只是排序，决策权在用户。

### Step 4: 等待用户决策

把选项表呈现给用户：

```
| # | 选项 | 优点 | 缺点 | 不可逆性 | 推荐 |

请选择（1-N），或提供你自己的解法。
```

用户可能：

- 选某个选项 → 进入 Step 5
- 提出自己解法 → 评估可行性后进入 Step 5
- 要求更多信息 → 补充后重新呈现
- 决定推迟 → 记录到 `docs/decisions/` 或对话中，转其他任务

### Step 5: 记录决策

用户决策后：

1. **对话中明示决策**：
   > 决策：选择选项 N（<选项名>）。下一步：<具体行动>。

2. **重要决策记录到文件**（满足任一条件时）：
   - 不可逆性 = 不可逆
   - 影响多个 skill 或后续多个任务
   - 用户明确要求记录

   记录位置：`docs/decisions/<YYYY-MM-DD>-<slug>.md`，内容含：
   - 阻塞描述
   - 考虑过的选项
   - 决策及理由
   - 后续行动项

3. **进入执行**：决策已定，转回原工作流（investigate / writing-plans / subagent-driven-development 等）。

---

## 与其他 skill 的衔接

| 衔接 | 触发 | 动作 |
|------|------|------|
| investigate | 阻塞原因不明 | 先 investigate 确认是外部阻塞，再走 resolve |
| brainstorm | 阻塞涉及方向选择 | 若选项涉及功能取舍，转 brainstorm Scale Gate 公开判定 |
| writing-plans | 决策需写入 plan | resolve 决策记录为 plan 中的前提条件 |
| subagent-driven-development | 决策影响任务拆分 | 决策后更新任务列表 |

---

## Red Flags

**NEVER：**
- 替用户做最终决策（只能推荐）
- 只给 1 个选项（调研不足）
- 给超过 5 个选项（没收敛）
- 隐藏选项的缺点
- 不标注不可逆性
- 决策后不记录（重要决策会丢失上下文）

**ALWAYS：**
- 标注推荐项及理由
- 等待用户显式选择
- 重要决策记录到 `docs/decisions/`
- 决策后明确下一步行动
