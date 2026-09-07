---
name: review
description: 当需要对工作区变更、commit、分支、PR 或 diff 进行独立代码审查时使用；输出有证据支持的审查结论，不修改候选。
---

# 独立代码审查

使用上下文干净的 fresh subagent，对明确的候选变更进行一次只读、证据驱动的对抗性审查。

本 skill 可以独立使用。它不要求需求文档、Plan、实现报告或测试证据存在，也不依赖其他 skills 或自动发起后续流程。

## 审查目标

支持审查：

- 当前工作区变更；
- staged changes；
- 单个 commit；
- commit range；
- branch diff；
- Pull Request；
- 用户直接提供的 patch 或 diff。

用户只说“审查当前修改”时，默认审查完整工作区候选，包括 staged、unstaged，以及属于本次变更的 untracked 文件。

如果无法区分本次变更与无关工作区修改，或审查范围存在会实质改变结论的歧义，先请求最小澄清。

## 可选上下文

存在时使用以下信息增强审查，不存在时仍完成代码审查：

- 用户需求、issue 或 spec；
- Plan 或验收标准；
- 技术和兼容性约束；
- 测试命令与结果；
- CI 报告；
- candidate SHA 或 diff hash。

有需求或验收标准时检查规格符合性；没有时，仍检查代码自身的正确性、安全性、兼容性、回归风险和测试质量。

只接收客观 artifacts。不要把实现者的推理过程、辩护、预期 verdict 或主会话怀疑的具体问题传给 reviewer。

## 候选快照

审查前确定：

```text
base revision
candidate 标识
changed files
完整 diff
```

candidate 标识可以是 commit SHA、base/head SHA、PR head、diff hash 或等价稳定标识。

完整 diff 必须覆盖审查范围内的生产代码、测试、配置、迁移和新增文件，不能只包含可见的 diff hunks 或默认 `git diff` 输出。

Verdict 只对该 candidate 有效。审查期间候选发生变化时，不签发有效 verdict；报告候选已变化并停止。

## 上下文隔离

优先创建不继承当前对话的 fresh subagent。传给 reviewer 的内容仅包括：

- 审查目标；
- candidate 信息；
- 完整 diff 和 changed files；
- 可选需求与验收标准；
- 可选客观测试证据；
- 必要的仓库级约束。

Reviewer 可以只读检查相关源码、调用方、类型、配置和仓库既有模式，不应被限制为只看 diff hunks。

如果运行环境不支持 fresh subagent，明确说明无法保证上下文独立。只有用户接受时，才进行同上下文的降级审查。

## 对抗性审查

Reviewer 的目标是尝试证伪候选，而不是最大化 findings 数量。

按相关性检查：

1. 明确的功能错误；
2. 正常、异常和边界路径；
3. 安全、权限和敏感数据；
4. 数据丢失、事务和一致性；
5. 兼容性和调用方破坏；
6. 并发、幂等、重试和状态转换；
7. 具有实际影响的性能问题；
8. 测试假阳性、实现细节耦合和关键覆盖缺口；
9. 存在需求输入时的需求与验收标准符合性。

不要报告：

- 纯个人编码偏好；
- formatter 或 linter 可以处理的样式问题；
- 与候选无关的历史问题；
- 没有具体失败场景的理论风险；
- 对已有技术选择的无证据争论；
- 推测性重构或过度工程建议。

对抗性不意味着必须发现问题。没有具体证据支持的问题不应形成 finding。

## Findings

只使用两级 findings。两级都必须有具体证据和现实影响；是否阻塞取决于问题的严重程度。

### Blocking

以下问题阻塞候选：

- 功能错误；
- 违反明确需求、验收标准或约束；
- 安全漏洞或数据丢失；
- 兼容性破坏；
- 可信的并发、事务或状态错误；
- 关键测试产生假阳性；
- 核心行为缺少必要证据。

### Non-blocking

以下问题不阻塞候选：

- 有具体证据和现实影响，但严重程度不足以阻塞候选的问题。

纯命名偏好、假想优化和没有实际场景的维护风险不形成 finding，也不为填充 Non-blocking 栏目添加建议。

任一 Blocking finding 存在时 Verdict 为 `BLOCK`；否则为 `APPROVE`。

### Finding 格式

```markdown
### [Blocking] <问题标题>

- 位置：path/to/file.ts:42
- 关联：<需求、约束或验收标准；没有时省略>
- 失败场景：<问题在什么条件下发生>
- 证据：<相关代码或行为>
- 影响：<对用户、数据或系统的后果>
```

每条 Blocking finding 必须包含精确位置、具体失败场景、代码证据和实际影响。低置信度怀疑不能作为 Blocking finding。

## 命令边界

Reviewer 可以读取已有测试证据，也可以为验证一个具体怀疑运行小范围、只读的检查命令。

Reviewer 不负责运行完整测试套件、建立测试环境或执行系统级验收。命令结果只能支持审查 finding，不能替代独立的动态验证结论。

## 输出

```markdown
## Review

- Candidate：<SHA / diff hash / PR head>
- Verdict：APPROVE / BLOCK

### Blocking findings

...

### Non-blocking findings

...
```

没有问题时明确输出：

```markdown
Verdict: APPROVE

未发现有具体证据支持的 Blocking findings。
```

不要为了体现对抗性而编造 findings。

## 边界

以下限制适用于本 skill 的审查职责，不限制外层执行者继续用户已授权的其他阶段。

不要：

- 修改生产代码、测试或其他候选文件；
- 修改需求、Plan 或验收标准；
- 自动修复 findings；
- commit、push 或更新 Pull Request；
- 自动调用或要求其他 skill；
- 决定调用者后续的工作流；
- 替用户接受风险或签发人工验收结论。

返回绑定 candidate 的审查结论。本 skill 的职责到此结束，不自动启动或要求后续流程。用户已授权复合任务时，外层执行者继续剩余工作；用户仅要求本阶段时，交付结果后结束任务。
