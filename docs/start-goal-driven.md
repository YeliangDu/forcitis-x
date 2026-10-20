# 启动目标驱动执行

在新会话打开本仓库后发送：

> 继续 HWK Modern，先读 AGENTS.md、HANDOFF.md 和 docs/goal-driven-plan.md。启动一个主代理和一个执行代理，按 planning/tasks.json 当前active_task推进（现为B02运行优先）。最终目标是完整替代旧应用；严格按原版证据独立验收。维持资产只读，代码只在replica，不提交、不推送。阶段交接时保存所有进度和下一步，遇到外部环境阻塞先记录并推进独立任务。

主代理分派的每轮任务应包含：任务ID、允许修改路径、原版输入与版本、待交付结果、可重跑验收命令、证据路径和完成边界。执行代理不能修改最终验收政策、删除失败案例或将NOT_RUN改为PASS。

提示词不会自行提供守护进程、跨会话恢复、Windows环境或无限预算；本仓库现已提供launchd调度器，按下述方式运行。


## 本机自动续接（2026-10-18获用户授权）

本机launchd任务 `com.yeliang.hwk-modern` 每60秒检查一次；锁保证串行。每轮以两个全新 `codex exec` 会话先执行后独立验收，沿用本机CLI模型配置和ChatGPT登录。会话使用workspace-write、approval_policy=never，权限不足即记录阻塞。不会自动创建当前界面的聊天标签。机器需开机且用户已登录；caffeinate在每轮工作期间防空闲睡眠，不保证合盖或断网继续。

```sh
python3 scripts/scheduler/control.py status
python3 scripts/scheduler/control.py pause
python3 scripts/scheduler/control.py resume
```

pause阻止新轮次，当前轮次可完成；resume在检查阻塞原因并解决后使用。日志、会话ID(JSONL thread.started)、最终报告、状态在 `evidence/scheduler/`；首个静态连通性检查在 `evidence/scheduler/setup/`。配置位于 `~/Library/LaunchAgents/com.yeliang.hwk-modern.plist`。卸载用 `launchctl bootout gui/$(id -u)/com.yeliang.hwk-modern`，应先pause并等待当前周期结束。

任一启动/验收/资产检查错误、明确外部阻塞、连续两轮无实质变更证据、单会话超过90分钟即暂停；90分钟是故障上限，不是五分钟轮询重启。调度器异常退出留下active.json时暂停，先核查其中PID及日志，确认旧进程已退出后清理active.json再resume。最终complete还必须通过现有验收检查器；该检查器不代替专业/使用者业务验收。

调度器本身不修改验收标准。worker不能标记最终PASS；reviewer亲自重跑检查并更新台账。运行会持续使用已有账户额度，遇到认证/配额错误会停机，解决后resume。禁止代理自行修改调度器、扩大权限或递归启动其他会话。

调度器控制回归：`python3 scripts/scheduler/test_runner.py`。这些测试只验证调度控制，不证明HWK业务等价。


## 任务卡与仓库内会话

用户要求每次新会话命名规范并能追踪执行流水。每轮递增一个持久化编号，执行/验收共用编号，如 `HWK-000001-B01-执行｜核查版本和组件`、`HWK-000001-B01-验收｜核查版本和组件`。`evidence/scheduler/cards.json` 为流水索引，各轮 `task-card.json` 记录前后编号、目标、角色、会话UUID、命名回读结果、原生会话文件路径及验收结论。通过已安装CLI的app-server `thread/name/set` 设置原生标题，再用 `thread/read` 回读核验；命名失败会记录，不能声称成功。

用户要求会话保存在本仓库。后续轮次以 `.codex-runtime/` 为CODEX_HOME，原生会话JSONL、会话数据库等落在该目录。认证/配置/技能仅链接现有用户配置，不复制密钥；整个runtime已gitignore。已在全局目录启动的首轮保持运行，按会话UUID把原生JSONL镜像至本仓库；下一次tick同步已结束记录。当前运行中的镜像只是截取至同步时刻，不能称完整终稿。终稿保留SHA-256。

CLI会话标题及本地存储已可验证，但不保证当前桌面聊天列表自动显示这些CLI会话。任务流水以仓库文件为准。仓库搬迁或Node路径变化后需重新核验launchd绝对路径。


## 实时可视化看板

本机URL：`http://127.0.0.1:18743`，浏览器每3秒从仓库刷新。展示建卡、执行、独立验收、本轮结束和阻塞；历史卡保留，点击可看会话UUID、活动及证据。完整阶段状态独立展示，轮次结束不意味着业务PASS。看板只读，不控制开发调度器。

看板服务：`python3 scripts/scheduler/board_service.py install|status|stop|start`。开发调度器与看板服务相互独立：暂停开发仍可看历史，停止看板不停止开发。仅绑定127.0.0.1:18743，不能在其他设备直接访问。launchd配置为 `~/Library/LaunchAgents/com.yeliang.hwk-modern-board.plist`；看板日志为evidence/scheduler/board.stdout及board.stderr。

前端维护：`npm ci --prefix replica/dev-board`；修改后执行该项目的npm test、build、lint。build更新dist后浏览器需重载。看板是工程辅助工具，不是HWK产品应用；业务门槛保持独立。服务读取源文件，不重写或补造业务台账；对旧轮次缺少finished状态时，从真实reviewer-final与会话完成事件恢复显示，并保留原文件。


## 受控并行（2026-10-18）

用户授权后，当前允许主线＋一张隔离取证卡同时执行。主线仍按执行→独立验收循环；旁路由com.yeliang.hwk-modern-parallel每60秒触发一次，单卡锁限制旁路最多一个会话。并行任务范围与输入在planning/parallel-cards.json，冻结副本位于~/Library/Application Support/HWKModern/workspaces/<卡ID>。代码限scripts、证据限evidence；全部原生会话仍在本仓库.codex-runtime，卡片/日志在evidence/scheduler。

独立验收使用read-only sandbox，亲自重跑检查；主控核对输入未改、提交哈希未变、来源路径和软链接限制后，原子导入新的evidence/parallel/<卡ID>。任何失败都保留隔离目录，不覆写已有文件；同ID不可覆盖导入。共享HANDOFF/README/planning及最终验收仍仅主线写。旁路的PASS只通过该切片。

控制命令：
- `python3 scripts/scheduler/control.py parallel-pause`：只暂停旁路后续卡，当前卡可结束。
- `python3 scripts/scheduler/control.py parallel-cancel`：核对本卡PID/命令后终止其进程组，保留工作目录，禁止未审核导入；主线继续。
- `python3 scripts/scheduler/control.py serial`：关闭后续旁路，回退串行，当前卡可正常结束。
- `python3 scripts/scheduler/control.py pause`：全局停止新轮次，两路当前任务可结束。

并行失败时只暂停旁路。恢复前先审查PARALLEL_PAUSED/parallel-state.json及<job>.result.json，解决或撤回失败job后再启用；不自动重复失败卡。当前仅批准evidence-only隔离取证，产品源码并行须另行落实同等隔离/验收/回收机制。看板在同一列可同时看到多张在途卡，区分主线轮次/隔离取证。

控制回归：scripts/scheduler/test_parallel.py（冻结输入、越界、软链接、验收失败、验收期间变更、重复导入拒绝与跨进程流水编号）。独立CLI真实sandbox探针已验证隔离目录可写而主仓库哨兵写入被拒绝，见evidence/scheduler/setup/isolation-probe.*。这些检查不代表HWK业务验收。

并行恢复：`parallel-resume`只在配置/阻塞已处理后恢复；`parallel-retry JOB-ID`只接受失败或取消job，保留原结果并创建新ID，同根job最多一次恢复重试。主线独立验收代理可为已经定位并验证修复的临时工具或报告问题使用此入口；业务失败、输入篡改、授权或环境缺失不能靠自动重试掩盖。队列补充使用 `parallel.py enqueue <reviewed-job.json>`，只接收限定文本快照和evidence-only任务，待办最多两张且拒绝重复范围/未满足前置。


## 目标驱动WBS（2026-10-18）

新轮次先由stages.py选择工作包，写入该卡stage-assignment.json，并以工作包ID/目标命名。主线执行与验收都先读这份合同，按stage-result.schema.json回报该包状态/证据；共享进度由控制器记录。阶段不能因一个函数/局部切片通过而通过，包达到复盘上限后保持未完成并要求具体解除条件。缺合同、依赖不满足、假PASS或未知范围容器均不能派卡。

看板“阶段目标与工作包”可切换十个阶段，展开每包看输入、交付、验收条件、依赖及当前状态。历史卡只保留为证据流水，不计成当前包验收。新并行提案必须填写stage_item_id，并归属当前可执行叶子包。

## 自动阻塞接手（2026-10-18）

launchd遇到自动暂停后，在同一runner锁内自动建立 evidence/scheduler/blockers/<事件哈希>/incident.json，并启动一个全新read-only诊断会话。REA预检先执行；主线active.json存在时不启动。事件按暂停原因和失败轮次去重，自动最多一次；启动前持久记录attempts，崩溃/认证失败也不无限重试。用户主动pause和最终complete不触发诊断。

诊断分类LOCAL_FIX（本地修复）、REPLAN（目标/工作包复盘）、EXTERNAL_INPUT（外部输入），输出来源、有限处理动作、解除条件及用户决策项；只读报告不自动变成修复成功。诊断卡及会话归入既有流水，主线PAUSED保持。查询：`python3 scripts/scheduler/control.py blockers`。诊断失败同样落盘，待前台接手；不会自动通知或唤醒当前聊天。

前台接手先读incident及原始日志，在授权内执行本地修复并复跑相应检查；涉及合同变更/复盘额度/外部输入先记录具体决定。完成解除条件后才运行resume，重新走stages.select及独立目标审查，不直接指定越级包，不覆盖原失败，不删除原业务缺口。当前只实现自动建单和诊断；自动修改与自动恢复尚未实现。

机制回归：`python3 scripts/scheduler/test_blockers.py`。PASS只代表阻塞处理控制行为，不代表HWK产品验收。

## 自动修复与恢复（2026-10-18最新授权，替代仅诊断限制）

自动暂停→一次独立诊断→LOCAL_FIX/REPLAN交自动修复→新read-only会话亲自复核→控制器核对真实命令日志及冻结输入→显式登记有限修订→移除同一事件暂停→下一tick重新目标审查和任务选择。EXTERNAL_INPUT、复核失败、用户主动暂停均不自动恢复。修复者不改共享台账、scheduler或原资产；控制器前后哈希核对受保护文件，发现越权修改保持暂停，需要前台检查，不声称自动回滚。

policy已由本次用户要求启用：每包一次最多追加两轮，原轮数及旧否定记录保留在recoveries；每阶段最多四项登记。它是明确的受审复盘，不是静默加额度。真实方法不可行则不修改合同。合同修改触发新WBS审查，阶段与最终业务门槛不变。登记中断留下recovery-transaction.json，阻止进一步自动恢复，前台依据before-contracts/progress修复。

状态在incident.status/recovery_run、planning/recovery-history.json及各recovery任务卡；本地控制查询blockers。action_required/repair_blocked在看板归阻塞，诊断结束不再冒充处理完成。尚无主动消息通知或聊天唤醒。控制回归：python3 scripts/scheduler/test_recovery.py。

修复被否决的接手补充：每目标最多两次修复尝试，第二次必须消费前次repair_review-final具体反馈；耗尽后自动选择其它合格阻塞包，全无可选则repair_exhausted。业务轮数只在独立放行后追加；失败修复不改轮数。首次真实HWK-000032已否决，不能以其SCAN局部方法声明恢复成功。

现成环境主线：2026-10-18新合同v2经HWK-000036放行B02入口；启动按HANDOFF最新远端进程/任务状态接续，不关停旧工作区用户进程，不执行C:\hwk历史脚本。旧B01串行阻断安排由AGENTS末节及D12明确替代，其义务/否定不删除。

## 最新主线续接方式：按收敛继续

convergence-policy启用后，旧两轮/固定重开次数仅为历史提醒；主线正常是worker→reviewer（含continuation建议）→下一张增量卡。没有明确下一步/无进展才运行一次只读planner，判断换方法、继续某个合法包或确需外部输入。planner不改Goal/完成条件，不给业务PASS。单卡失败不会自动暂停整条主线。真正外部等待/安全问题保留明确解除条件，不重复空转诊断。

后台main采用命令级命名permissions profile使网络和本地文件权限独立配置：workspace执行与read-only独立判断均可访问已授权ECS，隔离parallel工作区保持旧权限。未改用户全局配置/approval_policy。真实read-only网络probe与拒绝写入证据位于evidence/scheduler/setup/convergence/network-probe/。旧“连续两轮即停”和auto-recovery预算由本节及AGENTS最新用户授权取代。
