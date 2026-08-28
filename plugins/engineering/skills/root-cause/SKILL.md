---
name: root-cause
description: 当 issue、Bug、测试失败、生产异常、数据污染或非预期行为的原因尚不明确，需要基于代码、日志、trace、历史和可控实验定位因果机制时使用。输出证据化的根因报告与置信度；不实施修复、不修改需求、不调用其他 skills。
---

# 根因诊断

把问题症状转化为有证据支持的因果解释。定位错误状态第一次产生的位置和机制，而不是在最终爆炸点或最可疑代码处停止。

本 skill 可以独立使用。它只负责诊断，不实施生产修复，不编写持久回归测试，不做代码审查、最终验证、提交或发布。

## 适用边界

适用于：

- 根因未知的 Bug 或 issue；
- 偶发、环境相关或难以稳定复现的问题；
- 多组件、深调用链或异步系统异常；
- 错误参数、状态污染、数据损坏或配置传递问题；
- 测试在本地、CI 或特定环境异常失败；
- 生产事故和依赖行为变化。

根因已经明确、目标行为和修复范围已经确定时，不需要本 skill。

## 定义症状

开始时明确：

```markdown
### Target

- Issue：
- Candidate / Build / Environment：
- First observed：

### Symptom

- Expected：
- Actual：
- Reproduction：
- Stability：必现 / 偶发 / 特定条件 / 暂时无法复现
- Impact：
- Known-good comparison：
```

不能稳定复现时，不强行阻塞。使用日志、trace、metrics、环境差异、历史版本和生产 snapshot 继续缩小条件，并降低最终置信度。

## 因果标准

根因应形成可解释的因果链：

```text
触发条件
→ 缺陷状态
→ 失败机制
→ 可观察症状
```

区分：

- **症状**：最终观察到的错误；
- **触发条件**：使缺陷暴露的输入或环境；
- **促成因素**：放大概率或影响，但单独不足以造成问题；
- **根因**：产生错误状态或破坏系统不变量的机制。

相关性不是因果关系。可行时进行 counterfactual 验证：保持其他条件不变，移除或改变候选原因后，症状应消失或产生可预测变化。

根因可以是多个因素共同作用，也可能位于代码之外，例如配置、数据、依赖、部署、权限或外部服务。

## 选择诊断方法

按问题形态选择一种或组合多种方法，不使用固定层数、组件数或假设数量作为门禁。

### Hypothesis-driven

已有一个或多个合理候选原因时：

1. 根据现有代码和证据形成候选解释。
2. 选择能最大程度区分候选原因的最小检查或实验。
3. 记录证实、削弱或排除该假设的证据。
4. 根据新证据更新候选集合。

不要为了满足模板凑假设。一个强假设可以直接验证；没有合理假设时先收集更多上下文。

### Comparative diagnosis

存在正常对照时，比较：

- 正常请求与失败请求；
- 正常用户与异常用户；
- 本地与 CI；
- 旧版本与新版本；
- 成功路径与失败路径；
- 相似但正常工作的实现。

差异用于缩小范围，不能未经验证直接视为根因。

### Boundary instrumentation

知道系统跨越多个边界但不知道断裂位置，且现有日志不足时：

1. 在关键边界观察输入、输出、配置和环境。
2. 执行一次最小复现或代表性请求。
3. 找到最后一个正常边界和第一个异常边界。
4. 在缩小后的范围内继续形成和验证假设。

### Backward tracing

错误值、状态或路径的来源不明时：

1. 从症状和直接错误位置开始。
2. 找到直接导致错误的状态或操作。
3. 沿调用链和数据流向上追踪调用者与赋值点。
4. 定位错误状态第一次产生的位置。
5. 验证该位置能解释完整症状和触发条件。

不要在症状处增加兜底后就停止追踪。

### Bisection and history

问题与近期变化或特定输入有关时，使用 git history、blame、bisect、依赖锁文件、配置差异或测试二分缩小引入范围。

## 证据来源

按当前问题选择最有区分力的证据：

- 错误日志、stack trace 和异常上下文；
- 失败测试和最小复现；
- 相关代码、调用方和数据流；
- network trace、database state 和 runtime metrics；
- git log、blame、bisect 和版本差异；
- 配置、环境变量、feature flags 和部署元数据；
- 依赖版本和外部服务行为；
- 正常对照与异常样本。

记录原始命令、目标、环境和 artifacts，使结论可复核。不要仅凭“代码看起来可疑”确认根因。

## 临时 Instrumentation

优先使用现有日志、trace 和只读工具。证据仍不足时，可以添加可逆的临时 instrumentation，但必须：

- 使用 `[DIAG]` 或等价明显标记；
- 只采集定位所需信息；
- 不改变业务行为；
- 不记录 secrets、凭据或不必要的个人数据；
- 记录添加位置和运行命令；
- 结束前全部移除；
- 确认候选工作区恢复到调查前状态。

临时复现脚本和数据优先放在临时目录。不得把诊断 instrumentation、临时测试或日志语句留在候选中。

## 调查循环

1. 定义症状、目标和环境。
2. 阅读足以理解问题的代码与系统上下文。
3. 收集已有证据和正常对照。
4. 选择最合适的诊断方法。
5. 执行能区分候选解释的最小检查或实验。
6. 更新因果模型，必要时切换或组合诊断方法。
7. 可行时进行 counterfactual 验证。
8. 清理临时 instrumentation 和数据。
9. 输出根因报告或诚实说明证据不足。

不需要固定阶段数，也不要求所有问题都走完整方法集合。信息充分时尽快收敛；证据不足时不要强行确认。

## 置信度

- `CONFIRMED`：因果链完整，并有复现、counterfactual 或等价强证据支持。
- `PROBABLE`：多项证据一致且替代解释已显著削弱，但缺少最终因果实验。
- `INCONCLUSIVE`：证据不足、环境不可用、无法区分多个解释，或关键输入缺失。

只有 `CONFIRMED` 才能表述为已确认根因。其他状态必须明确保留不确定性。

## 输出

```markdown
## Root Cause Report

### Target

- Issue：
- Candidate / Build / Environment：

### Symptom

- Expected：
- Actual：
- Reproduction：
- Stability：
- Impact：
- First observed：

### Evidence

- ...

### Diagnostic Method

- ...

### Causal Chain

触发条件
→ 缺陷状态
→ 失败机制
→ 可观察症状

### Root Cause

- Location：
- Mechanism：
- Category：code / config / data / dependency / environment / external / requirement
- Confidence：CONFIRMED / PROBABLE / INCONCLUSIVE

### Ruled-out Alternatives

- 仅列真正验证过的重要替代解释及其排除证据。

### Detection Gap

- 为什么现有测试、监控或约束没有发现该问题。

### Reproduction Artifact

- 命令、临时脚本、输入或步骤：

### Invariant to Restore

- 描述必须重新成立的行为或系统不变量，不描述具体修复方案。

### Temporary Instrumentation

- Added：
- Removed：
- Workspace restored：yes / no
```

输出可以直接呈现在对话中；只有用户要求持久化时才写入文件。

## 完成条件

- 症状和验证对象明确；
- 结论有可复核证据；
- 因果链与影响范围一致；
- 置信度没有夸大；
- 重要替代解释已按需要验证；
- 临时 instrumentation 和数据已清理；
- 工作区恢复到调查前状态。

## 边界

不要：

- 修改生产逻辑或实施修复；
- 编写或保留持久回归测试；
- 修改需求、spec、Plan 或验收标准；
- 输出具体修复方案；
- 调用其他 skill；
- commit、push、创建或更新 Pull Request；
- 因为调查耗时而把第一个可疑点宣布为根因；
- 把无法复现、环境阻塞或多个解释并存包装成确定结论。

只返回证据化诊断结果，由调用者决定下一步。
