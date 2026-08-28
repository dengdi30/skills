# Skills

## 仓库契约

- 本仓库维护一组彼此独立、可按需组合的 Agent Skills。
- 活跃的第一方 skill 位于 `skills/engineering/<skill>/`。
- 活跃的第三方 skill 位于 `third-party/<skill>/`。
- 历史 skill 归档于 `skills/deprecated/`，不属于当前能力集。
- 每个活跃 skill 的 `SKILL.md` 是其用途、输入输出、执行规则与边界的事实来源。
- 本文件不规定固定开发流程，也不要求一个 skill 完成后自动调用另一个 skill。

## Skill 选择与使用

- 用户或开发者决定使用哪些 skill、调用顺序以及组合方式。
- 用户显式指定 skill 时，必须使用该 skill。
- 用户未显式指定时，仅在 skill 的描述直接匹配当前主要任务，且能提供实质性、非显然的指导时使用。
- 只选择完成当前任务所需的最小 skill 集；多个 skill 同时适用时，先说明各自承担的职责。
- 一旦决定使用某个 skill，必须在执行任务动作前完整读取其 `SKILL.md`，并遵守其中的边界。
- 从 `skills/engineering/*/SKILL.md` 发现第一方 skill。
- `third-party/baoyu-design/SKILL.md` 是活跃的外部设计 skill。使用时先完整读取入口文件，再按当前任务需要加载其引用资源。
- 不得隐式使用 `skills/deprecated/` 中的内容；只有用户明确要求审计、比较、迁移或恢复历史能力时才可读取。

## 编辑约束

- 保持第一方 skill 可独立使用，不得增加 skill 间的强制调用、固定交接或硬依赖。
- Skill 可以接收计划、需求、差异、测试证据、审查报告等通用产物，但不得要求这些产物必须由另一个指定 skill 生成。
- 新增或修改第一方 skill 时，保持目录结构为 `skills/engineering/<skill>/`。
- 上游原样引入的 skill 放在 `third-party/<skill>/`；未经用户明确要求，不修改其 vendored 内容。
- 第三方来源、固定版本、许可证、引入日期与本地修改状态记录在 vendored 目录之外。
- `skills/deprecated/` 视为只读归档；若要恢复其中能力，应迁移为新的活跃 skill，而不是直接继续维护归档副本。
- 遵守用户给定的任务范围。只有歧义会实质改变行为、范围、授权或不可逆决策时，才请求澄清。
- 不为当前任务额外引入未被请求的流程、文档、测试、门禁或自动化。

## 验证要求

修改第一方 skill 时，至少检查：

- `SKILL.md` 的 YAML frontmatter 完整且可解析。
- `name` 与目录名一致，`description` 能准确说明触发条件。
- 相对链接和引用资源可解析。
- 指令明确描述职责与边界，没有引入对其他 skill 的强依赖。
- 最终差异只包含当前任务需要的改动。

更新第三方 skill 时，至少检查：

- 固定并记录明确的上游 commit。
- vendored 内容与该 commit 对应的上游目录一致。
- 保留并记录许可证与来源信息。
- 更新 provenance 记录，并说明是否存在本地修改。
- 如未执行第三方脚本或动态验证，必须明确说明，不得将静态比对描述为行为验证。

只有实际运行了具有代表性的验证，才能声称运行时行为已通过验证。
