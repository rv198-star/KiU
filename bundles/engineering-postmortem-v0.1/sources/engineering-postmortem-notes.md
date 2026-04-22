# Engineering Postmortem Notes

## Blameless Postmortem
事后复盘的第一原则不是找替罪羊，而是先还原时间线、系统条件和决策压力。
如果没有时间线，团队只会抓住最后一个操作人，把系统里早就存在的告警缺口、权限设计和交接断层都忽略掉。
真正的 blameless 不是取消责任，而是把问题改写成“为什么这个系统让错误更容易发生、也更难被及时发现”。
复盘结论必须落到监控、runbook、review gate 和交接机制，否则复盘只是在情绪层面结束。

## Blast Radius And Reversibility
高风险变更上线前必须先说清 blast radius：会影响哪些用户、哪些数据、哪些依赖以及最坏结果是什么。
如果 blast radius 说不清，就不能把发布假设成“出了问题再看”；必须先设计 feature flag、canary、分批发布或人工 holdback。
回滚路径和可逆性要提前写明，特别是数据迁移、计费变更、权限策略这类不可逆步骤。
越不可逆的步骤，越需要更强的 review、预演和 abort condition。
把 scope、safeguard、detection、rollback 四件事在变更前写清楚，也能让事后复盘直接复用同一套框架。
