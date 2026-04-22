# 无责复盘

## Identity
```yaml
skill_id: postmortem-blameless
title: 无责复盘
status: under_evaluation
bundle_version: 0.1.0
skill_revision: 1
```

## Contract
```yaml
trigger:
  patterns:
    - incident_review_focuses_on_person
    - causal_chain_is_unclear
  exclusions:
    - incident_is_still_uncontained
intake:
  required:
    - name: incident_summary
      type: text
      description: 事故概述、影响范围与当前争议点。
    - name: timeline
      type: text
      description: 已知的时间线、检测信号和操作序列。
    - name: current_blame_narrative
      type: text
      description: 团队当前把责任归因给个人的说法。
judgment_schema:
  output:
    type: structured
    schema:
      verdict: enum[blameless_reframe_needed,accountability_already_systemic,insufficient_context]
      next_action: enum[reconstruct_timeline,identify_system_factors,retain_current_frame]
      confidence: enum[low,medium,high]
  reasoning_chain_required: true
boundary:
  fails_when:
    - timeline_is_missing
  do_not_fire_when:
    - incident_is_still_uncontained
```

## Rationale
这个技能处理的不是“要不要追责”，而是当复盘已经开始滑向“谁背锅”时，强制把讨论拉回时间线、系统条件和可观测证据。源文强调，真正的 blameless 不是取消责任，而是先问清楚：哪些监控空洞、权限设计、交接断点和默认假设，让错误更容易发生也更难被及时发现。[^anchor:postmortem-blameless-source-core]

如果没有时间线和系统上下文，团队会过度聚焦最后一个执行动作，错过那些更值得修补的检测、runbook、review gate 和 handoff 机制。这个技能因此要求先重建因果链，再区分“个人执行失误”与“系统性诱因”，让复盘输出能够转成真正的工程改进项，而不是情绪性的结案。[^anchor:postmortem-blameless-trace-db]

## Evidence Summary
核心证据一来自 source note 对 blameless 的边界定义：它不是抽掉责任，而是把问题改写为“为什么系统允许错误更容易发生、更难被及时发现”。[^anchor:postmortem-blameless-source-core]

核心证据二来自三个 incident traces 的共同模式：只盯着最后一个执行者，往往会漏掉时间线缺口、runbook 老化和检测机制失效这些更高杠杆的改进点。[^anchor:postmortem-blameless-trace-timeline]

## Relations
```yaml
depends_on: []
delegates_to: []
constrained_by: []
complements:
  - blast-radius-check
  - external:poor-charlies-almanack-v0.1:bias-self-audit
contradicts: []
```

## Usage Summary
Current trace attachments: 3.

- 适合在复盘会已经开始围绕“谁搞砸了”争执时触发，先把时间线和系统因素补齐。
- 如果事故还在进行中，应该先止血，等影响收敛后再进入这个技能。

Representative cases:
- `traces/canonical/blameless-db-index-rollout.yaml`
- `traces/canonical/incident-timeline-gap.yaml`
- `traces/canonical/runbook-ownership-reset.yaml`

## Evaluation Summary
当前 KiU Test 状态：trigger_test=`pass`，fire_test=`pass`，boundary_test=`pass`。

已绑定最小评测集：
- `real_decisions`: passed=1 / total=1, threshold=0.5, status=`pass`
- `synthetic_adversarial`: passed=1 / total=1, threshold=0.5, status=`pass`
- `out_of_distribution`: passed=1 / total=1, threshold=1.0, status=`pass`

关键失败模式：
- 当团队既有明显违规操作、又有系统性诱因时，blameless 容易被误读成“不要谈责任”。
- 如果时间线只剩口述版本，没有检测数据和变更记录，技能容易停留在抽象说教。

详见 `eval/summary.yaml` 与共享 `evaluation/`。

## Revision Summary
当前版本是 engineering bundle 的初版 under-evaluation seed。

本轮补入：
- 建立了时间线优先、系统因素优先的 contract 与双层 anchors。
- 绑定 3 条 canonical traces 和 3 个最小 evaluation cases，保证不是空壳原则条目。

当前待补缺口：
- 继续补充“系统性问题与明显违规操作并存”的灰区样本，压测 accountability 边界。
