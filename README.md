# HWK Modern

从原版安装资产重新建立可替代旧应用的现代实现。当前主线：B02 现成原版运行验证；B01 静态基线仍 PARTIAL（B01-02/03 BLOCKED），产品实现尚未开始。

## 已准备

- `vendor/64位网络版V5.4.25.1220/`：从旧工作区逐文件复制的安装包，含11个文件（包括包内元数据文件），共229,569,830字节。
- `evidence/baseline/installer-manifest.json`：来源、大小及SHA-256；只证明复制一致。目录标签不证明实际程序版本。
- `docs/goal-driven-plan.md`：完整目标、阶段门槛、独立验收、阻塞处理。
- `docs/goal-driven-source.md`：Goal-Driven 官方方法核查。
- `planning/`：范围、任务、验收状态。空白库存或缺失证据均不能通过最终验收。

## 检查与启动

```sh
python3 scripts/verify-installer.py
python3 scripts/check-acceptance.py --self-test
python3 scripts/check-acceptance.py
```

第三条目前应返回非零：应用未实现，功能库存未闭合。前两条通过仅证明资产完整及验收检查器的基础防误报行为。

继续工作先读 `AGENTS.md` 和 `HANDOFF.md`。执行首任务：`planning/tasks.json` 的 `B01`。启动双代理时使用 `docs/start-goal-driven.md`，本次准备没有启动长期运行。

## 边界

“最新”仅指在提供的旧hwk根目录发现的本地包；未核查厂商最新版。原安装程序尚未运行，实际二进制版本、授权、可运行环境均待核验。

旧工作区 `/Users/yeliang/Projects/YeliangDu/hwk` 保持原样；未复制旧实现、旧解包结果或旧运行库。历史分析仅能在以后作为待重新核验的证据索引。新实现统一在 `replica/`，证据统一在 `evidence/`。

本地Git仓库尚无提交、远端或推送。安装包将随本地版本管理；如以后选择远端，先确定私有存储和大文件策略。

## B01 静态提取里程碑（2026-10-18）

从工作副本使用7z 17.05提取MSI流及CAB，共517文件、142个MZ候选；CAB含458文件。清单与原始PE listing在 `evidence/baseline/b01/`。CAB中XWall.exe的PE资源ProductVersion为5.4.25.1209，目录标签为5.4.25.1220；两者不等同，实际安装版本仍待核验。MSI产品属性、安装文件名映射和依赖清单尚未完成。未运行任何包内程序。

资产复核PASS，台账检查器self-test PASS，最终验收FAIL（预期：库存及实现缺失）；npm test/build/lint均NOT_RUN。

## 自动续接

用户已授权本机launchd调度：每轮串行执行、独立验收，然后读交接续跑。操作与限制见 `docs/start-goal-driven.md`；状态命令为 `python3 scripts/scheduler/control.py status`。

## B01 MSI映射切片（2026-10-18）

状态PARTIAL，待独立审核。MSI表解码得到ProductVersion=`05.45.1211`；File表458条全部关联CAB且大小匹配，XWall.exe File.Version=`5.4.25.1209`。三种版本记录不合并。证据与缺口见 `evidence/baseline/b01/msi-decoded/findings.md`；表、路径和哈希均可复采。采集回归运行 `python3 scripts/test-msi-decoder.py`，含真实包关联及损坏/恢复对照，2项通过；不代表HWK业务回归。检查原始结果见 `evidence/baseline/b01/msi-checks.json`。原版安装、精确运行依赖和自定义动作仍未验证；npm检查NOT_RUN，最终验收FAIL。

## 独立验收（2026-10-18）

B01保持PARTIAL。主代理重新提取MSI/CAB并逐文件比对，59+458个原始文件哈希一致；独立复跑资产、采集回归和检查器自测通过。最终台账验收FAIL；npm三项NOT_RUN。重跑同一解码器不能替代独立MSI实现或原版运行证明。详情见 `evidence/scheduler-reviews/20261018T091825Z/review.md`。

## B01 依赖与自定义动作切片（2026-10-18）

状态PARTIAL，待独立验收。新增142个PE头部/导入清单（13个非零CLR目录）、8份配置原文、MSI自定义动作序列与条件，见 `evidence/baseline/b01/dependencies/findings.md`。XWall.exe为x64原生PE；HWKInstallDo的静态导出与安装序列已关联，实际效果仍未知。采集脚本 `scripts/collect-package-dependencies.py`；采集回归 `scripts/test-package-dependencies.py` 两项通过，独立读取PE头核对格式/CLR及源哈希。资产复核、MSI回归、检查器自测通过；最终验收FAIL，npm三项NOT_RUN。未运行原版、未作架构决定。

## HWK-000002 独立验收（2026-10-18）

静态采集子步骤PASS，B01仍PARTIAL。独立重采151份清单/原文哈希一致；资产前后校验、依赖与MSI采集回归及检查器自测PASS。最终验收FAIL；npm三项NOT_RUN。独立MSI读取、精确先决条件和运行行为仍待补证，B02依赖未满足。详见 `evidence/scheduler-reviews/20261018T092331Z/review.md`。

## HWK-000003 DataInfo 配置切片（2026-10-18）

B01保持PARTIAL，待独立审核。三份相同配置的DataInfo各解码17条连接模板、9466字节，保存字段偏移、长度、UTF-16LE原文及二进制，完整重编码一致。详见 `evidence/baseline/b01/datainfo/findings.md`。配置选择器均为SQL_NC_SP，不证明运行时数据库版本。新增采集回归2项通过，既有依赖/MSI回归及检查器自测退出0，资产复核退出0；最终验收FAIL，npm三项NOT_RUN。未运行原版、未决定架构；CLR元数据与原版运行缺口仍在。

## HWK-000003 独立验收（2026-10-18）

DataInfo静态采集子步骤PASS，B01仍PARTIAL。主代理独立读取源配置并核对哈希、归档、十六进制、全部字段偏移/长度/文本及选择器；三份均17条、9466字节。资产前后复核、三组取证回归与检查器自测PASS；最终验收FAIL，npm三项NOT_RUN。B02依赖未满足，CLR元数据及原版运行仍缺证据。详见 `evidence/scheduler-reviews/20261018T092720Z/review.md`。

## 实时开发看板

本机访问 [HWK 开发看板](http://127.0.0.1:18743)。每3秒自动读取任务、执行流水、独立验收与阻塞；新卡出现、执行转验收、轮次结束后保留卡片。点击卡片查看会话、结论与证据。以阶段台账判断业务完成，轮次结束不等于阶段PASS。

看板代码为 `replica/dev-board/`，只读数据服务为 `scripts/scheduler/dashboard.py`，由独立launchd任务 `com.yeliang.hwk-modern-board` 登录启动并在异常退出后恢复。不会改变开发调度状态，仅本机可访问。检查证据在 `evidence/scheduler/setup/dashboard/`。

开发看板自己的npm test/build/lint均PASS；这些检查只覆盖工程辅助看板。HWK替代应用尚未建立，其业务验收门槛仍按 `planning/acceptance.json`，不得用看板检查替代。

## HWK-000004 CLR 元数据切片（2026-10-18）

B01保持PARTIAL，待独立审核。通过REA静态提供程序采集13个HWKUtilRibbon载荷、130条AssemblyRef声明及目标框架属性，完整原始Evidence与边界见 `evidence/baseline/b01/clr/findings.md`。新增字节核对回归2项通过，既有三组取证回归、检查器自测及资产前后校验退出0；最终验收FAIL，npm三项NOT_RUN。行偏移、属性blob仍需进一步独立验证；元数据不证明安装或运行要求。未运行原版、未作架构决定。

## HWK-000004 独立验收（2026-10-18）

静态采集及有限字节核对子步骤PASS，B01仍PARTIAL。亲自复跑资产前后校验、四组取证回归和检查器自测PASS；最终验收FAIL，HWK应用npm三项NOT_RUN。独立核对13份REA封装与源哈希、元数据表行数及130条引用token blob；行偏移仍由REA提供，目标框架属性与完整表游标尚待独立验证。详见 `evidence/scheduler-reviews/20261018T093700Z/review.md`。B02依赖未满足，下一轮继续B01静态取证。

## HWK-000005 CLR 表游标与属性切片（2026-10-18）

B01保持PARTIAL，待独立审核。直接读取13个载荷，以独立表游标核对13个Assembly、130个AssemblyRef偏移；沿属性构造器/类型引用解码11个目标框架字符串，与旧记录一致。详见 `evidence/baseline/b01/clr-independent/findings.md`。REA 6.7.0实际连接版本握手被客户端策略拒绝，未继续使用连接，未宣称新版重采。新增2项取证回归、既有四组回归、资产前后检查及检查器自测退出0；最终验收FAIL，HWK业务npm三项NOT_RUN。独立MSI读取、运行环境与真实业务对照仍缺证据；命名/重构准备仅增静态观察。

## HWK-000005 独立验收（2026-10-18）

有限静态子步骤PASS，B01仍PARTIAL。独立读取器不导入执行侧代码，从PE/CLI源字节核对13份载荷全部已出现表布局、13个Assembly、130个AssemblyRef及11个目标框架属性链；仅覆盖实测小heap/小索引。资产前后、五组取证检查和检查器自测PASS；最终验收FAIL，HWK应用npm三项NOT_RUN。CLI实测6.7.0，实际MCP版本握手被客户端拒绝，保持BLOCKED。独立MSI与原版运行缺口仍在，B02依赖未满足。见 `evidence/scheduler-reviews/20261018T094300Z/review.md`。

## HWK-000006 独立 MSI 流读取切片（2026-10-18）

B01保持PARTIAL，待独立验收。独立固定schema读取器从提取流核对五表610行（Property47/File458/CustomAction9/执行序列73/UI序列23），与已有记录一致；ProductVersion原文05.45.1211，458载荷大小一致。来源字节/偏移/哈希与界限见 `evidence/baseline/b01/msi-independent/findings.md`。新增2项采集回归及既有检查退出0，资产前后复核退出0；最终台账FAIL，HWK应用npm三项NOT_RUN。REA实际MCP握手被客户端拒绝，身份BLOCKED；未修改配置。尚无独立OLE读取、其余表认证或原版运行证据，未解锁B02或架构选型。

## HWK-000006 独立验收（2026-10-18）

有限静态子步骤PASS，B01仍PARTIAL。亲自核对五表610行全部单元格、字符串池（含73107字节扩展条目）、流哈希及458载荷大小；资产前后、取证回归和检查器自测PASS。最终台账FAIL，HWK应用npm三项NOT_RUN。CLI6.7.0，实际MCP握手被客户端拒绝，身份BLOCKED。独立OLE/Binary绑定及原版运行未验证，B02依赖未满足；下一轮继续B01静态取证。见 `evidence/scheduler-reviews/20261018T095000Z/review.md`。

## HWK-000007 OLE/Binary 绑定切片（2026-10-18）

B01保持PARTIAL，待独立验收。普通源字节读取器直接读取MSI的CFB v3容器，59流与既有提取结果逐字节一致；六条Binary记录中，三条Binary来源动作关联到两个载荷哈希。原名、目录扇区链、字段偏移、哈希与限制见 `evidence/baseline/b01/ole-bindings/findings.md`。新增两项采集回归及既有五组回归、检查器自测、资产检查退出0；最终验收退出1，HWK应用npm三项NOT_RUN。实际REA MCP握手被客户端策略拒绝，CLI6.7.0；本轮字节读取不是REA Evidence。未执行安装动作、未解锁B02或决定架构。

## HWK-000007 独立验收（2026-10-18）

有限静态切片PASS，B01保持PARTIAL。独立读取MSI原始CFB字节，核对59流、6个Binary键及原始Object单元格、3条动作到2份载荷哈希的绑定。资产及执行证据前后哈希一致，六组取证回归与检查器自测通过；最终台账FAIL，HWK应用npm三项NOT_RUN。实际REA MCP握手被客户端拒绝，CLI6.7.0；独立字节审核不是REA Evidence。原版运行、启动条件及其他来源种类未验证，B02依赖未满足。下一轮继续B01静态声明取证。见 `evidence/scheduler-reviews/20261018T100100Z/review.md`。

## 可验证、可回收的并行

已允许一条主线＋一张隔离取证卡；看板同时显示，卡片区分“主线轮次”和“隔离取证”。输入冻结、系统写隔离、独立只读验收、哈希与真实执行日志门禁后，证据只导入全新目录。共享台账由主线汇总。可暂停、取消旁卡或退回串行；已定位的临时工具/报告故障允许保留失败记录后用新卡恢复一次，业务失败不能靠降标准重试。规则和命令见docs/start-goal-driven.md。

当前调度/看板控制回归31项PASS，构建、lint及资产复核PASS，真实隔离哨兵写保护及双卡并行已核验。首次并行报告未满足门禁被拒，未导入，原产物保留；重试使用新卡。以上均为工程控制验证，不替代HWK业务验收。

用户已授权必要时在阿里云建立测试环境；当前未因此创建资源，也未证明原版运行环境或软件许可就绪。

## HWK-000010 启动条件与搜索声明切片（2026-10-18）

B01保持PARTIAL，待独立验收。直接MSI源流新增五表43行，核对一个启动条件、四组文件搜索及九条动作的来源字面匹配与序列。REA CLI6.7.0另采集MSVBDPCADLL两个opaque资源及范围哈希；实际MCP握手被客户端拒绝。见 `evidence/baseline/b01/launch-search/findings.md`。七组取证回归、检查器自测及资产检查退出0；最终门槛FAIL，HWK业务npm三项NOT_RUN。准确先决条件和原版运行仍未知，B02未解锁；必要时建立阿里云环境已有用户授权，当前资源未核查。

## HWK-000010 独立验收（2026-10-18）

有限静态切片PASS，B01仍PARTIAL。亲自从源MSI核对十表653行及四组搜索、九动作字面关联；七组取证回归与检查器自测PASS，资产及执行证据前后哈希一致。CLI6.7.0资源清单与源载荷哈希复采一致，实际MCP身份核验被客户端拒绝，保持BLOCKED。最终门槛FAIL，HWK应用npm三项NOT_RUN。准确先决条件、控制流和原版运行仍未知，B02未解锁。见 `evidence/scheduler-reviews/20261018T101000Z/review.md`。

## HWK-000012 安装辅助DLL资源切片（2026-10-18）

B01保持PARTIAL，待独立验收。MSVBDPCADLL源字节解码两个资源：固定版本16.0.32016.11111、四Runtime显示串及九个版本字符串；另读取18导出，与CheckFX/VsdLaunchConditions安装目标字面关联。见 `evidence/baseline/b01/installer-resources/findings.md`。这些声明不证明准确运行库要求或动作实际行为。八组取证回归、检查器自测、资产前后检查退出0；最终门槛FAIL，HWK业务npm三项NOT_RUN。REA CLI6.7.0完整Evidence保留，实际MCP握手被客户端拒绝，身份BLOCKED；未运行原版、未解锁B02或决定架构。

## HWK-000012 独立验收（2026-10-18）

有限静态切片PASS，B01仍PARTIAL。独立从PE资源目录定位并核对两个资源、16字符串槽、完整版本树及18导出；八组取证回归、检查器自测及资产前后核验PASS，执行证据哈希未变。CLI6.7.0完整资源Evidence复采一致，实际MCP握手被客户端拒绝，身份BLOCKED。最终验收FAIL，HWK业务npm三项NOT_RUN；准确先决条件、动作行为及原版运行仍未知，B02未解锁。详见 `evidence/scheduler-reviews/20261018T101500Z/review.md`。

## HWK-000013 框架声明与指令字面关联（2026-10-18）

B01 PARTIAL，待独立验收。新增[静态切片](evidence/baseline/b01/framework-static/findings.md)：框架Property原文、10个DLL字面值及逐字节核对的指令地址引用、164普通导入；CheckFX地址窗口57处间接call中56处关联普通IAT，1处未解析。原始失败测试与修正后2项通过均保留。资源、启动搜索、依赖回归、资产复核及门槛检查器自测退出0；最终门槛FAIL，业务npm test/build/lint NOT_RUN。MCP身份核验遭客户端拒绝，CLI6.7.0原生就绪/GNU objdump路径失败；本切片来自普通源字节和Apple objdump，不冒称REA Evidence或原版运行。未确定准确运行先决条件或架构。

## HWK-000013 独立验收（2026-10-18）

有限静态切片PASS，B01仍PARTIAL。源MSI/PE独立读取核对164导入、10字面值/11引用、57个FF15模式；完整objdump复跑一致。0x10043884未解析，延迟导入目录为零；不证明函数边界或运行行为。九组取证回归、资产/执行证据前后哈希与检查器自测PASS，最终门槛FAIL，业务npm三项NOT_RUN。CLI6.7.0资源复采成功，实际MCP握手被客户端拒绝；B02未解锁。见 [独立验收记录](evidence/scheduler-reviews/20261018T102100Z/review.md)。

## HWK-000014 B01 槽位来源切片（2026-10-18）

PARTIAL，待独立验收。0x10043884位于可写.data，源初始指向0x1003b09d并有HIGHLOW重定位；完整objdump精确匹配15处间接调用、一处写入。局部指令在本地候选0x1003be6b和GetEnvironmentVariableW普通IAT值之间选择，helper语义和实际分支未知。证据见 `evidence/baseline/b01/framework-slot/findings.md`；复采 `python3 scripts/audit-framework-slot.py`，回归 `python3 scripts/test-framework-slot.py`。十组取证回归、资产和门槛自测通过，最终门槛FAIL（预期），npm三项NOT_RUN。REA CLI6.7.0资源Evidence已保留，MCP版本握手被客户端拒绝；B01仍PARTIAL，B02未解锁。

## HWK-000014 独立验收（2026-10-18）

有限静态切片PASS：独立读取PE源字节核对槽位/重定位/164导入和局部分支，完整objdump复跑一致并核对15调用及1写入。十组回归、资产及执行证据哈希检查通过；最终门槛FAIL，业务npm三项NOT_RUN。CLI6.7.0资源Evidence复采一致，MCP实际身份BLOCKED。B01仍PARTIAL，helper/本地候选及原版运行未知，B02未解锁。见[验收记录](evidence/scheduler-reviews/20261018T102700Z/review.md)。

HWK-000015执行：B01 helper/candidate有限静态切片 PARTIAL，117指令与VSD_FORCE_ANSI/三类导入关联见 `evidence/baseline/b01/framework-helper/findings.md`。11组回归、资产校验、门槛自测完成；输入哈希未变，最终门槛仍FAIL。REA CLI6.7.0资源Evidence已保存，MCP身份核验被客户端拒绝。等待独立验收；原版运行/求解与业务npm检查NOT_RUN，B01 PARTIAL、B02未解锁。

## HWK-000015 独立验收（2026-10-18）

有限静态切片PASS，B01仍PARTIAL。117指令源字节、普通导入、局部分支、字面值与虚拟尾部范围独立核对；11组取证回归、资产和执行证据哈希检查PASS。CLI6.7.0资源复采一致，实际MCP身份BLOCKED。完整CFG、辅助转换/异常及原版运行未知；B02未解锁，最终门槛FAIL，HWK业务npm三项NOT_RUN。见 `evidence/scheduler-reviews/20261018T103200Z/review.md`。

## HWK-000016 本地转换/错误路径切片（2026-10-18）

B01 PARTIAL，待独立验收。[证据](evidence/baseline/b01/framework-conversion/findings.md)新增三个有界窗口199条指令、37条相对边、三处GetLastError普通导入关联及条件写操作源字节。12组取证回归、资产校验和门槛自测退出0，输入哈希未变；最终门槛FAIL，HWK应用npm三项NOT_RUN。REA CLI6.7.0资源Evidence已保存，实际MCP身份核验被客户端审批策略拒绝并记BLOCKED。局部转换/分配/清理语义、完整CFG、准确先决条件与原版运行仍未知；B02未解锁，命名/架构准备仅登记静态观察。下一条命令：`python3 scripts/test-framework-conversion.py`。

## HWK-000016 独立验收（2026-10-18）

有限静态切片PASS，B01仍PARTIAL。独立源字节复核199指令、37相对边、三处普通导入及扫描/条件写指令；12组取证回归、资产与执行证据哈希检查通过。CLI6.7.0资源复采一致，实际MCP身份BLOCKED；完整CFG、转换契约及原版运行未知。B02未解锁，最终门槛FAIL，HWK业务npm三项NOT_RUN。见[验收记录](evidence/scheduler-reviews/20261018T103900Z/review.md)。

## HWK-000017 转换分派静态切片（2026-10-18）

B01 PARTIAL，待独立验收。两个窗口63指令/10相对边关联0xfde9比较、本地辅助调用与MultiByteToWideChar/WideCharToMultiByte普通导入；见[证据](evidence/baseline/b01/framework-dispatch/findings.md)。13组取证回归、资产及门槛自测退出0，输入哈希不变，最终门槛FAIL。REA CLI6.7.0资源Evidence保留，MCP身份BLOCKED。完整转换/异常契约、准确先决条件及原版运行未知；B02未解锁，业务npm三项NOT_RUN。

## HWK-000017 独立验收（2026-10-18）

有限静态切片PASS：独立核对63条指令、10条相对边及两处普通导入声明；13组回归、资产与执行证据哈希检查通过。CLI6.7.0资源复采一致，MCP身份BLOCKED。完整CFG/转换及异常契约/准确先决条件与原版运行未知；B01仍PARTIAL、B02未解锁，最终门槛FAIL，HWK业务npm三项NOT_RUN。见[验收记录](evidence/scheduler-reviews/20261018T104400Z/review.md)。

## HWK-000018 共用错误状态静态切片（2026-10-18）

B01 PARTIAL，待独立验收。[证据](evidence/baseline/b01/framework-error-state/findings.md)记录两个有界窗口17指令、2分支、GetLastError/SetLastError两处普通导入关联及13处E8调用引用。局部偏移+4写入与条件恢复模式有源字节支持，对象类型、生命周期及完整异常契约未知。14组取证回归、资产校验及门槛自测退出0，vendor/源载荷哈希不变；最终门槛FAIL，业务npm三项NOT_RUN。REA CLI6.7.0完整资源Evidence已存，MCP身份核验被客户端拒绝，BLOCKED。准确先决条件和Windows原版运行仍未验证，B02未解锁；命名/架构准备仅增量登记静态事实。

## HWK-000018 独立验收（2026-10-18）

有限静态切片PASS：独立核对17指令、2分支、2普通导入及13处E8调用；14组取证回归、资产和执行证据哈希检查通过。修正名称观察误放字段列表的问题。CLI6.7.0资源复采一致，实际MCP身份BLOCKED。B01仍PARTIAL、B02未解锁；准确先决条件与原版运行未知，最终门槛FAIL，业务npm三项NOT_RUN。见[验收记录](evidence/scheduler-reviews/20261018T104900Z/review.md)。

## HWK-000019 运行准备关联切片（2026-10-18）

B01 PARTIAL，待独立验收。[证据](evidence/baseline/b01/runtime-readiness/findings.md)锁定五份既有JSON与142PE源哈希，关联2382条导入边（388条有包内同名候选）及13托管框架声明；候选不表示实际加载或安装要求。阿里云CLI3.4.11可用；上海只读ECS查询在OAuth端点DNS失败，未取得资源列表、未创建资源。Windows/许可和原版运行仍未知，B02未解锁。REA CLI6.7.0，MCP身份调用被客户端拒绝，未重试；本轮是既有静态JSON汇总。检查见checks.json；HWK业务npm三项NOT_RUN，最终门槛FAIL。

## HWK-000019 独立验收（2026-10-18）

有限既有静态JSON关联切片PASS；142PE/13托管源哈希、2382导入边完整集合及版本分离核对一致。15组取证回归、资产及执行证据哈希检查通过。跨格式候选0；同名候选不证明实际加载。B01 PARTIAL、B02未解锁，Windows/许可与原版运行未知，MCP实际身份BLOCKED、CLI6.7.0，最终门槛FAIL，业务npm三项NOT_RUN。见[验收记录](evidence/scheduler-reviews/20261018T105500Z/review.md)。

## HWK-000020 CheckFX属性消费者（2026-10-18）

B01 PARTIAL，待独立验收。[证据](evidence/baseline/b01/framework-properties/findings.md)新增7个窗口379指令、94相对边、12普通导入关联及两个helper到msi.dll序号74/145的跳板链。记录ANY回退候选、False声明与false比较字面值差异、TRUE输出候选、局部条件和返回路径；实际属性值、比较大小写、完整CFG/异常及准确先决条件未知。16组取证回归最终退出0；错误字面值预期和修正日志保留，源输入未改。资产/载荷哈希不变，安装包校验及门槛自测退出0，最终门槛FAIL，业务npm三项NOT_RUN。CLI6.7.0资源Evidence已保存，MCP身份核验被客户端拒绝，BLOCKED；B02未解锁，未运行原版或作架构决定。下一条命令：`python3 scripts/test-framework-properties.py`。

## HWK-000020 独立验收（2026-10-18）

有限静态切片PASS：379指令、94相对边、12普通导入及41处E8引用独立源字节复核一致，16组取证回归通过，资产与执行证据哈希未变。CLI6.7.0资源复采一致，MCP身份BLOCKED。B01仍PARTIAL、B02未解锁；完整CFG/属性/比较语义、准确先决条件与原版运行未知，最终门槛FAIL，业务npm三项NOT_RUN。见[验收记录](evidence/scheduler-reviews/20261018T110100Z/review.md)。

## 整体Goal与WBS

现在按整体Goal HWK-G001 → 十个阶段成果 → 明确工作包 → 执行/独立验收卡 → 原始证据派发。定义在planning/stage-contracts.json，进度在stage-progress.json；看板可切换阶段并展开工作包目标、输入、交付物、完成条件和依赖。

B01收敛为四包：版本身份、包内完整文件/组件库存、相关安装先决条件交接、基线独立验收。优先汇总既有证据，不再按上一轮地址/函数无界开卡。历史卡不删除，也不自动算工作包通过。

求解与全体系实施中尚依赖真实库存的项目标为待分解容器；规划包独立通过、有限子包覆盖全部冻结功能ID后，才执行叶子包。所有工作包独立通过才推进阶段；复盘上限触发未完成/阻塞，不降低标准。控制回归45项及看板build/lint、资产复核PASS；不代表HWK产品验收。

## HWK-000021 · B01-01版本基线交付

PARTIAL，等待独立验收。[工作包清单](evidence/stages/B01/B01-01/work-package.json)锁定11原资产SHA-256，复核517提取文件、140已有PE listing版本声明并补录5随包EXE版本。目录标签5.4.25.1220、MSI ProductVersion原文05.45.1211、XWall.exe MSI File.Version及PE版本5.4.25.1209分别保留，差异原因未知。复跑：`python3 scripts/check-version-baseline.py`，不新增版本解析器。三组相关取证回归、资产检查及门槛自测退出0；最终业务门槛退出1，应用npm test/build/lint NOT_RUN。REA CLI6.7.0；实际MCP握手被客户端拒绝，未重试/改配置。本轮7z/MSI读取不冒称REA Evidence，未运行原版或选定新架构。

## HWK-000021 · B01-01独立验收

版本身份工作包PASS，B01阶段仍PARTIAL。亲自复核11原资产、517提取文件、145份7z listing，以及原XWallClientX64.msi的59流与五表610行源字节；执行证据哈希未变。目录标签5.4.25.1220、MSI原文05.45.1211、主PE版本5.4.25.1209分别保留，差异原因未知，以资产SHA-256集合锁定。相关检查通过；最终业务门槛FAIL，HWK应用npm三项NOT_RUN，实际REA MCP身份BLOCKED。见[独立验收](evidence/scheduler-reviews/20261018T112200Z/review.md)。剩余B01工作包由控制器派发，未认证安装运行或新架构。

## B01-02 文件组件库存汇总（HWK-000022）

PARTIAL，已提交独立验收候选：`evidence/stages/B01/B01-02/work-package.json`。11原资产、458 CAB载荷、59 MSI流（含6 Binary）、459组件/30目录/459特性映射逐项保留；142 PE、375非PE、13 CLR记录与既有来源/哈希对应。1个无File载荷组件单列；声明导入和实际绑定分开。

随包运行库安装器按原资产登记；嵌套载荷未递归核查，实际安装/绑定留B02，完整业务库存留B03。未新增二进制分析；REA预期6.7.0，身份查询被客户端审批拒绝，未重试。复跑：`python3 scripts/check-component-baseline.py --out /private/tmp/hwk-b01-02-review`。资产、五组相关取证回归和门槛self-test通过；最终业务门槛FAIL，npm test/build/lint NOT_RUN。原始结果见同目录checks.json；阶段状态由外部控制器维护。

B01-02独立验收仍PARTIAL：主MSI/CAB源字节及库存复跑通过；四个SQL/VC随包安装器内部载荷库存、哈希和来源缺失，须定向补证后复审。独立日志：`evidence/scheduler-reviews/20261018T113100Z/review.md`。未将静态缺口移交为B02运行验证。

## 独立目标审查控制器（2026-10-18，本轮）

工作包全部PASS只产生阶段候选；独立只读assessor分别审查阶段实际达成、总Goal贡献、组合覆盖与整体实际达成。控制工程回归、build/lint及资产检查见evidence/scheduler/setup/assurance-verification/。首次真实审查HWK-000023因证据路径夹带说明被拒绝，无放行记录；新会话HWK-000024已采纳CONTINUE，贡献PASS、组合PARTIAL、总体实际达成PARTIAL，仅允许继续B01补证，最终接续状态以HANDOFF.md及planning/goal-assurance-implementation.json为准。看板已接入独立审查角色，并在Chrome实际核对。上述控制工程检查不代表HWK业务实现或业务验收通过；B01仍PARTIAL。

本轮最终64项控制工程回归、dev-board build/lint、资产核验PASS。阶段目标尚未实证放行；主控复核下一包为B01-02，并恢复已授权launchd续接。

## HWK-000025 · B01-02第二轮定向补证

执行候选BLOCKED，待独立审核与两轮上限复盘，B01仍PARTIAL。[本轮证据](evidence/stages/B01/B01-02/attempt-25/findings.md)新增2,116静态节点、6份SQL/VC MSI、253条File映射、41条Binary记录及两份Burn载荷清单；来源/哈希、声明与实际绑定分开。16份WSUS扫描目录未递归闭合，MSU组件目标/差分内容仍未知，不能把静态缺口移给B02。相关回归与资产复核通过；最终业务门槛FAIL，HWK应用npm三项NOT_RUN。REA CLI6.7.0资源Evidence已保存，实际MCP身份被客户端策略拒绝。未运行原版、选择架构或修改云资源。复跑：`python3 scripts/test-bundled-runtime.py --out evidence/stages/B01/B01-02/attempt-25`。

B01-02第二轮独立验收 **BLOCKED**：资产与相关回归复跑通过，新增逐节点分类、MSI组件/特性及Binary哈希复核和16份WSUS源listing；内部成员库存与MSU目标/差分对应仍未闭合。见[evidence/scheduler-reviews/20261018T121000Z-B01-02/review.md](evidence/scheduler-reviews/20261018T121000Z-B01-02/review.md)。控制器处理两轮复盘，B01-03可独立继续；阶段仍PARTIAL，原版运行与npm检查NOT_RUN。

## 阻塞接手机制（2026-10-18）

自动暂停后由launchd接手一次独立只读诊断，保留阻塞单、处理步骤、解除条件与待决事项；用户暂停不触发。查询 `python3 scripts/scheduler/control.py blockers`。自动修复/恢复尚未实现，前台处理并验证后恢复，详见 docs/start-goal-driven.md。6项阻塞控制回归及12项runner回归PASS；不是HWK业务验收。

控制阻塞修复：HANDOFF合法来源与诊断路径规范化已验证，47项控制回归及资产完整性PASS；B01-02仍BLOCKED（2/2），有限复盘提案见evidence/scheduler-reviews/20261018T-recovery/B01-02-replan-proposal.json，尚未批准或执行。

## HWK-000029 · B01-03安装先决条件收敛

执行候选 **PARTIAL**，待独立审核。[工作包清单](evidence/stages/B01/B01-03/work-package.json)关联MSI全部序列及9项动作，核对三个包络1,830指令源字节、2,172边与13处标志引用。新增消费者传入`_VsdLaunchCondition`/查询模板和`0x100124bf`回调地址的证据；包络及顺序边不等于完整CFG。入口绑定、标志可达性、回调/异常和相关返回仍未闭合，不满足done_when；四项有限补证及B02运行步骤见[记录](evidence/stages/B01/B01-03/findings.md)。

复跑：`python3 scripts/summarize-install-prerequisites.py --out /private/tmp/hwk-b01-03-review`及`python3 scripts/test-install-prerequisites.py`。新增3测试及三组相关回归、资产校验与门槛自测通过；最终业务门槛FAIL，HWK应用npm三项NOT_RUN。首次误用不存在的门槛脚本退出2已保留并按实际脚本补跑。REA CLI6.7.0；MCP身份调用被客户端审批策略拒绝，未重试，未把普通objdump关联称为REA Evidence。B01仍PARTIAL、B01-02仍BLOCKED，B02未解锁；未运行原版或改变架构/云资源。

## HWK-000029 · B01-03独立验收

工作包 **PARTIAL**：独立复跑与PE源字节审计一致，资产/冻结输入/交付哈希不变，相关回归通过。安装入口、CheckFX标志路径、回调/求值及异常/最终返回仍有四项缺口，不能因1830指令和局部检查通过标PASS。合同剩余一轮可定向补证；第二轮仍缺则BLOCKED复盘。见[验收记录](evidence/scheduler-reviews/20261018T125000Z-B01-03/review.md)。B01仍PARTIAL、B01-02仍BLOCKED、B02未解锁；最终业务门槛FAIL，HWK应用npm三项NOT_RUN。REA CLI6.7.0，实际MCP身份调用被客户端拒绝，未重试或改权限；未运行原版或改变云资源/架构。

## HWK-000030 · B01-03第二轮有界补证

执行候选 **BLOCKED**，待独立验收及两轮上限复盘。[本轮记录](evidence/stages/B01/B01-03/attempt-30/findings.md)新增205指令源字节核查，补回调调用/参数/遍历退出、msi.dll ordinal47跳板和F2前缀共用正常返回尾部；累计本图2035指令。setup入口、CheckFX标志生产及异常/HWKInstallDo最终返回仍缺，不能通过done_when；未扩大无关helper。复跑：`python3 scripts/audit-install-consumer-return.py --out /private/tmp/hwk-b01-03-return-review`。

新增3回归、两组既有回归、资产前后核查和门槛自测通过；最终业务门槛FAIL，HWK应用npm三项NOT_RUN。REA CLI6.7.0，实际MCP身份被客户端策略拒绝，未重试；本次是普通保留源字节核查。B01仍PARTIAL、B02未解锁，未运行原版/真实工程或改变云资源/架构。合同与阶段进度由外部控制器维护。

## HWK-000030 · B01-03独立验收

工作包 **BLOCKED（两轮上限）**：2035条局部指令及ordinal47源导入身份独立复核、回归与资产哈希检查通过；四项安装控制流/返回缺口仍未关闭，见[验收记录](evidence/scheduler-reviews/20261018T131000Z-B01-03/review.md)。B01仍PARTIAL，B01-04依赖未满足、B02未解锁，须外部主控有限复盘。最终业务门槛FAIL；HWK应用npm三项及原版运行NOT_RUN。REA CLI6.7.0，实际MCP身份被客户端策略拒绝，未重试。

## 自动阻塞修复已启用（用户最新授权）

launchd现消费阻塞诊断并自动执行修复、独立复核、受审有限合同修订和合法续接；细则见planning/auto-recovery-policy.json及docs/start-goal-driven.md。真实HWK-000032复核否决后保留业务阻塞，正在按反馈有限补修；原业务PASS门槛不变。修复失败会尝试其它合格阻塞包，无可行方法或外部输入缺失则明确停止，不无限循环。

现成环境已实测：2026-10-18 SSH连通HWK-WIN-TEST（Windows Server 2022），已安装XWall.exe与冻结包SHA256完全一致，LocalDB进程运行。证据evidence/runtime/ecs-20261018/summary.json。服务端连接、许可和真实工程业务闭环仍NOT_RUN；不代表B01/B02或产品验收通过。

## 运行优先工作流（2026-10-18用户授权）

新版合同v2经HWK-000036独立计划审查CONTINUE，主控回读verified_plan=True、select=B02-01。主线B02→B03→B04→P01–P04→E01；B01剩余义务保留并在R01前闭合，R01仍须干净安装卸载及全量业务/使用者专业验收。

本轮ECS隔离启动、文件对话框提交门窗样例和原安装445文件哈希不变已实测；工程语义、许可认证、计算/报告/绘图/往返未通过，运行观察PARTIAL，见evidence/runtime/workflow-reset/summary.json。76项控制/重编排回归及资产核验PASS，均不是业务PASS；应用npm检查NOT_RUN。

## HWK-000037 · B02-01（2026-10-18）

BLOCKED：本会话SSH连接被网络策略拒绝（Operation not permitted，exit 255），远端未执行脚本、未创建目录。冻结XWall与真实样例本地哈希复核、vendor校验和门槛自测通过；最终门槛仍FAIL，npm检查NOT_RUN。交付见 `evidence/stages/B02/B02-01/work-package.json`，环境采集脚本已准备但未经Windows执行验证。B02-01及产品均未通过，待独立复核与可连接会话续采。

HWK-000037独立验收：B02-01 BLOCKED。只读SSH复跑同样exit255/Operation not permitted；本地哈希与vendor前后通过，实时环境及隔离仍缺证。详见 `evidence/scheduler-reviews/HWK-000037-B02-01/review.md`。最终门槛未通过，npm三项NOT_RUN。

## 收敛驱动续接与事件销项（用户最新授权）

主线不再因固定轮数、单卡失败或连续两轮无增量自动停排；独立验收另给下一步focus，无明确下一步由续接agent判断方法/切片/合法包。原Goal、done_when、依赖与最终标准保留。HWK-000039实际SSH核查后CONTINUE，HWK-000040独立计划审查放行，B02-01仍保留旧BLOCKED验收而dispatch就绪。

后台workspace/read-only网络profile已实测可SSH，read-only仓库写入拒绝，不改全局配置或approval_policy。原固定次数修复链退出主线。阻塞事件处理后自动销项；12张历史卡移入历史（6销项/6归并），原失败与B01缺口不删除。独立目标判断正文13px已由真实Chrome DOM/截图核验；看板test/build/lint及控制回归PASS，仅工程辅助验收，HWK业务仍未通过。证据evidence/scheduler/setup/convergence/。

## HWK-000041 · B02-01实时环境及隔离交付

执行候选PARTIAL，待独立验收。[本轮清单](evidence/stages/B02/B02-01/attempt-41/work-package.json)记录SSH及Active console会话4、Windows Server 2022/zh-CN、346字体文件、10运行库记录、.NET 4.8及运行中的LocalDB 11.0.7001.0。实例i-bp1cb2hxk0td5z149z54、cn-hangzhou/cn-hangzhou-k实测；费用UNKNOWN，未新建资源。

新建 `C:\hwk-modern\HWK-000041-B02-01` 下client/projects/outputs；445文件源前后与副本清单完全一致，XWall和真实门窗样例匹配冻结资产。路径无重解析点，原PID60096未变，本轮无新启动/任务。只允许之后在留证及进程占用核查后回收本卡目录，保留现有ECS/源安装/其它进程任务。

命令长度拒绝、stdin EOF超时及LocalDB编码错误全部保留，定长UTF8传输及独立编码探针已实测成功；只停止本卡确认身份的超时读取进程。采集一致性、3项传输回归、资产及门槛自测通过；最终业务门槛FAIL，HWK应用npm三项NOT_RUN。REA MCP版本查询被客户端策略拒绝，环境证据非REA分析。数据库应用绑定、许可与计算/报告/保存重开仍待后续工作包。复跑：`python3 scripts/check-b02-environment-41.py`；不要重跑创建脚本覆盖已有目录。

HWK-000041独立验收：B02-01 PASS（仅环境及隔离）。直接SSH只读复跑445文件清单、工程哈希、环境/LocalDB及实例身份全部一致；61项交付输入哈希通过。证据：`evidence/scheduler-reviews/HWK-000041-B02-01/review.md`。B02整体仍PARTIAL，许可/计算/报告/往返未验证，产品门槛未通过，npm三项NOT_RUN。

## HWK-000042 · B02-02 UI及连接切片

独立验收PARTIAL；[复核日志](evidence/scheduler-reviews/HWK-000042-B02-02/review.md)确认源445文件、冻结副本/样例、进程及TCP快照一致，64项交付哈希匹配。新启动与实际许可仍NOT_RUN。[工作包清单](evidence/stages/B02/B02-02/work-package.json)及[清晰截图](evidence/stages/B02/B02-02/attempt-42/desktop-visible.png)：现有隔离XWall PID60096/session4显示sample-working.cwx工程树和属性；进程TCP快照实测Established到165.154.20.222:1433，仅证明该时刻连接，不证明服务端身份、SQL查询或许可。未重复启动客户端。445文件源安装、B02-01副本及样例哈希与既有基线一致。

本轮仅创建HWK-000042-B02-02采集目录/命名任务，任务已核对并移除，原进程保留；原安装、原样例及服务配置未修改。REA6.7.0身份查询被客户端审批策略拒绝，未重试，无新二进制分析。首张遮挡截图、返回数据但exit1、替代调度被已有任务保护拒绝及本地解析错误均留证。切片一致性、传输回归、资产前后校验和门槛自测exit0；最终产品门槛exit1，npm三项NOT_RUN。新副本启动、实际许可操作、计算/报告/绘图/往返仍待验证，干净安装卸载留B01/R01。复跑：`python3 scripts/check-b02-license-42.py`。

## HWK-000043 · B02-02 关于窗口切片（PARTIAL）

实际打开原版“关于”窗口，截图显示5.4.25.1209（64位网络版）、文档模型1057、工程模型677及服务到期日2028年5月17日。到期显示不证明许可操作可用；新冻结副本启动、许可门控操作及计算报告往返仍NOT_RUN。证据：`evidence/stages/B02/B02-02/attempt-43/`，交付清单：`evidence/stages/B02/B02-02/work-package.json`。源XWall与原门窗样例、本轮工作样例哈希复查一致；445文件全量刷新两次超时，保留历史独立核验边界。旧PID60096/session4及关于窗口保留，自有采集任务已清理。

资产前后校验、观察一致性、SSH传输回归及门槛自测exit0；最终门槛exit1；npm三项NOT_RUN。UIA未暴露关于文本；截图为该事实来源。独立验收待外部会话，不改合同/进度。

独立验收HWK-000043：PARTIAL。截图与原始UI均显示到期日2028年5月17日，已纠正执行摘要误读；80项交付及5项输入哈希一致，独立SSH复查现行进程/TCP与四项关键文件哈希匹配。新启动、实际许可操作仍NOT_RUN，445文件全量刷新未完成。详见[evidence/scheduler-reviews/HWK-000043-B02-02/review.md](evidence/scheduler-reviews/HWK-000043-B02-02/review.md)。

## HWK-000044 · B02-02 执行增量（待独立验收）

工作包保持PARTIAL。445项源安装文件与B02-01冻结清单逐项一致；已实际查看系统设置基本页并取消，正常退出旧客户端，以B02-01冻结客户端打开哈希一致的真实工程副本。新PID78216/session4响应正常，到165.154.20.222:1433的TCP连接已观测；限定时间窗Application 1000/1001/1026查询无记录。许可实际门控操作仍NOT_RUN，不能由到期文本、打开工程或TCP推断许可通过。安装卸载仍归B01/R01。

证据：`evidence/stages/B02/B02-02/attempt-44/`，交付：`evidence/stages/B02/B02-02/work-package.json`。回归：`python3 scripts/check-b02-license-44.py`；资产校验、transport与验收门槛自测通过，最终门槛预期FAIL，npm三项NOT_RUN。保留新进程供下一轮操作，禁止重复启动。

HWK-000044独立验收：PARTIAL/CONTINUE。171项交付与5项输入哈希一致；直接SSH只读复算445项源安装文件完全一致（前导路径符规范化留证），新PID78216/session4及1433连接复现，真实工作样例哈希未变。新启动原始截图/脚本经核对；实际许可门控仍NOT_RUN。证据：[独立复核](evidence/scheduler-reviews/HWK-000044-B02-02/review.md)。npm三项NOT_RUN，最终门槛FAIL；不重复启动，下一步在现有冻结客户端执行可逆实际许可门控操作。

## HWK-000045：许可操作取证进展（PARTIAL）

已展开真实工程强度树，打开门窗锁点强度信息及计算书输出设置；截图与原始采集见 `evidence/stages/B02/B02-02/attempt-45/`。目录选择尝试后原版 PID78216 在 SHELL32.dll 崩溃（事件1000/1001），根因及采集方法影响未明；路径保护未通过，未提交导出，无报告文件，实际许可仍未证实。源安装445文件及原样例/工作样例哈希前后相同。本轮任务已清理，当前无XWall，未重复启动。

切片证据检查、资产、SSH传输回归及验收器自测通过；最终验收检查仍非零，npm检查NOT_RUN（应用未建立）。下一步更换目录导航方法并恢复同一冻结隔离客户端，独立验收前B02-02保持PARTIAL；安装卸载仍属B01/R01。

独立验收 HWK-000045：B02-02 PARTIAL。只读SSH核对445项源文件、隔离程序及样例哈希一致，原PID崩溃事件获独立确认；当前无进程/报告。实际许可仍未证实，改用普通UI目录导航或可逆计算入口续接。证据见 `evidence/scheduler-reviews/HWK-000045-B02-02/review.md`。npm test/build/lint NOT_RUN；B02及最终Goal未完成。

## HWK-000046 · B02-02荷载重算切片（执行PARTIAL）

在同一冻结隔离客户端重新打开真实门窗样例，实际提交计算高度并观察内嵌计算输出变化：21m时高度系数0.754007、阵风系数1.976809，恢复20m后为0.737993、1.98735；最小值处理前的横梃负风荷载由-0.768453恢复-0.756143kN/m²。Ctrl+A未全选导致2021m的中间操作保留，随后明确首尾选择纠正；未保存工程。证据：`evidence/stages/B02/B02-02/attempt-46/`。

445项源安装、隔离EXE及样例哈希前后一致；PID113264/session4保持响应和TCP1433连接，本轮限定事件查询无新增XWall错误。本轮探针任务已移除，客户端保留且高度恢复20m。此荷载操作实际可用，但是否实施许可门控、服务器身份语义及其他分支未知；B02-02与整体目标仍PARTIAL，交独立验收。未做报告/文件往返或干净安装。

`python3 scripts/check-b02-license-46.py`、资产校验、SSH传输回归、验收检查器self-test均exit0；最终业务门槛exit1（未完成）。npm test/build/lint NOT_RUN，无应用。

HWK-000046独立验收：B02-02 PARTIAL。189交付及5输入哈希一致；直接只读SSH确认445源文件、隔离EXE/样例哈希和PID113264/session4及1433连接。21m→20m输出变化经原始截图/全文复核，许可门控仍未知。回归/资产/传输/门槛自测exit0，最终门槛exit1；npm三项NOT_RUN。验收会话误读SSH私钥造成工具日志泄露，continuation=STOP_SAFETY，须撤销替换凭据并独立复核后恢复远端取证。[独立日志](evidence/scheduler-reviews/HWK-000046-B02-02/review.md)。

B02-02 attempt-47（用户解除安全阻塞后续接，非控制器派卡）：**新增真实计算书生成切片**。隔离客户端（PID4568/session1，路径与冻结哈希一致）、445 源文件前后与 B02-01 冻结清单逐一相同、TCP 165.154.20.222:1433 建立。经普通 UI 目录树导航（MSAA 选中项反馈）把输出目录改到本轮授权 `C:\hwk-modern\HWK-000048-B02-02\reports`，再用产品自带「保存计算书文件」写出 2,829,593 字节 RTF（sha256 `577D61F4…A52A7B0`），全程未写入历史默认目录 `C:\hwk\hook-out`；生成分支无许可拒绝或错误，限定 Application 1000/1001/1026 查询为空。避开而非重试了 2026-10-18 的 BFFM_SETSELECTIONW 崩溃路径。许可条款、服务端授予语义及其它门控分支仍未知，报告文件名因自动化脚本缺 BOM 出现乱码（内容正确），生成的工程是存活客户端已打开的 a.cwx 而非冻结样例。B02-02 与整体目标仍 PARTIAL，交独立验收。证据 `evidence/stages/B02/B02-02/attempt-47/`，回归 `python3 scripts/check-b02-license-47.py`（exit 0）；验收检查器 self-test exit 0；npm test/build/lint NOT_RUN（无应用）。

## 离线模块透明化与查表解出（2026-10-20，用户指派线程）

状态：玻璃跨中挠度、玻璃面板强度两个模块的 5 项口径（调用面/算式/输入与查表/分支/数值）**全部闭合**，且数值复算不再手填系数：

- 查表节点 `GetSDr`（`FUN_1802a0fa0`，μ）与 `GetSMr`（`FUN_1802a2940`，m）的语义、23 条分支与 38 个内嵌轴表全部解出；`GetNg`（η）三张表同样已解。
- 锚点：μ=0.00406、m=0.0442 @ a/b=1；η=0.998228/0.992846/0.997133；外片应力 6.726054 复算差 9.8e-8。

```sh
python3 scripts/extract-coefficient-tables.py
python3 scripts/extract-lookup-table.py
python3 scripts/check-module-numeric.py
```

产物：`migration_workspace/coefficient-tables.md`、`lookup-tables.md`、`modules/glass-stress-transparency.md`、`VERIFICATION.md` A16–A18。
另（同轮续做）：`.cwx` 记录字段**顺序与类型**由 `Serialize` 链叠加解出，`HWKWallContext` 前 13 个字段与原版 `b.cwx` 字节逐字段对齐（3/3 差分锚点）：
`python3 scripts/build-serialize-chains.py --cwx migration_workspace/raw/cwx-diff-20261019/files/b.cwx`。

仍留：`GetSMr` 的石材/铝板细分分支（`$3∈{20,25,30}`）无原版打印锚点；`.cwx` 记录边界（`u32 A`）、聚合槽位细分与其余 411 个类的对齐（B11 残余）；B02/B01 主线状态不受本轮影响。
npm test/build/lint 仍 NOT_RUN（尚无应用）。

## 产品规格 V1 与 PoC/MVP（2026-10-20 用户确认）

产品定位：**中心化薄客户端工程计算协作平台**（8 城/300 人/200 人日常；域账号 SSO；无离线；100 在线/20 并发重算）。
正确性以规范为准，旧系统差异登记台账；交付物为"数值+文本+图形"三元组，PDF 内嵌 RulePack 指纹/引擎版本/figure hash/审计号。

- 冻结契约与待定项：`docs/product-spec-v1.md`（S1–S9）
- PoC（断面引擎 / 图形→计算桥 / 结果→PDF / FE 可选）与 MVP（3 体系 + 单城 10–20 人 + 6 类分析图）判据：`docs/poc-mvp-plan.md`
- 决策：`docs/decisions.md` D14–D22；可验收清单：`planning/scope.json`（POC-1..4、MVP-1..9，全部 NOT_RUN）

`python3 scripts/check-acceptance.py` 目前仍应 exit 1：13 项未通过 + 7 个 gate 未过；74 体系全量库存仍未闭合。

