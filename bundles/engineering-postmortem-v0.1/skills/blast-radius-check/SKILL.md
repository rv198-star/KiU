# 影响面检查

## Identity
```yaml
skill_id: blast-radius-check
title: 影响面检查
status: under_evaluation
bundle_version: 0.1.0
skill_revision: 1
```

## Contract
```yaml
trigger:
  patterns:
    - risky_change_scope_is_unclear
    - rollback_path_is_unclear
    - reversibility_is_ignored
  exclusions:
    - change_is_fully_reversible_and_low_impact
intake:
  required:
    - name: change_summary
      type: text
      description: 拟上线变更的内容、目标与关键依赖。
    - name: affected_surface
      type: text
      description: 受影响用户、数据、服务、运营流程和最坏后果。
    - name: rollback_plan
      type: text
      description: 回滚路径、abort condition 与可逆性说明。
judgment_schema:
  output:
    type: structured
    schema:
      verdict: enum[blast_radius_unknown,blast_radius_bounded,insufficient_context]
      next_action: enum[bound_scope_before_release,proceed_with_guardrails,collect_more_context]
      confidence: enum[low,medium,high]
  reasoning_chain_required: true
boundary:
  fails_when:
    - affected_surface_is_unknown
  do_not_fire_when:
    - change_is_fully_reversible_and_low_impact
```

## Rationale
这个技能的目标不是把所有上线都变成重流程，而是在高风险变更进入执行前，强制团队先说清 blast radius、rollback path 和 reversibility。源文明确指出，如果连受影响用户、依赖系统、数据后果和最坏结果都说不清，就不能把发布假设成“出了问题再看”，而应该先补齐 feature flag、canary、分批发布或人工 holdback 等保护措施。[^anchor:blast-radius-check-source-core]

它和事后复盘形成前后呼应：复盘要回答“为什么问题会扩散”，而 blast-radius-check 要在变更前先回答“如果出事，会扩散到哪里、如何止损、哪些步骤根本不可逆”。特别是数据迁移、计费改写、权限策略这类步骤，只要 reversibility 没被明确写出来，就不能把风险控制交给模糊的乐观预期。[^anchor:blast-radius-check-trace-migration]

## Evidence Summary
核心证据一来自 source note 对高风险变更的要求：scope、safeguard、detection、rollback 四件事必须在变更前写清楚，否则 blast radius 只是口头假设。[^anchor:blast-radius-check-source-core]

核心证据二来自三个 release traces：当团队先补齐 feature flag、canary、holdback 和 abort condition 时，影响面会被切成可观测、可停止的小单元，而不是直接暴露给全量用户。[^anchor:blast-radius-check-trace-flag]

## Relations
```yaml
depends_on: []
delegates_to: []
constrained_by:
  - external:poor-charlies-almanack-v0.1:margin-of-safety-sizing
complements:
  - postmortem-blameless
contradicts: []
```

## Usage Summary
Current trace attachments: 3.

- 适合在变更要进入执行，但团队对影响面、回滚和可逆性只有模糊口头共识时触发。
- 如果只是低影响且可即时回退的小改动，这个技能应该主动退出，避免制造假流程。

Representative cases:
- `traces/canonical/blast-radius-flag-guard.yaml`
- `traces/canonical/phased-rollout-holdback.yaml`
- `traces/canonical/irreversible-migration-precheck.yaml`

## Evaluation Summary
当前 KiU Test 状态：trigger_test=`pass`，fire_test=`pass`，boundary_test=`pass`。

已绑定最小评测集：
- `real_decisions`: passed=1 / total=1, threshold=0.5, status=`pass`
- `synthetic_adversarial`: passed=1 / total=1, threshold=0.5, status=`pass`
- `out_of_distribution`: passed=1 / total=1, threshold=1.0, status=`pass`

关键失败模式：
- 团队可能把“有回滚按钮”误当成 blast radius 已被控制，而忽略数据与外部依赖的不可逆后果。
- 当 scope 说明过于乐观时，技能容易低估慢性扩散或下游兼容性风险。

详见 `eval/summary.yaml` 与共享 `evaluation/`。

## Revision Summary
当前版本是 engineering bundle 的初版 under-evaluation seed。

本轮补入：
- 建立了 blast radius、rollback、reversibility 三件套的 judgment contract 与双层 anchors。
- 绑定 3 条 canonical release traces 和 3 个最小 evaluation cases，保证变更前判断有证据底座。

当前待补缺口：
- 继续补充“局部可回退但全链路不可逆”的混合变更样本，提升边界判断的精度。
