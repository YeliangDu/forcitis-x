# HWK 计算核心结构（静态取证版）

状态：**PARTIAL**。全部结论来自静态证据（导出表 / 导入表 / objdump / Ghidra 12.1.4 反编译），
**没有**原版运行验证；标 `NOT_RUN` 的部分不得当作已确认行为。

证据等级缩写：`EXPORT`=导出表实测，`IMPORT`=导入表实测，`DISASM`=objdump 反汇编实测，
`DECOMP`=Ghidra 反编译（附 evidence_id），`STRING`=源字节字符串扫描，`NOT_RUN`=未验。

模块身份（`migration_workspace/raw/module-names.json`，102 个 PE 成员的导出表自报名）：

| 模块 | CAB 成员 | 导出数 | SHA-256 |
| --- | --- | --- | --- |
| `HWKKernal.dll` | `_F35DC0979FF04306B20773A25268CC58` | 32,314 | `877057a4…` |
| `HWKSciCal.dll`（计算引擎） | `_F9C459BBE74648A0830ACE9FDF861E3E` | 605 | 见 module-names.json |
| `HWKWallUtil.dll`（注册适配） | `_1D7374B2004D4FE39A79BCDFC9340FB8` | 748 | `efefcabb…` |
| `WallUtilPlug1.xdl`（插件） | `_73B1DFBD13E2497EBB9C0D8524329A54` | 1 | `60af5ba6…` |

---

## 1. 分层与依赖方向（`IMPORT`，`migration_workspace/raw/import-graph.json`）

```
XWall.exe ──6504 符号──▶ HWKKernal.dll
                         │
   adap_*.dll (10+ 个业务适配器) ──▶ HWKKernal.dll
                         │
                         ├──2 符号──▶ HWKWallUtil.dll ──179 符号──▶ HWKSciCal.dll
                         │                                   ▲
                         ├──84 符号──────────────────────────┘
                         └──55 符号──▶ HWKUtil.dll ◀──111 符号── HWKSciCal.dll
WallUtilPlug1.xdl ──166 符号──▶ HWKSciCal.dll，──27 符号──▶ HWKUtil.dll
HWKThermData.dll / HWKFeUtil.dll / HWKModelClass.dll / HWKOptim.dll / HWKShSolve.dll
                ──▶ HWKSciCal.dll（各 42 / 42 / 9 / 3 / 1 符号）
```

要点：

- `HWKSciCal.dll` 是**被 12 个模块导入**的公共计算引擎，不是某个业务模块的私有实现。
- `HWKUtil.dll` 是更底层的工具层（`String`、容器），被 25 个模块导入，连引擎自己也依赖它。
- `HWKWallUtil.dll` 只被 `HWKKernal.dll` 以 **2 个符号**导入——即 `InitNewFunction` 与 `InitMyFEFunction`
  这两个注册入口；内核不直接调用工具函数，而是通过命名条目。
- `adap_*.dll` 是业务适配层（架构立柱、强度、荷载、板有限元、中空玻璃胶、水密等），全部依赖 `HWKKernal.dll`。

## 2. 引擎对象模型（`EXPORT`，`HWKSciCal.dll` 605 个导出）

| 角色 | 符号（原样） | 说明 |
| --- | --- | --- |
| 表达式基类 | `?eval@CXMap@XYUtil@@UEAAPEAV12@AEBV?$CXDict@VCXMap@XYUtil@@@2@@Z` | `CXMap::eval(CXDict<CXMap>&)` → 返回 `CXMap*`，核心求值虚函数 |
| 派生/化简 | `?derive@…`, `?simplify@CXMap…`, `?simplifyFunction@…` | 表达式变换 |
| 解析 | `?parse@CXMap@XYUtil@@SAPEAV12@VString@2@@Z`, `?doParseString@…` | 文本表达式 → 节点树 |
| 直接求值入口 | `?doEval_Double@CXMap@XYUtil@@QEBANXZ`, `doEval_Bool`, `doEval_String`, `doEvalVariant`, `doEvalString` | 一次性求值包装 |
| 名称工厂 | `?functionFactory@CXMap@XYUtil@@SAPEAV12@AEBVString@2@@Z` | **名字 → 节点实例**，注册表与求值之间的枢纽 |
| 命名登记 | `?setName@CXMap@XYUtil@@QEAAXAEBVString@2@_NPEAV?$CXDict@VCXMap@XYUtil@@@2@@Z` | 注册适配层调用的就是这个 |
| 参数访问 | `?nArgs@`, `?parameters@`, `?parameter@`, `?argument@`, `?checkParamTypes@`, `?evalParams@` | 形参/实参与类型检查 |
| 自省 | `?name@`, `?string@`, `?tstr@`, `?help@`, `?htmlString@`, `?desc@`, `?isA@`, `?isKindOf@` | 节点自描述（跟踪文本 `Name(%1,%2)` 即此类产物） |
| 类型判定 | `?isConstant@`, `?isInternal@`, `?isOperatorType@`, `?isMatrixType@`, `?isStringType@`, `?isPointerType@` | 节点种类 |

节点子类（各有 `X_Map_Runtime_Class@CX…` 静态运行时类 + `desc()` + `cast()`）：

| 子类 | 语义（依据符号名） | 备注 |
| --- | --- | --- |
| `CXConstant` | 常量；`add/sub/mul/div/pow/less/large/equal/nequal` 静态运算 | 符号级运算重载 |
| `CXVariable` | 变量 | `derive` 走单独实现 |
| `CXOperator` | 二元运算符节点；`GetTree1/GetTree2` | 显式二叉树 |
| `CXMatrix` / `CXTMatrix` | 矩阵/张量节点；`at(i)`, `at(i,j)`, `set(i,j,…)` | 荷载与内力用 |
| `CXPointerContainer` | 指针容器 | |
| `CXStringDefine` | 字符串定义 | |
| `CXMapInternal` | 内部节点 | |
| `CXMapVariableArguments` / `CXParameter` | 可变参数节点与形参 | `addParameterName`, `argumentIndex` |
| `CXMapDongdong` / `CXMapDongdongPtr` | **加密狗访问**（`DoCheckLockLib`, `DoOpen`, `DoClose`, `DoCommand`, `DoRandomTestValue`, `UpdateMyComputerTime`, `GetMapInfo`） | 许可门控可能进入求值路径，未验证 |

全局注册表（`EXPORT`）：

- `?m_pDictMaps@CXMap@XYUtil@@2PEAV?$CXDict@VCXMap@XYUtil@@@2@EA` — 名字字典指针（全 static）
- `?g_lpMapRuntimeClassListHead@@3PEAVCXMapRuntimeClass@@EA` — 节点类运行时链表头
- `?GetDictMap@CXInterpreter@XYUtil@@QEAAAEAV?$CXDict@VCXMap@XYUtil@@@2@XZ` — 取解释器字典
- `?getprocessmap@CXInterpreter@XYUtil@@QEAAPEAVCXMap@2@AEBVString@2@_N@Z` — 按名字取节点

## 3. 命名条目层（`STRING` + `DISASM` + `DECOMP`）

登记入口（`EXPORT`）：`?InitNewFunction@XYUtil@@YAXPEAVCXInterpreter@1@@Z` @ `0x1802e4330`（HWKWallUtil.dll）。

`DECOMP` 实测函数体只有 4 步（evidence_id `ev_45106813…`）：

```c
void __cdecl XYUtil::InitNewFunction(CXInterpreter *param_1) {
  _Var1 = _time64(0);            // 时间种子
  FUN_180331af0(_Var1);          // 播种：混合后写入 DAT_1805573f0，再 FUN_180331c80(seed)
  XYUtil::CXInterpreter::SwitchDictMap(param_1);
  FUN_1802d8960(param_1);        // 批量 CXMap::setName
}
```

条目规模（`DISASM` + `STRING`，`migration_workspace/raw/cxmap-entries.json`、`cxmap-bindings.json`）：

| 注册函数 | 调用点 | 有名字 | 已绑定实现 |
| --- | --- | --- | --- |
| `FUN_1802d8960`（0x2d8960–0x2e4321） | 308 | 290 | 290 |
| `FUN_1802d4fc0` | 89 | 89 | 89 |
| `FUN_18025ec40` | 1 | 0（动态名） | 0 |
| 合计 | 398 | 379 字面量 + 1 动态 | 379 |

- 290 条在 `FUN_1802d8960` 内**全部**绑定到各自独立的构造实现函数（零复用）；
  `FUN_1802d4fc0` 的 89 条同样全部绑定。合计 **379 条字面量名字 → 379 个不同实现函数**。
- 第 380 条 `prefix` **不是条目名**：`FUN_18025ec40` 从 `evalParams` 里按 key `"prefix"` 取出字符串，
  再用 `operator+(prefix, …)` 拼出动态名字后 `setName`。即存在**运行时拼名的登记**，
  静态扫描会把它误当字面量名字。`FUN_18025ec40` 本身也不是注册器，而是一个节点实现体
  （`ta` 取 1/2/3/4 分支、8 个数值输入、三次幂与 1.1 系数、阈值 3.0、输出 1×4 `CXTMatrix`）。
- 输入个数由跟踪文本 `Name(%1,%2,…)` 推得：1 参 124、2 参 68、3 参 62、4 参 35、5 参 20、
  6 参 7、7 参 4、8 参 3、9 参 1（共 324；另有 56 个条目无跟踪文本）。
- 玻璃家族 6 条：`CalGlassStress`、`CalGlassPSStress`、`CalGlassDisp`、`CalGlassPSDisp`、
  `CalcGlassShadeCoef`、`CalcGlassUFactor`；前四者跟踪文本均为 `(%1,%2,%3,%4)`（4 输入）。
- 四条玻璃实现函数地址严格等距 `0x210`（`0x307300 / 0x307510 / 0x307720 / 0x307930`），
  顺序与注册顺序一致 → 同一模板批量生成的节点类。

## 4. 驱动方式

`HWKKernal.dll` 有 36 个导出以 `CXInterpreter*` 为形参（`EXPORT`），典型：

```
?Process_All@HWKWallContext@@QEAAXPEAVCXInterpreter@XYUtil@@@Z
?Process_All@HWKWallStruct@@QEAAXPEAVCXInterpreter@XYUtil@@@Z
?Process_All@HWKUDataInfos@@QEAAXPEAVCXInterpreter@XYUtil@@@Z
?ProcessMapFormula@HWKWallCheck@@IEAAXPEAVCXInterpreter@XYUtil@@@Z
?ProcessCustomFormula@HWKWallCheck@@IEAAXPEAVCXInterpreter@XYUtil@@@Z
?PostProcess_WallType@HWKWallStruct@@QEAAXPEAVCXInterpreter@XYUtil@@@Z
```

配合 `CXMap::eval(CXDict<CXMap>&)` 与 `doEval_Double`，可判定计算不是"调函数取值"的 API 风格，
而是**建图 → 命名 → eval** 的表达式图风格。`NOT_RUN`：实际调用顺序、时机、失败分支。

## 5. 对替代实现的影响（判断，非结论）

1. 要替代计算体系，必须实现的不只是一个求值器，而是：节点类体系 + 名字注册表 + 表达式解析 +
   `CXDict<CXMap>` 依赖解析 + 单位/量纲（后者**尚未取证**）。
2. 380 个命名条目是当前可量的语义面上限；其中 324 个的输入个数已知，实现函数 290 个已知。
3. `CXMap::functionFactory(name)` 是"注册名 → 节点"的唯一枢纽，替代实现可以此为最小切面。
4. `CXMapDongdong` 说明许可检查就在引擎模块内，可能影响求值可用性——必须先取证再设计。

## 6. 未完成（逐项保留）

| 项 | 状态 | 说明 |
| --- | --- | --- |
| `FUN_1802d4fc0` / `FUN_18025ec40` 的 90 条绑定 | NOT_RUN | 反编译在途 |
| `CXMap::functionFactory`（`0x180021560`）实现 | NOT_RUN | 反编译在途 |
| `CXMap::setName`（`0x180023e60`）bool 语义 | NOT_RUN | 反编译在途 |
| `CXMap::eval`（`0x180021210`）依赖解析 | NOT_RUN | 反编译在途 |
| `doEval_Double`（`0x180020930`）数值精度路径 | NOT_RUN | 反编译在途 |
| 单个节点（如 `FUN_180307300` = CalGlassDisp）内部算法 | NOT_RUN | 未反编译 |
| 单位/量纲、容差、异常路径 | NOT_RUN | 无任何证据 |
| 与 `.cwx` 工程文件的公式文本关系 | NOT_RUN | 未取证 |
| 原版运行下的求值结果 | NOT_RUN | 需 B02 环境 |

---

## 7. 引擎求值链路（`DECOMP` 实测，2026-10-18 补）

四条核心函数已反编译，证据 id：`functionFactory` `ev_b27a76d7…`、`setName` `ev_66eb0fe5…`、
`CXMap::eval` `ev_7529cd57…`、`doEval_Double` `ev_b47d79ec…`。

### 7.1 注册是真的注册"原型实例"，不是构造函数指针

```c
CXMap *XYUtil::CXMap::functionFactory(String *param_1) {
  plVar1 = XYUtil::CXGDict::look_string((CXGDict *)m_pDictMaps, param_1, 0, 0);
  if (plVar1 != 0) { return (*(**(code **)(*plVar1 + 0x20)))(plVar1); }   // 虚表 +0x20 = 克隆
  return 0;
}
```

`m_pDictMaps`（全局 `CXDict<CXMap>`）里存的是**节点对象本身**，工厂查到后调虚表 `+0x20`
（`copy()`）返回副本。所以注册的是原型，取用时克隆——不是"名称→构造器"的映射。

### 7.2 `setName` 的语义（bool 参数已确认）

```c
XYUtil::String::operator=((String *)(this + 0x18), param_1);   // 名字存在对象 +0x18
XYUtil::String::stripWhiteSpaces((String *)(this + 0x18));     // 名字去空白
if (名字非空 && param_2)
    XYUtil::CXGDict::look_string(param_3, (String *)(this + 0x18), this, 2);  // 模式 2 = 插入
```

- `bool` = **是否写入字典**；380 条注册全是 `true`，说明这是"登记"路径而非"仅改名"。
- 名字会被 `stripWhiteSpaces` 规范化 → 名字比较前应假设去空白。
- 模式 `2` 具体是覆盖还是追加，`look_string` 未反编译，`NOT_RUN`。

### 7.3 `CXMap::eval` 的依赖求值

```c
this_00 = evalParams(this, param_1);          // 先求所有形参
plVar6  = *(longlong **)(this + 0x38);        // 节点 +0x38 = 表达式树指针
if (plVar6 == 0) { Debug::log("CXMap(%1=%2)::eval with tree==0L, this should never happen …");
                   _CxxThrowException(...); }  // 树为空直接抛异常
pCVar4  = (*(plVar6 + 0x40))(plVar6, this_00); // 树 -> eval(dict)
cVar3   = (*(*pCVar4 + 0x68))(pCVar4);         // 是否为常量
if (!常量 && 名字非空) {
    look_string(dict, "$$__noEvaluateFunctions"); // 符号求值开关
    if (开关存在 && this[8]==0) 返回自身副本，保留表达式
}
```

要点：

- 求值顺序是**先求形参再求本节点**（`evalParams` 在前），即拉取式依赖驱动。
- 节点对象字段：`+0x18` 名字（`String`）、`+0x38` 表达式树、`+0x08`/`+0x20` 另有标志与计数。
- 存在 `$$__noEvaluateFunctions` **符号模式**：置位时非叶节点不求值、返回表达式副本。
  这意味着同一套节点既能算数值也能保持符号表达式——替代实现必须区分这两种模式。
- 树为空是"不应发生"路径：直接 `Debug::log` + `_CxxThrowException`（异常类型来自 `DAT_180055378`）。

### 7.4 数值取值路径

`doEval_Double` 自己构造一个 `CXGDict(0x11,0,true,false)`，再调虚表 `+0x40` 求值，
最后从结果对象的 **`+0x8` 偏移取 `double`**（与节点实现体里 `*(double *)(lVar15 + 8)` 一致）。
`0x11` 参数含义、以及非 double 类型的取用规则：`NOT_RUN`。

### 7.5 原始源码目录结构（`STRING` 实测，来自 `__FILE__` 断言串）

调试日志把原始编译路径留在二进制里，可反推原工程分模块源码目录：

| 模块 | 源码根 | 独立 `.cpp` 数 | 样例 |
| --- | --- | --- | --- |
| `HWKSciCal.dll` | `f:\hwkxwallu\xwall\hwkscical\` | 13（+1 个 `hwkutil\array.h`） | `xmap.cpp`、`xinterpreter.cpp`、`xtmatrix.cpp`、`xoperator.cpp`、`xvariable.cpp`、`xmapvararg.cpp`、`xmapdongdong.cpp`、`pluginmanager.cpp`、`getok.cpp` |
| `HWKWallUtil.dll` | `f:\hwkxwallu\xwall\hwkwallutil\` | 38 | `awning3dprob.cpp`、`clayplate3dprob.cpp`、`railing3dprob.cpp`、`fe*`（20+ 个 FE 文件）、`getalpha.cpp`、`getfa.cpp`、`fesetload.cpp` |
| `HWKKernal.dll` | `f:\hwkxwallu\xwall\hwkkernal\` | 11（仅断言点覆盖到的） | `hwkbeamex.cpp`、`hwkcornerpole.cpp`、`hwkanalysisofcylinder.cpp` |

这些路径是**编译期绝对路径**，说明原工程代码根为 `f:\hwkxwallu\xwall\`，引擎目录名 `hwkscical`
（= HWK Sci Cal），与 DLL 名对应。FE（有限元）代码集中在 `hwkwallutil\fe*.cpp`，与第 3 节
114 个 `FEAdd*` 条目同源。

### 7.6 仍未取得

| 项 | 状态 |
| --- | --- |
| `look_string` 模式 `2` 的确切语义 | NOT_RUN |
| `evalParams` 内部（形参求值、循环引用检测） | NOT_RUN |
| `CXGDict(0x11,…)` 参数含义 | NOT_RUN |
| 节点实现体（如 `FUN_180307300` = CalGlassDisp）算法 | 反编译在途 |
| 单位/量纲、容差、异常分支 | NOT_RUN |
| 原版运行数值对照 | NOT_RUN（需 B02 环境） |

---

## 8. 节点类层：379 个类，379 个独立实现（`DISASM` 批量提取）

方法（可复用）：基类 `??_7CXMap@XYUtil@@6B@`（HWKSciCal.dll `0x180040e68`）的 **槽 8 = `eval`**
（槽值等于导出 `?eval@CXMap@XYUtil@@UE…` `0x180021210` 已验证）。对每个构造函数取其实写入对象首字段的
vftable 地址，逐槽与基类比对，即可批量得到每个节点的 `eval` 覆盖地址，无需逐个反编译。

产出：`migration_workspace/node-vtables.md`、`raw/node-vtables.json`。

| 指标 | 值 |
| --- | --- |
| 条目数 | 379 |
| 提取到 vftable | 379（100%） |
| eval 覆盖基类 | 379（100%） |
| **不同 vftable 地址** | **379** |
| **不同 eval 地址** | **379** |

玻璃家族实测：

| 条目 | 构造 | vftable | eval |
| --- | --- | --- | --- |
| `CalGlassDisp` | `FUN_180307300` | `0x1804190a0` | `0x1803081c0` |
| `CalGlassPSDisp` | `FUN_180307510` | `0x180419170` | `0x1803087b0` |
| `CalGlassStress` | `FUN_180307930` | `0x180418f00` | `0x1803097c0` |
| `CalGlassPSStress` | `FUN_180307720` | `0x180418fd0` | `0x180308f90` |
| `GetKuz` | `FUN_180253aa0` | `0x180402838` | `0x18025d200` |
| `GetKuzcal` | `FUN_180253c70` | `0x180401728` | `0x18025d640` |
| `CalcGlassShadeCoef` | `FUN_180033f60` | `0x1803d9df0` | `0x1800419d0` |
| `CalcGlassUFactor` | `FUN_180034140` | `0x1803d9b80` | `0x180042070` |

结论（对替代方案是硬约束）：**379 个名字 = 379 个类 = 379 个不同的 eval 实现，零复用。**
不存在"通用节点 + 配置表"的结构；替代实现必须逐个实现这 379 个 eval，
或者证明某个子集可以用统一模型等价表达（后者需要逐个差分验证，不能假定）。

`CalGlassDisp` 的参数名表由构造函数实测（`DECOMP` `ev_36304e39…`）：
`ms`, `qwk`, `aw`, `dw`, `theta`, `prefix`, `def` —— 共 7 个具名参数，
与跟踪文本 `CalGlassDisp(%1,%2,%3,%4)` 的 4 个位置不一一对应（跟踪文本只打印前 4 个），
两者关系 `NOT_RUN`。

---

## 9. 第一个节点的完整算法：`CalGlassDisp::eval`（`DECOMP` `ev_9910259c…`）

反编译地址 `0x1803081c0`（由第 8 节 vtable 槽 8 得到）。函数体 7.2KB，结构可直接归纳：

### 9.1 节点 eval 的统一模板

```c
CXConstant *CalGlassDisp::eval(CXMap *this, CXDict<CXMap> *dict) {
  Time::Time(&t, true); uVar3 = Time::getTickCount(&t);        // ① 计时
  f = (float)FUN_180331b80();                                  // ② 取一个随机浮点
  if ((int)(f * 89.0) == 0x2c) CXMap::GetHMMxValue(uVar3);      // ③ 随机许可校验
  d = evalParams(this, dict);                                  // ④ 先求形参
  ms=look("ms"); qwk=look("qwk"); aw=look("aw"); dw=look("dw");
  theta=look("theta"); prefix=look("prefix"); def=look("def");  // ⑤ 按名取 7 个参数
  if (任一为空) { 新建 CalGlassDisp 节点并把 0..6 号实参按声明顺序绑上; return 它; }  // ⑥ 符号回退
  /* ⑦ 数值计算 */
  v = ms * qwk * pow(aw, 4.0) / dw * theta * 1000000000.0;
  r1 = new CXConstant(v);                    // 无名字
  r2 = new CXConstant(v, prefix + def);      // 带名字的输出
  return r1/r2;
}
```

### 9.2 实测算术表达式（事实，非推断）

```
结果 = ms × qwk × aw⁴ ÷ dw × theta × 1e9
```

对应伪代码：

```c
dVar18 = pow(*(double *)(lVar12 + 8), 4.0);                       // aw^4
dVar18 = ((qwk * ms * dVar18) / dw) * theta * 1000000000.0;
```

`1e9` 是硬编码常量；`aw` 取 4 次幂（`pow(x,4.0)`，不是 x*x*x*x，逐位结果可能不同）。
**物理含义未与原版规范或计算书对照，不作断言。**

### 9.3 参数顺序实测（两个独立证据一致）

构造函数 `FUN_180307300` 传入的顺序与 eval 里"缺参数回退"绑定 `0..6` 的顺序完全一致：

| 索引 | 名字 |
| --- | --- |
| 0 | `ms` |
| 1 | `qwk` |
| 2 | `aw` |
| 3 | `dw` |
| 4 | `theta` |
| 5 | `prefix` |
| 6 | `def` |

跟踪文本 `CalGlassDisp(%1,%2,%3,%4)` 只打印 **前 4 个**（`ms, qwk, aw, dw`），
`theta/prefix/def` 不出现 —— 这解释了第 8 节里"7 个参数 vs 4 个占位符"的差异。

### 9.4 随机许可校验（重要）

```c
f = (float)FUN_180331b80();             // RNG，种子来自 FUN_180331af0（_time64 播种）
if ((int)(f * 89.0) == 0x2c)            // 0x2c = 44，约 1/89 ≈ 1.1% 命中
    CXMap::GetHMMxValue(getTickCount()); // 硬件锁（HMM）交互
```

- 该校验**不参与返回值**：`dVar18` 只由 7 个参数决定，上述调用是副作用。
- 但它**依赖时间**（`Time::getTickCount`）且**按概率触发**，意味着同一工程连续求值时的
  外部调用次数不确定 —— 影响可复现性测试与性能测量，不影响数值结果（在返回值层面）。
- `GetHMMxValue` 内部行为：`NOT_RUN`。

### 9.5 该模板对另外 378 个节点的可复用性

第 8 节已给出全部 379 个 `eval` 地址。结合本节模板，逐个节点的阅读成本可按"取参 → 缺失回退 →
算术表达式"三段切分，不需要每次从汇编重建上下文。**但模板只是阅读脚手架，不代表各节点算法同构**——
本节只实测了 `CalGlassDisp` 一个。
