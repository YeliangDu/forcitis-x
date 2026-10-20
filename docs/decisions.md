# 决定与未决事项

- D01：新工作区为 `/Users/yeliang/Projects/YeliangDu/hwk-modern`，从安装资产起步。原工作区保留，新代码统一 `replica/`。
- D02：前端保留 React + TypeScript + Vite，lint使用oxlint；尚未创建应用工程。
- D03：桌面宿主、数值内核、持久化未选。候选评估应覆盖桌面/打印/图形/文件集成、双精度运算顺序与运行库差异、数据无损往返和部署。用一条真实工程链做实验后写ADR，不能仅因某语言流行而选择。
- D04：以新仓库用户完整替代要求作为目标，包含`.cwx`文件往返。历史“仅导入”不自动沿用；若后来明确改范围，登记用户决定并重新评估替代目标。
- D05：包目录标记1220，实际PE资源及运行版本待查；历史1209与1220差异只作为核验线索，不当成已确认的新基线。
- D06：不承诺100/300小时完成。先以门窗端到端试点测得吞吐、主要未知及样本成本，再提供估算区间。

- D07（2026-10-18用户）：REA使用最新稳定版。现场升级6.4.0→6.7.0，CLI/新MCP身份核验通过；配套skill42、207个MCP工具。本次旧会话所持6.4.0连接不再用于新分析，旧证据保留来源版本。每轮版本门禁见scripts/scheduler/check_rea.py。
- D08（2026-10-18用户）：旧系统命名在第一轮跑通后标准化再替代。当前仅做原名/含义/证据/歧义/兼容边界准备；第一轮跑通的具体验收范围与正式标准名尚未决定，不提前批量改名。

- D09（2026-10-18用户）：后续准备整体重构软件架构和求解器；授权当前轮次做前置取证。增量清单为planning/refactoring-preparation.json；先有行为契约、依赖与案例，再评估接口和选型。未决定具体目标架构、求解器语言或算法；不改变D03及现有业务验收标准。

- D10（2026-10-18用户）：允许风险可验证、可回收的并行。初始1主线＋1隔离取证卡；冻结输入、OS写隔离、SHA-256、只读独立验收及全新目录原子导入，parent验收不自动通过。共享台账保持单写；可取消单卡或退回串行。

- D11（2026-10-18用户）：必要时允许在阿里云建立测试环境。先只读核查可复用资源，再按原版需求配置，保留费用、资源ID和回收方式。当前未创建云资源，Windows环境状态仍待验证，软件许可与原版实际运行不因此自动通过。

- D12（2026-10-18用户）：无人值守首要解决整体Goal→阶段目标→工作包目标的WBS分解。采用stage-contracts/stage-progress及强制派卡门禁；B01收敛四包，历史卡不冒充工作包通过。未知范围容器须由实际库存分解后执行，卡片/阶段额度触发复盘而非降低完成标准。

- D12（2026-10-18用户授权运行并重编排）：复用ECS i-bp1cb2hxk0td5z149z54（cn-hangzhou-k），已安装原版exe与冻结包哈希匹配。主线先B02现成环境真实运行，入口为B01-01独立通过及冻结绑定证据；B01其余缺口/否定/轮数保留至最终闭合，不阻断现成运行取证。R01仍依赖E01+B01并明确干净安装卸载，当前未通过。隔离运行只写C:\hwk-modern\本轮目录与本轮任务，不执行历史脚本或修改服务端。

- D13（2026-10-18用户授权「配置rea + Ghidra」）：REA 6.7.0 的 ghidra provider 要求 Ghidra 12.1.x。官方 `ghidra_12.1.4_PUBLIC_20260921.zip`（SHA-256 `ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db`）只含 `os/linux_x86_64` 与 `os/win_x86_64` 原生反编译器，**不含 macOS**，故 native_decompiler 检查失败与安装路径无关。取舍：不换 provider（Hopper 付费、IDA 需许可、kuna 未安装），改用发行包自带的 C++ 源码在本机 clang++ `-std=c++17 -arch arm64` 构建 `ghidra_opt`→`Ghidra/Features/Decompiler/os/mac_arm_64/decompile` 与 `sleigh_opt`→`sleigh`；构建时须分两次 make（同时给 `ghidra_opt sleigh_opt` 会使 `MAKECMDGOALS` 落到 `com_opt/depend`，把需要 GNU BFD 的 `analyzesigs.cc`/`loadimage_bfd.cc`/`codedata.cc` 一并编译而在 macOS 缺 `bfd.h` 处失败）。验证：产物为 `Mach-O 64-bit executable arm64`，`rea doctor --provider ghidra` 9/9 通过，其中 `ghidra-native_decompiler` 报 `reports mach-o arm64`。安装位置 `~/tools/ghidra_12.1.4_PUBLIC`（890MB，不含在仓库内）；`GHIDRA_INSTALL_DIR` 经 `~/.zshrc` 标记块与 `launchctl setenv` 提供，launchd 侧重启后需重跑 setenv，永久化须改 plist（未改调度器）。注意 pi 后台任务不继承 `launchctl setenv` 之后的变量，需显式 export。边界：反编译产物只作静态行为证据，属「Ghidra 反编译」等级，不等于原版运行结果；不改变 D03 的架构/求解器选型结论。验证补充：真实反编译已跑通，`?Solve@HWKCalc_GlassDisp@@UEAAHXZ` 与 `?Serialize@HWKCalc_GlassDisp@@MEAAXAEAVCbArchive@@@Z` 各返回 Ghidra 12.1.4 伪代码（evidence_id `ev_d7c5777…4d55eb`、`ev_67bebb4…20cf95`），单函数耗时约 76 秒且未因 `--snapshot` 复用而缩短；原始 Evidence 存 `migration_workspace/raw/*.rea.json`。另实测发现同址别名：`0x89be0` 同时挂着 GlassArea/GlassDisp/GlassStrength/GlassWeight 四个 `Serialize` 导出，按名字取函数不等于语义归属唯一，取证包须显式标注别名。

- D14（2026-10-20用户确认）：图形采用**参数化单一真源 + 派生计算模型**，不做通用 CAD/BRep 内核，不做 AutoCAD 插件（`.arx/.grx/.zrx`）兼容；3D 仅保留"查看"可能，不进 V1 范围。依据：旧系统图形能力分散在 CAD 插件（`HWUtil*.arx` 含 `ACAD.exe`）与 `HWKCAD.dll`/`HWKGraphModelLib.dll`（图元-关系-模型-FE 桥）三层，计算链只需板/壳/杆。
- D15（2026-10-20用户确认）：**结果图形与计算分离**——计算引擎只产出"图形规格数据 + 模板 id"，渲染独立成层（确定性、无随机、无时钟）；图形数据与数值同源。
- D16（2026-10-20用户确认）：计算书 = **数值 + 文本要素 + 图形** 三元组；PDF 内嵌 RulePack 指纹、引擎版本、figure hash、审计号；签章层可后置插入且不重排版。计算书为安全证据，必须可由快照+指纹重生成。
- D17（2026-10-20用户确认）：图形互操作分级推进 **L1 参照导入 → L2 识别导入 → L3 导出（PDF/DXF，DWG 待定）**；DWG 写入是否采购 SDK 由下游需求决定，不阻塞 MVP。
- D18（2026-10-20用户确认）：**产品规格 V1 冻结**（`docs/product-spec-v1.md`）：形态=中心化薄客户端（无离线，域账号 SSO，100 在线/20 并发重算）；正确性以规范为准 + 旧系统差异台账 + 黄金回归；数据主干 Project/Scheme/Geometry/Member/Section/CalcCase/ResultBundle/RulePack/Deviation/Figure/AuditEvent；边界外含 `.cwx` 写回、旧 UI 复刻、加密狗复刻、离线。
- D19（2026-10-20用户确认）：**PoC/MVP 定义与关卡**（`docs/poc-mvp-plan.md`）：PoC=P1 断面引擎、P2 图形→计算桥、P3 结果→PDF（P4 FE 可选后置）；MVP=3 体系 + 单城市 10–20 人 + 6 类分析图 + 不含 DWG 写入/签章；出口判据 M1–M7；8 城依次推广，禁止并行铺开。PoC 完成后用实测吞吐反推排期。
- D20（2026-10-20用户确认）：**正确性以规范为准**（旧系统存在已知错误，本轮修正）；与旧系统的每处差异必须登记 `Deviation`（条文依据/影响面/裁决人），未裁决不得用于对外 PDF；`compat_profile` 仅用于复现历史结论与对账。
- D21（2026-10-20用户确认）：计算引擎**首版优先 TypeScript 单栈纯函数**（无随机/无时钟/无 IO），超越函数若与旧 CRT 存在差异则隔离到 WASM 替换；该选择不改变"桌面宿主/部署形态"仍待 ADR 的状态。
- D22（2026-10-20用户确认）：历史工程继续由旧系统处理，新系统只处理**新项目**；`.cwx` 写回与记录边界（`u32 A`）移出 P0/P1 范围，仅保留"可选只读参照"。

- D23（2026-10-21用户）：**旧系统产品名不得进入新系统；旧系统不规范的命名必须规范化**。按四层执行：T0 新系统表面积（代码/UI/API/包名/日志）只允许标准名，出现 `XWall`/`HWKSoft`/`HWK` 前缀等旧产品名即违规；T1 领域标识用标准领域名（规范编号与条文号保持官方写法）；T2 兼容适配层（`.cwx` 导入、旧 DB 适配）允许旧名但必须集中且逐条登记映射；T3 证据/文档保留原名供追溯。首轮映射见 `docs/naming-conventions.md` §5.4，权威登记表为 `planning/naming-observations.json`（每条补 `canonical_name` 与 `layer`）。该决定**取代**此前"原名为准、不覆盖"的默认做法（D08 的"不批量改名"仅适用于尚未建立映射的条目）。

- D24（2026-10-21用户）：新系统产品名定为 **FORCITIS-x**（显示写法 `FORCITIS-x`；技术标识小写 `forcitis-x`）。该名进入 T0（UI 标题、报告页眉/页脚、包名、安装程序名、日志标识），**不含旧品牌字样**。派生约定：npm scope `@forcitis-x/*`、根包名 `forcitis-x`、可执行文件名 `forcitis-x`、报告落款“FORCITIS-x”。中文显示名暂缺（待定）。商标/域名可用性未核查，属**未完成的法律核对项**；核查后若需改名，只改 T0，不改领域标识与数据 ID。D23 的“禁用旧产品名”不变。

