# Project Architecture Narrative

KiU (`学以致用`) turns source knowledge into executable action capacity.

It is not a summary engine, quote database, translator, or generic RAG notebook. Those systems help users retrieve or restate knowledge. KiU tries to answer a harder question: when should knowledge change what a user notices, judges, chooses, refuses, does, or recalibrates?

## The Short Version

```text
Book -> Read Accurately -> Distill Judgment -> Skill or Workflow -> Calibrate Use -> Verify Action Value
```

In Chinese public language:

```text
原书 -> 读准原书 -> 提炼判断 -> 生成技能 / 分流流程 -> 校准应用 -> 验证行动价值
```

The project keeps these steps separate because each step has a different failure mode.

## 1. 读准原书

KiU first preserves what the source says: passages, claims, structure, anchors, and provenance. This step can support summaries and lookup, but it is not the final product.

Failure to avoid: treating book material as action guidance before it carries action-ready judgment.

## 2. 提炼判断

KiU then asks what transferable judgment the source supports. This is where usable thinking separates from notes, quotes, and chapter summaries.

The key rule is: `技能不是摘要`.

Failure to avoid: compressing a book into fluent prose that does not help a user decide anything.

## 3. 生成技能

KiU publishes a skill only when the artifact can help a user notice signals, define problems, judge tradeoffs, choose actions, refuse misuse, or recalibrate. A published skill must know when it should fire and when it should not.

The public goal is: `学到最后要能用`.

Failure to avoid: publishing chapter headings, exercises, concepts, or source containers as if they were installable skills.

## 4. 分流流程

Some useful source material is deterministic procedure. KiU keeps that material as workflow output instead of pretending it is a judgment skill.

Failure to avoid: inflating a checklist into a thick skill, or collapsing a judgment-rich skill into a checklist.

## 5. 校准应用

Application context can matter. Current facts, market conditions, user constraints, or risk level may change whether a skill should be applied.

The boundary principle is: `用而不染`. Application context may gate or caveat use, but it must not rewrite the source-derived skill.

Failure to avoid: blending current-world assumptions into a source-faithful skill so that users can no longer tell what came from the book.

## 6. 验证行动价值

KiU evaluates whether generated outputs help users in four action layers:

- Discover signals.
- Define problems.
- Resolve actions.
- Calibrate feedback.

Evidence levels remain explicit. Internal scenario checks are not real-user validation, and same-book reference comparisons are not external preference proof.

Failure to avoid: using internal scores to claim external validation.

## Why This Architecture Exists

Without separation, a system tends to confuse five things: what the book said, what the book implies, what action a user should take, which deterministic workflow applies, and whether current facts make the action safe.

KiU keeps those apart so that knowledge can be used without losing its source boundary.

## One-Sentence Description

KiU reads a source accurately, distills action-ready judgment, publishes bounded skills, routes deterministic workflows separately, calibrates application without polluting the source, and verifies whether the result creates action value at an explicit evidence level.
