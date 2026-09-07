# 完整根因报告模板

需要完整、结构化报告时使用；只列真正验证过的替代解释，不为填充模板推测证据。

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
