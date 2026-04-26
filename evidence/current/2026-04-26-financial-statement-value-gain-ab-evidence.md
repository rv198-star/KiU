# Financial Statement 模块价值增益法 A/B 证据

## 范围

本证据记录 2026-04-26 对外部模块价值增益法做的初步 A/B 试验。

试验只覆盖 Financial Statement 一本书，不覆盖 Shiji、Mao、Poor Charlie、Effective Requirements 等其他样本。因此它不能支持跨书普适性结论。

## 试验路径

- A 组：`/tmp/kiu-v081-financial-value-gain-ab/A`
- B 组：`/tmp/kiu-v081-financial-value-gain-ab/B`
- B2 组：`/tmp/kiu-v081-financial-value-gain-ab/B2`

这些路径是临时试验目录，不是 release artifact。

## 观察结果

A 组是当前基线生成物。

B 组尝试把价值增益信息补入技能文本，但触碰了与结构化评估摘要耦合的 Markdown 展示层。该轮暴露的主要问题不是方法论无效，而是工程用法错误：不能只改展示文本而不同步结构化源数据。

B2 组改为只补充契约、理由和下游使用检查，不改评估摘要。它保持了与 A 组一致的自动评分和 release gate 状态，同时人工阅读上更明确地提示了决策价值、证据价值、交接价值、风险降低价值和执行价值。

## 工程结论

- 模块价值增益法适合放在生成编排、模块审计或优化 backlog 中，而不是用于事后手工 patch 最终 `SKILL.md`。
- 如果改动涉及 contract、usage、evaluation summary 或其他结构化耦合内容，必须同步修改结构化文件并重新生成。
- 当前自动评分没有捕捉到 B2 相比 A 的人工可用性提升，说明该类价值可能需要补充人工 review 或专门指标。
- 当前证据只支持“Financial Statement 单书初测可用”，不支持“对五本书稳定有效”。

## 后续验证

五本齐发应作为下一步验证项，而不是当前证据的隐含前提。

五本验证需要比较：

- A 组：不调用模块价值增益法的当前生成链路。
- B 组：在生成编排或模板层调用模块价值增益法后的生成链路。
- 评估项：自动评分、人工使用价值、来源忠实、结构一致性、边界污染。

在该验证完成前，项目不得把单书试验结果写成通用增益声明。

