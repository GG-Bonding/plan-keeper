<div align="center">

# Plan Keeper

**每个开发任务一份计划，审批、更新、恢复都在同一个文件里。**

一个本地优先的 Agent Skill，用一份由 Git 忽略的 Markdown 文件维护可评审的技术方案、关键决策、审批与验收记录。

[快速开始](#快速开始) · [工作流程](#工作流程) · [参与贡献](#参与贡献) · [English](README.md)

</div>

## 为什么用 Plan Keeper？

开发任务跨越多个会话时，新的会话需要知道你批准了什么、已经改了什么、实际跑过哪些检查。Plan Keeper 将这些信息保存在当前 Git 工作区的 `.ai/plans/<任务 ID>.md`，文件路径在整个任务期间保持固定。

- **先审阅，再实施。** 在编码前查看验收标准、变更范围、实施步骤、风险和验证方案。
- **范围变化有记录。** 有实质变更时，在原文件中升级计划版本，并重新审批。
- **换会话能接着做。** Agent 对照计划、当前分支、HEAD 和工作区状态，确认从哪里继续。
- **计划留在本地。** 用 Git 本地排除规则防止计划进入普通暂存流程，无需修改项目共享的 `.gitignore`。

## 技术方案格式

[UTF-8 Markdown 模板](assets/implementation-plan.md)以评审摘要开篇，记录范围、现状依据和关键取舍。关键行为可用 Mermaid 流程图或时序图展示，再用短代码差异和验收表对应到同一项改动。多模块需求可链接[模块方案](assets/module-record.md)。

开发前只建总 Plan。项目或模块需要单独评审时再建文档。开发和测试完成后，进入上线准备时才生成[发布与排查手册](assets/release-runbook.md)，有配置变更才附[带注释的 YAML](assets/release-config.example.yaml)。每份文件只保留当前阶段需要的决策、验证和操作。

## 快速开始

需要 Git 和 Python 3.7 或更高版本。辅助脚本只使用 Python 标准库。

### 1. 安装 Skill

在 Codex 的用户技能目录中安装一次，即可在多个项目中使用。

```sh
mkdir -p ~/.agents/skills
git clone https://github.com/GG-Bonding/plan-keeper.git ~/.agents/skills/plan-keeper
```

如果只在某个项目里使用，把技能目录放到该项目的 `.agents/skills/` 下。其他支持 Agent Skills 的客户端请使用各自的技能目录和调用方式。

### 2. 创建计划并审批

在 Codex 中打开一个 Git 项目，试试这条指令。

> 用 $plan-keeper 给 issue 421 的 Redis 超时修复制定实施计划，任务 ID 用 `issue-421`，完成后给我审批。

查看 `.ai/plans/issue-421.md`，确认当前版本后明确批准。

> 批准 `.ai/plans/issue-421.md` 的第 1 版。请按批准范围实施，并记录验证结果。

### 3. 在新会话继续

打开原来的 Git 工作区，让 Codex 恢复任务。

> 用 $plan-keeper 从 `.ai/plans/issue-421.md` 恢复这个任务。

## 工作流程

| 阶段 | 计划记录什么 |
| --- | --- |
| `DRAFT` 草稿 | 当前行为、验收标准、范围、实施步骤和拟执行的检查。 |
| `APPROVED` → `IN_PROGRESS` 审批与实施 | 当前版本的审批、已完成步骤和执行决策。 |
| `BLOCKED` 或 `REPLANNING` 阻塞与调整 | 阻塞原因或实质变更，以及下一步动作。调整范围后需要重新审批。 |
| `VERIFYING` → `COMPLETED` 验证与完成 | 实际执行的命令、观察到的结果、待验证项和交付链接。 |

[技能说明](SKILL.md)定义审批和执行流程，[实施计划模板](assets/implementation-plan.md)定义记录结构。辅助脚本提供 `init <task-id>` 和 `check <task-id>`，用于创建计划和检查 Git 排除状态。

## 为已实现的代码补录计划

代码已经实现时，仍然使用同一条计划路径。Agent 根据现有代码、相关提交和能找到的测试证据，分别记录已实现的行为、已验证的结果和剩余工作。只补文档时可以直接记录，后续要改代码时，再审批拟变更的范围。

> 用 $plan-keeper 根据现有 SDK 和业务交互代码补录 issue 421，写清已验证的内容和剩余工作。

## 一个需求拆成多份模块文档

保留一份总计划，并从中链接各模块的文档。

```text
.ai/plans/
├── issue-421.md
└── issue-421/
    ├── sdk.md
    └── business-interaction.md
```

总计划记录共同范围、审批和整体验收条件。模块文档各自记录最新进展和验证结果，想看 SDK 或业务交互的细节时可以直接打开对应文档。恢复任务时先读总计划，再按链接进入模块。模块文档与总计划遵循同样的 Git 本地排除规则。详见[模块记录模板](assets/module-record.md)。

## 本地存储与 Git

- 计划留在创建它的工作区。不同的克隆或 Git worktree 各自保存计划。
- 辅助脚本按需向 Git 解析出的 `info/exclude` 添加 `/.ai/plans/`，检查目标路径是否被忽略，并在发现计划已被跟踪或暂存时停止。
- 项目共享的忽略规则可能覆盖本地规则，`git add -f` 也能绕过忽略规则。如果本地规则被移除，在项目根目录运行 `git rev-parse --git-path info/exclude` 找到排除文件，恢复规则后再运行辅助脚本的 `check`。
- 审批和范围检查由 Agent 按技能说明执行。辅助脚本负责检查本地路径和 Git 状态。

## 参与贡献

欢迎[提交 Issue](https://github.com/GG-Bonding/plan-keeper/issues/new)，说明预期行为、实际结果和最小复现方式。公开的 Issue 和 PR 请使用脱敏示例。

提交改动前，在仓库根目录运行测试。

```sh
python3 -B -m unittest discover -s tests -v
```

测试在临时 Git 仓库中运行，覆盖重复计划、会话恢复、忽略规则覆盖、强制暂存和关联 worktree。
