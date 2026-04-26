# Concept Language Glossary

This glossary preserves traceability from historical/internal KiU terminology to the v0.8 `学以致用` architecture language.

It is not the main project narrative. New user-facing and reviewer-facing documents should use the v0.8 language first. Historical terms remain valid inside archived reports, release evidence, attribution, and this glossary.

## v0.8 Public Architecture Language

| Public wording | Precise meaning | Use in new docs |
| --- | --- | --- |
| 读准原书 | Preserve source facts, passages, anchors, structure, and provenance. | README, architecture narrative, source-fidelity docs. |
| 提炼判断 | Turn source material into transferable judgment. | README, architecture narrative, generation docs. |
| 生成技能 | Publish bounded skills that help users judge, choose, refuse, act, or recalibrate. | README, skill docs, scorecards. |
| 分流流程 | Keep deterministic procedures as workflows instead of thick skills. | README, workflow docs, boundary reviews. |
| 校准应用 | Add isolated current context, fact checks, caveats, and safety gates. | README, current-fact and application docs. |
| 验证行动价值 | Evaluate whether outputs create action value at a stated evidence level. | README, evaluation guides, release notes. |

## Historical To v0.8 Mapping

| Historical or internal term | v0.8 term | Where it belongs now |
| --- | --- | --- |
| Graphify absorption | 读准原书 maturity / source evidence maturity | Historical evidence and attribution only. |
| graph-backed evidence | 读准原书 / source evidence | Current technical language when evidence structure matters. |
| cangjie methodology absorption | 提炼判断 + 生成技能 discipline | Historical benchmark and attribution only. |
| cangjie core closure | 生成方法就绪度 / production-method readiness | Historical evidence only. |
| RIA-TV++ | 提炼阶段链路 / extraction-to-skill stage chain | Historical implementation detail. |
| triple verification | 证据校验 / evidence verification | Current public language when needed. |
| C-class action value | 验证行动价值 / action-value evaluation | Current public language. |
| A/B/C taxonomy | method integrity, source/fact safety, action value, evidence confidence | Internal metric taxonomy. |
| three-layer review | source/generated/usage review | Internal evidence format. |
| proxy usage | 内部场景校验 / internal scenario check | Evidence tier, not user validation. |
| same-source benchmark | 同书参照对比 / same-book reference comparison | Evidence tier. |
| blind review pack | 盲评包 / blind review pack | Condition-dependent validation artifact. |
| world alignment | 校准应用 / application calibration | Current public language. |
| live fact verification | 当前事实核验 / current-fact check | Application calibration component. |
| use-state arbitration | 应用状态门 / application-state gate | Application calibration component. |
| application readiness | 应用就绪门 / application-readiness gate | Application calibration component. |
| workflow gateway | 流程路由器 / workflow router | Current public language. |
| workflow-vs-agentic boundary | 流程/判断边界 | Current public language. |
| action-skill identity | 行动技能身份 / action skill identity | Current public language. |

## Migration Rule

When a new document must mention a historical term, introduce it once like this:

`读准原书（historically discussed as Graphify absorption in v0.6 evidence）`

After that first mention, continue with the v0.8 term.

Do not rewrite old evidence packs just to change names.

## What Not To Do

- Do not use this glossary as the opening explanation of the project.
- Do not mass-replace historical reports.
- Do not hide external influence or attribution.
- Do not create more branded terms when a plain action phrase works.
