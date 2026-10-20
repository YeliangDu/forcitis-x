# 节点算式抽取（L5 / A 路线，机械替换，未做语义推断）

- 输入：`migration_workspace/raw/nodes/*.rea.json`（379 份）
- 状态分布：`EXPR`=51、`FE_OP`=12、`INTERPOLATION`=4、`NO_ARITH`=259、`PARTIAL`=31、`SELECTED`=1、`STRING_TABLE`=3、`TABLE_BUILDER`=2、`TABLE_LOOKUP`=15、`VARARG_GET`=1
- 失败：0

规则（`CalGlassDisp` 已人工核对，见 `calculation-core.md` §9）：

1. `String::String(<local>,"名")` → `local` 绑定该参数名；
2. 随后 `look_string(…, <local>, …)` 的结果变量绑定同名参数（含 `local_x = pVar5;` 别名）；
3. `X = **(code **)(*W + 0xa8))(…)` 是该参数的数值对象，`*(double *)(X + 8)` 为数值；
4. `dVar/fVar = …` 逻辑语句按出现顺序代入（多行表达式先拼接）。

`p[变量]` = 该取值变量未能绑定到参数名，**保持未知、不猜**。

| 节点 | 状态 | 解析到的参数名 | 代入后的表达式 |
| --- | --- | --- | --- |
| `CalGlassDisp` | EXPR | `aw`, `def`, `dw`, `ms`, `prefix`, `qwk`, `theta` | `((qwk * ms * (pow(aw,4.0))) / dw) * theta * 1000000000.0` |
| `CalGlassPSDisp` | EXPR | `aw`, `def`, `dw`, `ms`, `num`, `prefix`, `qwk`, `theta` | `((qwk * ms * (pow(aw,4.0))) / dw) * theta * 1000000000.0` |
| `CalGlassPSStress` | EXPR | `aw`, `def`, `num`, `prefix`, `qw`, `sw`, `theta`, `tw` | `(((sw * 6.0 * qw * 1000.0 * aw * aw) / tw) / tw) * theta` |
| `CalGlassStress` | EXPR | `aw`, `def`, `prefix`, `qw`, `sw`, `theta`, `tw` | `(((sw * 6.0 * qw * 1000.0 * aw * aw) / tw) / tw) * theta` |
| `GetAAs1` | EXPR | `M`, `N`, `V`, `ab`, `ar`, `av`, `fy`, `z` | `(V) / (av) + (N) / ((ab) * 0.8 * (fy)) + (((M) - -(N) * 0.4 * (z)) / ((ar) * 1.3 * (ab) * (fy) * (z)) + ((V) - -(N) * 0.3) / (av)) / ((ar) * 1.3 * (ab) * (fy) * (z))` |
| `GetAAs2` | EXPR | `M`, `N`, `ab`, `ar`, `fy`, `z` | `(M) / (((M) - ABS((N)) * 0.4 * (z)) / ((ar) * 0.4 * (ab) * fy * (z))) + (N) / ((ab) * 0.8 * fy)` |
| `GetAMJRatio` | EXPR | `diameter`, `thickness` | `0.8 - (((thickness) - (diameter) * 3.0) * 0.1) / ((diameter) + (diameter))` |
| `GetAddDRm` | EXPR | `$0`, `$1` | `$0 * 0.001` |
| `GetAddHs` | EXPR | `$0`, `1/%1` | `(0.0) + 1.0 / $0[pCVar14]` |
| `GetArchShapeRatio` | EXPR | `L`, `f`, `type` | `(((f) - 0.1) / 0.1) * 0.8 - 0.8` |
| `GetArchSnowRatio` | EXPR | `L`, `f` | `(L / (f)) * 0.125` |
| `GetAvKValue` | EXPR | `ga`, `gk`, `pa`, `pk` | `pa + ga` |
| `GetBeamDflim` | EXPR | `$0`, `$1`, `$2`, `GLOB_LC_SHJS` | `(((1.0 / (GLOB_STEELLIMIT)) - 2.0) * 120.0) / 2.5 + 180.0` |
| `GetBeamDfnum` | EXPR | `$0`, `$1`, `$2`, `GLOB_LC_SHJS` | `((($2) - 2.0) * 120.0) / 2.5 + 180.0` |
| `GetBeamTriHeight` | EXPR | `beamcalmode`, `bfecal`, `height`, `width` | `height * 0.5` |
| `GetBoltNRatio` | EXPR | `$0`, `$1` | `1.1 - (($0) / $1) / 150.0` |
| `GetBoltPullState` | EXPR | `myc`, `n` | `(n) - myc` |
| `GetBoltVXYNum` | EXPR | `$0` | `(0.0) + $0[pCVar15]` |
| `GetCLayoutSMin` | EXPR | `$0` | `sqrt(((($0) - ($0)) * (($0) - ($0)) + ($0 - ($0)) * ($0 - ($0))))` |
| `GetDSlopeShapeRatio` | EXPR | `D`, `DM`, `FM`, `H`, `angle`, `rtype` | `((180.0 - (angle)) - 15.0) * 0.03333333333333333 + 0.2` |
| `GetDflim` | EXPR | `$0`, `$1`, `$2`, `GLOB_LC_SHJS` | `1.0 / ((((1.0 / (GLOB_STEELLIMIT)) - 3.6) * 45.0) / 0.8999999999999999 + 180.0)` |
| `GetDfnum` | EXPR | `$0`, `$1`, `$2`, `GLOB_LC_SHJS` | `((($2) - 3.6) * 45.0) / 0.8999999999999999 + 180.0` |
| `GetHDr` | EXPR | `$0`, `$1` | `(0.0) + (1.0 / ($0 + $1))` |
| `GetHc` | EXPR | `$0`, `$1` | `(((((pow($0 / 1000.0,3.0)) * ($1[5]) * ($1[5]) * 9.8 * (1.0 / ($1[3] + 273.15)) * $1[8] * 1000.0 * $1[4]) / ($1[6] * 1e-05 * $1 * 0.01)) * $1 * 0.01) / $1) * 1000.0` |
| `GetHr` | EXPR | `$0`, `$1`, `$2` | `(2.268e-07 / ((1.0 / ($0[pCVar20]) + 1.0 / ($0[pCVar20])) - 1.0)) * (pow($1 + 273.15,3.0))` |
| `GetIz` | EXPR | `$0`, `$1` | `pow($1 / 10.0,-(double)0.3)` |
| `GetLPAngle` | EXPR | `PRJ`, `angle` | `((tan(((tan(((atan((tan(((0.0) * (angle)) / 180.0)) / (sin((0.0) / 3.0)))) * (tan(((0.0) * (angle)) / 180.0))) / 180.0)) * *(double *)PI_exref) / 180.0)) * *(double *)PI_exref) / 180.0` |
| `GetNextAirIndex` | EXPR | `$0`, `$1`, `$2` | `((1.0 / ($2[3] + 273.15)) * ($2[5]) * ($2[5]) * (pow($1 / 1000.0,3.0)) * 9.8 * $2[8] * 1000.0 * $2[4]) / (*(double *)((longlong)local_250 + 8) * 1e-05 * $2 * 0.01)` |
| `GetOuterThicknessOfHollowGlass` | EXPR | `ta` | `(0.0) + (ta[6])` |
| `GetPoleDflim` | EXPR | `$0`, `$1`, `$2`, `GLOB_LC_SHJS` | `1.0 / ((((1.0 / (GLOB_STEELLIMIT)) - 3.6) * 45.0) / 0.8999999999999999 + 180.0)` |
| `GetPoleDfnum` | EXPR | `$0`, `$1`, `$2`, `GLOB_LC_SHJS` | `((($2) - 3.6) * 45.0) / 0.8999999999999999 + 180.0` |
| `GetRGlass` | EXPR | `prefix`, `ta` | `((ta[4]) * 1.1) / ((ta[2]) + (((((ta[0]) * 1.1) * ((ta[0]) * 1.1) * ((ta[0]) * 1.1)) * 1.1) * ((((ta[0]) * 1.1) * ((ta[0]) * 1.1) * ((ta[0]) * 1.1)) * 1.1) * ((((ta[0]) * 1.1) * ((ta[0]) * 1.1) * ((ta[0]) * 1.1)) * 1.1)) + (ta[4]) + (ta[…` |
| `GetSSlopeShapeRatio` | EXPR | `FM`, `angle`, `rtype` | `((180.0 - (angle)) - 15.0) * 0.02666666666666666 - 1.2` |
| `GetShapeCoefCalc` | EXPR | `a`, `fv`, `vv`, `zf`, `zv` | `(fv) - (((a) * ((zv) * 0.8 - (zv))) / 1.4 + (zv) + ((((a) * ((fv) * 0.8 - (fv))) / 1.4 + (fv)) - (vv)))` |
| `GetSlopeShapeRatio` | EXPR | `a`, `type` | `((a) - 5.0) * -0.05 - 2.0` |
| `GetSlopeSnowRatio` | EXPR | `a` | `1.0 - ((180.0 - (360.0 - (a))) - 25.0) * 0.03` |
| `GetSlopeWKP` | EXPR | `bgz`, `shapes`, `uz`, `w0`, `wlimintNeg`, `wlimitPos` | `(bgz) * uz * w0 * (bgz)` |
| `GetStabFactor` | EXPR | `lambda`, `sectype` | `(lambda) * 0.65` |
| `GetStoneBoardAl` | EXPR | `Bsl`, `Bw`, `Hsl`, `Hw`, `LINKSIDE`, `SLOTTYPE`, `SlotCount` | `((Bw) - (Bsl + Bsl) * 0.001) - (Bsl + Bsl) * 0.001` |
| `GetStoneBoardBl` | EXPR | `Bsl`, `Bw`, `Hsl`, `Hw`, `LINKSIDE`, `SLOTTYPE`, `SlotCount` | `((Bw) - (Bsl + Bsl) * 0.001) - (Bsl + Bsl) * 0.001` |
| `GetTFromDB` | EXPR | `$0` | `pow(10.0,$0 / -10.0)` |
| `GetTeglass` | EXPR | `ta` | `((ta[0]) * 0.95) * ((ta[0]) * 0.95) * ((ta[0]) * 0.95)` |
| `GetTrueNvf` | EXPR | `D`, `f`, `t`, `t1` | `((((t) * 2.4 * (D) * (f)) - (f)) * ((t1) - 1.0)) / 1.5 + (f)` |
| `GetUSupportReForce` | EXPR | `mat1`, `mat2`, `n0`, `n1`, `name`, `truesimple` | `(mat1) + mat1` |
| `GetWFD` | EXPR | `B`, `E`, `H`, `I`, `T`, `mlen`, `wf` | `(((pow(_X,4.0)) * (((pow((H),4.0)) * (((3.125 - (((B) * 0.5) / (H)) * (((B) * 0.5) / (H)) * 5.0) + ((pow(((B) * 0.5),4.0)) + (pow(((B) * 0.5),4.0))) / (pow((H),4.0))) * (((pow((H),4.0)) * (wf)) / ((E) * 240.0 * (I))))) / ((E) * 120.0 * (…` |
| `GetWFM` | EXPR | `B`, `H`, `T`, `mlen`, `wf` | `(((H) - (mlen)) * 0.5) * (wf) * (((H) - (mlen)) * 0.5) * 0.5` |
| `GetWFQ` | EXPR | `B`, `H`, `T`, `mlen`, `wf` | `(H) * (((H) - (B)) * (wf) * 0.5 + (B) * (wf) * 0.25) * 0.25` |
| `GetWallUValue` | EXPR | `CWALLU_HASFRAME`, `CWALLU_HASGLASS`, `CWALLU_HASGLASSEDGE`, `CWALLU_HASPANELEDGE`, `CWALLU_HASPANNEL`, `CWALLU_TAREA`, `CWALLU_UAREA`, `areas`, `kvalues`, `types` | `((areas[pCVar25] * types[pCVar25]) + (0.0)) / ((0.0) + areas[pCVar25])` |
| `GetWeldNMVF` | EXPR | `mfx`, `mfy`, `nfa`, `vfa` | `sqrt((((vfa) + (mfy)) / 1.22) * (((vfa) + (mfy)) / 1.22) + (nfa + (mfx)) * (nfa + (mfx)))` |
| `GetWeldNMVI` | EXPR | `b`, `hf`, `index`, `length` | `((((b) * (b) * (b)) / 12.0) - (((((b) * (b) * (b)) / 12.0) * (((b) * (b) * (b)) / 12.0)) / ((((b) * (b) * (b)) / 12.0) + (((b) * (b) * (b)) / 12.0) + (b)))) - (((b) * (b) * (b)) / 12.0) * 0.5` |
| `StartAirIndex` | EXPR | `$0`, `$1`, `$2` | `((1.0 / ($2 + 273.15)) * ($1[5]) * ($1[5]) * (pow($0 / 1000.0,3.0)) * 9.8 * $1[8] * 1000.0 * $1[4]) / (*(double *)((longlong)local_250 + 8) * 1e-05 * $1 * 0.01)` |
| `AwningAddProb` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `AwningDelProb` | NO_ARITH | `handle` | `—` |
| `CalcGlassShadeCoef` | NO_ARITH | `calcinfo`, `calrad`, `gopparam`, `handle`, `layids`, `thicks` | `—` |
| `CalcGlassUFactor` | NO_ARITH | `calcinfo`, `calrad`, `gopparam`, `handle`, `layids`, `thicks` | `—` |
| `CheckHasHollowBeforeLayer` | NO_ARITH | `layer`, `ta` | `—` |
| `CheckPoleIsSimpleSup` | NO_ARITH | `poleinfo` | `—` |
| `ClayPlateAddProb` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `ClayPlateDelProb` | NO_ARITH | `handle` | `—` |
| `DoCalcAwning3d` | NO_ARITH | `GAK`, `bz`, `drawsize`, `hand`, `loads`, `material`, `model` | `—` |
| `DoCalcClayPlate3d` | NO_ARITH | `bz`, `drawsize`, `hand`, `loads`, `material`, `model` | `—` |
| `DoCalcRailing3d` | NO_ARITH | `Come Here 17`, `Come Here 18`, `Come Here 19`, `Come Here 20`, `Come Here 21`, `bz`, `drawsize`, `hand`, `hmaterial`, `loads`, `model`, `vmaterial` | `—` |
| `DoCalcShell` | NO_ARITH | `MODEL`, `bz`, `hand`, `shellinfo`, `thickinfo` | `—` |
| `DoDrawVSec` | NO_ARITH | `bz`, `secdata` | `—` |
| `DoGetAwning3dReaction` | NO_ARITH | `GAK`, `gkindex`, `hand`, `loads`, `material`, `model`, `nodeindex` | `—` |
| `DoGetAwning3dReactionInfo` | NO_ARITH | `GAK`, `hand`, `loads`, `material`, `model` | `—` |
| `DoGetAwning3dReactionMatrix` | NO_ARITH | `GAK`, `hand`, `loads`, `material`, `model` | `—` |
| `DrawGlassTempInfo` | NO_ARITH | `calcinfo`, `calrad`, `layids`, `sgopparam`, `shandle`, `thicks`, `ugopparam`, `uhandle` | `—` |
| `DrawGlassUInfo` | NO_ARITH | `calcinfo`, `calrad`, `funccode`, `layids`, `thicks`, `ugopparam`, `uhandle` | `—` |
| `DrawHoldingBlock` | NO_ARITH | `D`, `H`, `H0`, `L`, `L0`, `T`, `UpDown` | `—` |
| `DrawWallUTable` | NO_ARITH | `areas`, `descs`, `kvalues`, `type`, `types` | `—` |
| `DtoK` | NO_ARITH | `$0` | `—` |
| `FEAddAnaOfAluBoardProb` | NO_ARITH | `$0`, `x` | `—` |
| `FEAddAnaOfCylinderProb` | NO_ARITH | `$0`, `x` | `—` |
| `FEAddAnaOfQuadMindlinSProb` | NO_ARITH | `$0`, `x` | `—` |
| `FEAddBDLoad` | NO_ARITH | `BID`, `epos`, `hand`, `lcid`, `loadcase is empty! add loadcase first`, `name`, `spos`, `val` | `—` |
| `FEAddBFLoad` | NO_ARITH | `BID`, `hand`, `lcid`, `loadcase is empty! add loadcase first`, `name`, `pos`, `val` | `—` |
| `FEAddBTDLoad` | NO_ARITH | `BID`, `epos`, `hand`, `lcid`, `loadcase is empty! add loadcase first`, `name`, `spos`, `val` | `—` |
| `FEAddBTULoad` | NO_ARITH | `BID`, `epos`, `hand`, `lcid`, `loadcase is empty! add loadcase first`, `name`, `spos`, `val` | `—` |
| `FEAddBeamExModelProb` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `FEAddBoardModelProb` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `FEAddCBProb` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `FEAddCFrameModelProb` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `FEAddGBeamModelProb` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `FEAddGOPProb` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `FEAddGraphModelProb` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `FEAddLnkNetProb` | NO_ARITH | — | `—` |
| `FEAddLnkTrussProb` | NO_ARITH | — | `—` |
| `FEAddLoadcase` | NO_ARITH | `hand`, `name` | `—` |
| `FEAddMat` | TABLE_LOOKUP | `hand`, `mname` | `table[fun_1802798d0](uVar14) + table[fun_1802793c0](uVar14,3) + table[fun_180276eb0](uVar14,3)` |
| `FEAddNode` | NO_ARITH | `DOF`, `IsCon`, `hand`, `name`, `rg`, `x`, `xg`, `y`, `yg` | `—` |
| `FEAddPlaneStressProb` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `FEAddProb` | NO_ARITH | `$0`, `$1` | `—` |
| `FEAddShellProb` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `FEAddThermProb` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `FEAddUnregLnkNetProb` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `FEAddVFrameModelProb` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `FEAnalysisOfAluBoard` | NO_ARITH | `bz`, `drawsize`, `hand`, `model` | `—` |
| `FEAnalysisOfCylinder` | NO_ARITH | `bz`, `drawsize`, `hand`, `model` | `—` |
| `FEAnalysisOfQuadMindlinSimple` | NO_ARITH | `bz`, `drawsize`, `hand`, `model` | `—` |
| `FEArchDraw` | NO_ARITH | `GK1MAXDISP`, `GK1MAXSTRESS`, `GK2MAXDISP`, `GK2MAXSTRESS`, `GK3MAXDISP`, `GK3MAXSTRESS`, `drawbz`, `drawsize`, `hand`, `loads`, `poleinfo`, `sec` | `—` |
| `FEBIniSecData` | NO_ARITH | `hand` | `—` |
| `FEBeamDraw` | NO_ARITH | `beaminfo`, `drawbz`, `drawsize`, `hand1`, `hand2`, `loads`, `sec1`, `sec2` | `—` |
| `FECBeamDraw` | VARARG_GET | `cbeaminfo`, `drawbz`, `hand`, `loads`, `mat`, `prefix`, `sec` | `INTERP(fun_180112570) + INTERP(fun_1801126f0) + INTERP(fun_180112760)` |
| `FEClear` | NO_ARITH | `hand` | `—` |
| `FEClearBLoad` | NO_ARITH | `BID`, `hand` | `—` |
| `FEClearCBProb` | NO_ARITH | `handle` | `—` |
| `FEClearProb` | NO_ARITH | `handle` | `—` |
| `FEDelAnaOfAluBoardProb` | NO_ARITH | `handle` | `—` |
| `FEDelAnaOfCylinderProb` | NO_ARITH | `handle` | `—` |
| `FEDelAnaOfQuadMindlinSProb` | NO_ARITH | `handle` | `—` |
| `FEDelBeamExModelProb` | NO_ARITH | `handle` | `—` |
| `FEDelBoardModelProb` | NO_ARITH | `handle` | `—` |
| `FEDelCBProb` | NO_ARITH | `handle` | `—` |
| `FEDelCFrameModelProb` | NO_ARITH | `handle` | `—` |
| `FEDelGBeamModelProb` | NO_ARITH | `handle` | `—` |
| `FEDelGOPProb` | NO_ARITH | `handle` | `—` |
| `FEDelGraphModelProb` | NO_ARITH | `handle` | `—` |
| `FEDelLnkNetProb` | NO_ARITH | `handle` | `—` |
| `FEDelLnkTrussProb` | NO_ARITH | `handle` | `—` |
| `FEDelLoad` | NO_ARITH | `BID`, `fid`, `hand` | `—` |
| `FEDelPlaneStressProb` | NO_ARITH | `handle` | `—` |
| `FEDelProb` | NO_ARITH | `handle` | `—` |
| `FEDelShellProb` | NO_ARITH | `handle` | `—` |
| `FEDelThermProb` | NO_ARITH | `handle` | `—` |
| `FEDelUnregLnkNetProb` | NO_ARITH | `handle` | `—` |
| `FEDelVFrameModelProb` | NO_ARITH | `handle` | `—` |
| `FEDoAll` | FE_OP | `hand`, `loads`, `mcfginfo`, `mcfgleft`, `mcfgright`, `mcinfo`, `sec` | `CALL(FUN_1800c3270)` |
| `FEDoArchPole` | NO_ARITH | `hand`, `loads`, `poleinfo`, `sec` | `—` |
| `FEDoBeam` | FE_OP | `hand1`, `hand2`, `loads`, `poleinfo`, `polepos`, `sec1`, `sec2` | `CALL(FUN_180087f10, FUN_18008a1f0)` |
| `FEDoBeamEx` | NO_ARITH | `controls`, `drawsize`, `hand`, `loads`, `model`, `polepos`, `widths` | `—` |
| `FEDoBoardAnalysisMitc4` | NO_ARITH | `bz`, `drawsize`, `hand`, `loads`, `model`, `widths` | `—` |
| `FEDoCBeam` | FE_OP | `cbeaminfo`, `hand`, `loads`, `mat`, `sec` | `CALL(FUN_18010e0d0)` |
| `FEDoCFrame` | FE_OP | `containweight`, `drawsize`, `hand`, `loads`, `model`, `polepos`, `widths` | `CALL(FUN_180115fb0)` |
| `FEDoCPole` | FE_OP | `drawsize`, `hand`, `loads`, `model`, `polepos` | `CALL(FUN_18013a8f0)` |
| `FEDoGBeam` | NO_ARITH | `drawsize`, `hand`, `loads`, `model`, `polepos`, `widths` | `—` |
| `FEDoGrilleVPole` | NO_ARITH | `hand`, `loads`, `poleinfo`, `sec` | `—` |
| `FEDoGrilleVPoleDraw` | NO_ARITH | `drawbz`, `drawsize`, `hand`, `loads`, `poleinfo`, `ratio`, `sec` | `—` |
| `FEDoLGAPole` | FE_OP | `hand`, `loads`, `poleinfo`, `polepos`, `pos`, `sec1`, `sec2` | `CALL(FUN_1801626d0, FUN_1801636b0)` |
| `FEDoLinkNet` | NO_ARITH | `bz`, `coninfo`, `hand`, `lnkinfo`, `loads`, `matxinfo`, `matyinfo`, `preloads`, `temps` | `—` |
| `FEDoLinkTruss` | NO_ARITH | `coninfo`, `context`, `hand`, `loads`, `temps`, `widthinfo` | `—` |
| `FEDoLockPointShell` | FE_OP | `bz`, `hand`, `height`, `load`, `shelllockinfo`, `thickinfo`, `width` | `CALL(FUN_1800bf080)` |
| `FEDoPXTPole` | NO_ARITH | `hand`, `loads`, `poleinfo`, `polepos`, `sec` | `—` |
| `FEDoPlaneStressAnalysisMitc4` | NO_ARITH | `bz`, `drawsize`, `hand`, `loads`, `model`, `widths` | `—` |
| `FEDoPole` | NO_ARITH | `hand`, `loads`, `poleinfo`, `polepos`, `sec` | `—` |
| `FEDoShell` | NO_ARITH | `angle`, `bz`, `hand`, `loads`, `shellinfo`, `thickinfo`, `weight` | `—` |
| `FEDoTherm` | NO_ARITH | `bz`, `controlinfo`, `drawline`, `drawsize`, `hand`, `linetemp`, `modelinfo`, `structinfo` | `—` |
| `FEDoUnregLinkNet` | NO_ARITH | `bz`, `calcweight`, `coninfo`, `context`, `drawsize`, `hand`, `loads`, `temps` | `—` |
| `FEDoVFrame` | FE_OP | `containweight`, `drawsize`, `hand`, `loads`, `model`, `polepos`, `widths` | `CALL(FUN_180115fb0)` |
| `FEDoVOLGPole` | FE_OP | `hand`, `height`, `loads`, `poleinfo`, `polepos`, `sec`, `sec2` | `CALL(FUN_1801d2730)` |
| `FEDoVPXTPole` | NO_ARITH | `hand`, `loads`, `poleinfo`, `polepos`, `sec` | `—` |
| `FEDoXTPole` | FE_OP | `hand`, `loads`, `polelength`, `sec` | `CALL(FUN_1801fb1f0)` |
| `FEGetDData` | NO_ARITH | `bid`, `hand` | `—` |
| `FEGetDMax` | NO_ARITH | `bid`, `hand` | `—` |
| `FEGetMData` | NO_ARITH | `bid`, `hand` | `—` |
| `FEGetMMax` | NO_ARITH | `bid`, `hand` | `—` |
| `FEGetPiece` | NO_ARITH | `bid`, `hand` | `—` |
| `FEGetQData` | NO_ARITH | `bid`, `hand` | `—` |
| `FEGetQMax` | NO_ARITH | `bid`, `hand` | `—` |
| `FELGAPoleDraw` | NO_ARITH | `beaminfo`, `drawbz`, `drawsize`, `hand`, `loads`, `pos`, `prefix`, `sec1`, `sec2` | `—` |
| `FEMCDraw` | NO_ARITH | `drawbz`, `hand`, `loads`, `mcfginfo`, `mcfgleft`, `mcfgright`, `mcinfo`, `ratio`, `sec` | `—` |
| `FEMCDrawStress` | NO_ARITH | `ghand`, `gratio`, `hand`, `ratio` | `—` |
| `FEMCGHDoAll` | PARTIAL | `blocknum`, `blocksidedist`, `hand`, `loads`, `mcfginfo`, `mcinfo`, `mcsupinfo`, `sec` | `1e-06 < mcsupinfo` |
| `FEMCGHDraw` | PARTIAL | `drawbz`, `hand`, `loads`, `mcfginfo`, `mcinfo`, `numdispmat`, `ratio`, `sec`, `supinfo` | `1e-06 < supinfo` |
| `FEMCHDoAll` | FE_OP | `hand`, `loads`, `mcfginfo`, `mcinfo`, `sec` | `CALL(FUN_18022c870)` |
| `FEMCHDraw` | NO_ARITH | `drawbz`, `hand`, `loads`, `mcfginfo`, `mcinfo`, `ratio`, `sec` | `—` |
| `FEMCMaxStress` | FE_OP | `ghand`, `gratio`, `hand`, `ratio` | `CALL(FUN_18021f5f0)` |
| `FEPXTPoleDraw` | NO_ARITH | `beaminfo`, `drawbz`, `drawsize`, `hand`, `loads`, `sec` | `—` |
| `FEPoleDraw` | NO_ARITH | `drawbz`, `drawsize`, `hand`, `loads`, `poleinfo`, `ratio`, `sec` | `—` |
| `FERun` | NO_ARITH | `bids`, `hand`, `lcid`, `lds` | `—` |
| `FERunMax` | NO_ARITH | `Error: BEAM ID:%1 not a beam element`, `bid`, `bids`, `hand`, `lcids`, `lds` | `—` |
| `FESetENode` | NO_ARITH | `hand`, `n1`, `n2`, `name` | `—` |
| `FESetESec` | NO_ARITH | `hand`, `name`, `sec` | `—` |
| `FESetEle` | NO_ARITH | `hand`, `n1`, `n2`, `name`, `sec` | `—` |
| `FESetFixState` | NO_ARITH | `hand`, `name`, `r`, `x`, `y` | `—` |
| `FESetLPos` | NO_ARITH | `BID`, `epos`, `fid`, `hand`, `load not exist`, `spos` | `—` |
| `FESetLValue` | NO_ARITH | `BID`, `fid`, `hand`, `load not exist`, `val` | `—` |
| `FESetNPos` | NO_ARITH | `hand`, `name`, `x`, `y` | `—` |
| `FESetSec` | TABLE_LOOKUP | `A`, `I`, `S`, `W`, `hand`, `mname`, `sname`, `t` | `table[fun_1802798d0](uVar17) + table[fun_1802793c0](uVar17,3) + table[fun_180276eb0](uVar17,3)` |
| `FESetSecMat` | TABLE_LOOKUP | `hand`, `mname`, `sname` | `table[fun_1802798d0](uVar15) + table[fun_1802793c0](uVar15,3) + table[fun_180276eb0](uVar15,3)` |
| `FESetSecN` | TABLE_LOOKUP | `A`, `I`, `Iy`, `S`, `W`, `hand`, `mname`, `sname`, `t` | `table[fun_1802798d0](uVar19) + table[fun_1802793c0](uVar19,3) + table[fun_180276eb0](uVar19,3)` |
| `FEVOLGPoleDraw` | NO_ARITH | `beaminfo`, `drawbz`, `drawsize`, `hand`, `height`, `loads`, `prefix`, `sec`, `sec2` | `—` |
| `FEVPXTPoleDraw` | NO_ARITH | `beaminfo`, `drawbz`, `drawsize`, `hand`, `loads`, `sec` | `—` |
| `FEWinFanDoAll` | NO_ARITH | `hand`, `height`, `loads`, `sec`, `supinfo`, `width` | `—` |
| `FEWinFanDraw` | NO_ARITH | `drawbz`, `hand`, `height`, `loads`, `ratio`, `sec`, `supinfo`, `width` | `—` |
| `FEXTPoleDraw` | NO_ARITH | `drawbz`, `drawsize`, `hand`, `loads`, `poleinfo`, `ratio`, `sec` | `—` |
| `GetACFt` | SELECTED | `H`, `W`, `q`, `side`, `t` | `(((H) * (q) * (W) * 0.5) / (((double)sel(H\|W) * (q) * 0.5) / (t))) / ((W) + (H))` |
| `GetAVmax` | PARTIAL | `$0`, `$1`, `$2` | `(double)0.32 * (table[fun_180254fd0](iVar10,$2))` |
| `GetAirAn` | NO_ARITH | `$0` | `—` |
| `GetAl` | TABLE_LOOKUP | `$0` | `table[fun_180276990](uVar8)` |
| `GetAlpha` | NO_ARITH | `$0` | `—` |
| `GetAmax` | PARTIAL | `$0`, `$1`, `$2` | `(double)0.32 * (table[fun_180254fd0](iVar10,$2))` |
| `GetAmaxFa` | TABLE_LOOKUP | `$0`, `$1` | `table[fun_180254fd0](($0),$1)` |
| `GetAnchorAcnFormula` | NO_ARITH | `%1`, `(`, `+%1`, `Ccrn`, `FCODE`, `S`, `Scrn`, `c1`, `c2`, `c3`, `c4`, `crn`, `dM`, `dN`, `layout` | `—` |
| `GetAntiEQLevelString` | NO_ARITH | `$0` | `—` |
| `GetAntiNoiseDrawing` | NO_ARITH | `$0` | `—` |
| `GetAr` | NO_ARITH | `$0`, `CXConstant`, `x` | `—` |
| `GetArchBLen` | PARTIAL | `$0`, `$1` | `(cos(($1 * *(double *)PI_exref) / 180.0)) * $0` |
| `GetArchHeight` | PARTIAL | `$0`, `$1` | `sin(($1 * *(double *)PI_exref) / 180.0)` |
| `GetBF` | NO_ARITH | `b`, `m`, `q`, `t` | `—` |
| `GetBackSlotStressRatio` | NO_ARITH | `GLOB_LC_JS`, `SlotCount` | `—` |
| `GetBeamUNmax` | NO_ARITH | `$0`, `$1`, `$2`, `GLOB_LC_SH` | `—` |
| `GetBeamUmax` | NO_ARITH | `$0`, `$1`, `$2`, `GLOB_LC_SH` | `—` |
| `GetBeamWTMax` | NO_ARITH | `$0`, `$1` | `—` |
| `GetBgz` | TABLE_LOOKUP | `$0`, `$1`, `$2` | `table[fun_180255170](local_60,*(($1) + 8), *(($2) + 8),1)` |
| `GetBgzcal` | PARTIAL | `$0`, `$1`, `$2` | `(((pow($1 / 10.0,-(double)0.3)) * (pow(35.0,((double)0.3 - 0.16) * 1.8)) * 0.5) + ((pow($1 / 10.0,-(double)0.3)) * (pow(35.0,((double)0.3 - 0.16) * 1.8)) * 0.5) + 1.0) * (double)0.8` |
| `GetBoardMaterial` | NO_ARITH | `x` | `—` |
| `GetBoardType` | NO_ARITH | `x` | `—` |
| `GetBoltAn` | NO_ARITH | `D0`, `index`, `layout`, `length` | `—` |
| `GetBoltLength` | NO_ARITH | `layout` | `—` |
| `GetBoltLinkDrawing` | NO_ARITH | `layout`, `length`, `title`, `width` | `—` |
| `GetBoltNcb` | STRING_TABLE | `$0`, `$1`, `$2` | `STRLIT(fun_1802784c0)` |
| `GetBoltNumber` | NO_ARITH | `layout` | `—` |
| `GetBoltNvb` | TABLE_LOOKUP | `$0`, `$1`, `$2` | `table[fun_180278990](uVar11,0)` |
| `GetBoltShearDesc` | NO_ARITH | `simpleshear` | `—` |
| `GetBoltTForceTable` | TABLE_BUILDER | `fn`, `layout`, `t`, `vs` | `table[fun_18002c040](dVar2)` |
| `GetCBoltLayoutNTable` | NO_ARITH | `M`, `N`, `layout` | `—` |
| `GetCBoltLayoutRR` | PARTIAL | `$0` | `(0.0) + (($0 - ((0.0) / (double)(iVar2))) * (p[plVar14] - ((0.0) / (double)(iVar2))))` |
| `GetCBoltLayoutTotalN` | NO_ARITH | `M`, `N`, `layout` | `—` |
| `GetCBoltTForceTable` | TABLE_BUILDER | `fn`, `hs`, `layout`, `t`, `vs` | `table[fun_180058f10](dVar3)` |
| `GetCFrameReaction` | NO_ARITH | `gkindex`, `hand`, `loads`, `model`, `widths` | `—` |
| `GetCFrameReactionInfo` | NO_ARITH | `loads`, `model`, `widths` | `—` |
| `GetCLayoutS12` | NO_ARITH | `$0`, `$1` | `—` |
| `GetCPoleReaction` | NO_ARITH | `hand`, `loads`, `model`, `nodeindex` | `—` |
| `GetClosedShapeCoef` | NO_ARITH | `$0`, `$1`, `$2`, `GLOB_LC_GD` | `—` |
| `GetCommonBoltDrawing` | NO_ARITH | `layout`, `length`, `title`, `width` | `—` |
| `GetCommonLayoutRRzox` | PARTIAL | `$0` | `(0.0) + (($0 - ((0.0) / (double)(iVar2))) * (p[plVar14] - ((0.0) / (double)(iVar2))))` |
| `GetCompKtheta` | PARTIAL | `De`, `a`, `t`, `w` | `pow((a),4.0)` |
| `GetCompMetalPlateDe` | NO_ARITH | `$0`, `$1` | `—` |
| `GetCompMetalPlateTe` | NO_ARITH | `$0`, `$1` | `—` |
| `GetCompMetalPlateWe` | NO_ARITH | `$0`, `$1` | `—` |
| `GetCurrentGlassName` | NO_ARITH | `index`, `namei`, `namem`, `nameo`, `struct` | `—` |
| `GetDBFromT` | PARTIAL | `$0` | `log(1.0 / $0)` |
| `GetDSlopeShapeRatioRegionText` | NO_ARITH | `rtype` | `—` |
| `GetDe` | INTERPOLATION | `$0`, `CXConstant`, `x` | `INTERP(fun_180299d50)` |
| `GetDesity` | NO_ARITH | `$0` | `—` |
| `GetDispOfDistri` | PARTIAL | `Ex`, `Ix`, `lx`, `qx` | `pow((lx),4.0)` |
| `GetDispOfTrape` | PARTIAL | `Ex`, `Ix`, `ax`, `lx`, `qx` | `pow(_X_00,4.0)` |
| `GetDispOfTriang` | PARTIAL | `Ex`, `Ix`, `lx`, `qx` | `pow((lx),4.0)` |
| `GetE` | TABLE_LOOKUP | `$0`, `$1` | `table[fun_180276eb0](uVar7,0) + table[fun_180276eb0](uVar7,*(($1) + 8))` |
| `GetEQFormat` | NO_ARITH | `$0`, `$1` | `—` |
| `GetEQSSubFormat` | NO_ARITH | `$0`, `$1`, `$2` | `—` |
| `GetEarBoardDrawing` | NO_ARITH | `index` | `—` |
| `GetEarthQuakeLevelString` | NO_ARITH | `$0` | `—` |
| `GetF02` | NO_ARITH | `$0`, `$1` | `—` |
| `GetFEArchReaction` | NO_ARITH | `gkindex`, `hand`, `loads`, `nodename`, `poleinfo`, `sec` | `—` |
| `GetFc` | NO_ARITH | `$0` | `—` |
| `GetFcuk` | NO_ARITH | `$0`, `$1` | `—` |
| `GetFp` | TABLE_LOOKUP | `$0`, `$1` | `STRLIT(fun_180278650)` |
| `GetFrictionBoltAntiSlip` | NO_ARITH | `$0`, `$1` | `—` |
| `GetFrictionBoltNtb` | NO_ARITH | `$0`, `$1` | `—` |
| `GetFrictionBoltNvb` | NO_ARITH | `a`, `b`, `c` | `—` |
| `GetFrictionBoltPreForce` | NO_ARITH | `$0`, `$1` | `—` |
| `GetFstk` | NO_ARITH | `$0`, `$1` | `—` |
| `GetFt` | TABLE_LOOKUP | `$0`, `$1` | `table[fun_180278990](uVar6,0) + table[fun_180278990](uVar6,*(($1) + 8))` |
| `GetFvk` | NO_ARITH | `$0`, `$1` | `—` |
| `GetFyk` | NO_ARITH | `$0`, `$1` | `—` |
| `GetGama` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `GetGlassDesc` | NO_ARITH | `%0(%1)+%2+%3(%4)+%5+%6(%7)`, `%1(%2)+%3+%4(%5)+%6+%7(%8)`, `FF`, `FH`, `HS`, `PB`, `TP`, `wi`, `wm`, `wo`, `xdata` | `—` |
| `GetGlassLayerDesc` | NO_ARITH | `$0` | `—` |
| `GetGlassLayerThickness` | PARTIAL | `$0` | `(0.0) + p[plVar8]` |
| `GetGlassName` | NO_ARITH | `ta` | `—` |
| `GetGlassRatioMat` | PARTIAL | `prefix`, `ta` | `(ta[6]) / (((((((dVar21 * 1.1) * 1.1) * ((dVar21 * 1.1) * 1.1) * ((dVar21 * 1.1) * 1.1)) * 1.1) * 1.1) * (((((dVar21 * 1.1) * 1.1) * ((dVar21 * 1.1) * 1.1) * ((dVar21 * 1.1) * 1.1)) * 1.1) * 1.1) * (((((dVar21 * 1.1) * 1.1) * ((dVar21 * …` |
| `GetGlassThickMat` | NO_ARITH | `prefix`, `ta` | `—` |
| `GetGlassThickMatT` | NO_ARITH | `ta` | `—` |
| `GetGlassXDesc` | NO_ARITH | `ish`, `nm`, `wm`, `xi`, `xm`, `xo` | `—` |
| `GetGlueF1` | NO_ARITH | `$0` | `—` |
| `GetGlueF2` | NO_ARITH | `$0` | `—` |
| `GetGr` | NO_ARITH | `$0` | `—` |
| `GetHasAirLayer` | NO_ARITH | `$0` | `—` |
| `GetHasHollow` | NO_ARITH | `ta` | `—` |
| `GetI10` | NO_ARITH | `$0` | `—` |
| `GetInterpolation` | INTERPOLATION | `MATA`, `MATV`, `pos` | `INTERP(fun_180299d50)` |
| `GetKk` | NO_ARITH | `$0` | `—` |
| `GetKtheta` | PARTIAL | `Ew`, `a`, `t`, `w` | `pow(t,4.0)` |
| `GetKuf` | PARTIAL | `$0`, `$1` | `pow(35.0,((double)0.3 - 0.16) * 1.8)` |
| `GetKuh` | NO_ARITH | `$0` | `—` |
| `GetKuz` | NO_ARITH | `$0`, `$1` | `—` |
| `GetKuzcal` | TABLE_LOOKUP | `$0`, `$1` | `table[fun_180255450](local_88,*(($1) + 8))` |
| `GetLGAForceData` | NO_ARITH | `checkpos`, `hand` | `—` |
| `GetLMCBeamDfGMax` | NO_ARITH | `$0`, `CXStringDefine`, `GLOB_LOCALCODE`, `x` | `—` |
| `GetLMCBeamDflim` | NO_ARITH | `$0`, `$1`, `GLOB_LOCALCODE` | `—` |
| `GetLMCBeamDfnum` | NO_ARITH | `$0`, `$1`, `GLOB_LOCALCODE` | `—` |
| `GetLMCDflim` | STRING_TABLE | `$0`, `$1`, `$2` | `STRLIT(fun_180276de0)` |
| `GetLMCDfnum` | STRING_TABLE | `$0`, `$1`, `$2` | `STRLIT(fun_180276de0)` |
| `GetLambda` | NO_ARITH | `$0`, `$1` | `—` |
| `GetLarge` | NO_ARITH | `$0`, `$1` | `—` |
| `GetLayoutCenter` | PARTIAL | `$0` | `((double)iVar19 * (p[plVar14]) + dVar6 + (p[plVar14])) - (dVar5 - (0.0))` |
| `GetLayoutRR` | NO_ARITH | `$0` | `—` |
| `GetLayoutRRzox` | NO_ARITH | `$0` | `—` |
| `GetLayoutS2` | NO_ARITH | `$0`, `$1` | `—` |
| `GetLess` | NO_ARITH | `$0`, `$1` | `—` |
| `GetLockPointCount` | NO_ARITH | `bottom`, `height`, `left`, `right`, `top`, `width` | `—` |
| `GetM` | TABLE_LOOKUP | `$0`, `$1` | `table[fun_1802793c0](uVar8,0) + table[fun_1802793c0](uVar8,*(($1) + 8))` |
| `GetMCBoltFcb` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `GetMatrixLength` | NO_ARITH | `$0` | `—` |
| `GetMatrixMul` | NO_ARITH | `$0`, `$1` | `—` |
| `GetMaxBoltPullForce` | NO_ARITH | `FORCEM`, `FORCEN`, `center`, `myc`, `n` | `—` |
| `GetMaxBoltTForceData` | NO_ARITH | `layout`, `t`, `vs` | `—` |
| `GetMaxCBoltTForceData` | NO_ARITH | `hs`, `layout`, `t`, `vs` | `—` |
| `GetMetalNg` | INTERPOLATION | `$0`, `$1` | `INTERP(fun_180299d50)` |
| `GetMetalPlateFt` | NO_ARITH | `$0`, `$1` | `—` |
| `GetMetalPlateFv` | NO_ARITH | `$0`, `$1` | `—` |
| `GetMidLayerANoise` | NO_ARITH | `$0` | `—` |
| `GetNg` | INTERPOLATION | `$0`, `$1` | `INTERP(fun_180299d50) + INTERP(fun_180299d50)` |
| `GetNu` | PARTIAL | `$0`, `$1` | `(pow((pow(p[plVar3],3.0)) * (p[dVar19]) * 0.0001,(double)0.31)) * (double)0.1` |
| `GetOKStr` | NO_ARITH | `x` | `—` |
| `GetOKString` | NO_ARITH | `x` | `—` |
| `GetPXTForceData` | NO_ARITH | `checkpos`, `hand` | `—` |
| `GetPlateLoadString` | NO_ARITH | `wkn`, `wkp`, `wn`, `wp` | `—` |
| `GetPoleCalcStab` | NO_ARITH | `poleinfo` | `—` |
| `GetPoleLambda` | PARTIAL | `A`, `Ix`, `Iy`, `L`, `Mat`, `sectype` | `(((((L * 100.0) / (Ix)) / *(double *)PI_exref) * (table[fun_180277390](local_f8,4))) * ((((L * 100.0) / (Ix)) / *(double *)PI_exref) * (table[fun_180277390](local_f8,4)))) * 0.65` |
| `GetPr` | NO_ARITH | `$0` | `—` |
| `GetProjCodeInfo` | NO_ARITH | `$0` | `—` |
| `GetRBoardEmitData` | NO_ARITH | `name` | `—` |
| `GetRDis` | PARTIAL | `B`, `E`, `H`, `Hr`, `isDRib`, `t`, `wk` | `pow((Hr),3.0)` |
| `GetRMidHollowGlass` | PARTIAL | `ta` | `(ta[4]) / (ta[6]) + dVar21 / (ta[6]) + ((dVar21 * 1.1) / (ta[6]) + (ta[4]) / (ta[6]) + ((dVar19 * 1.1) / (ta[6])))` |
| `GetRecip` | NO_ARITH | `$0` | `—` |
| `GetRibGlassThickMatrix` | NO_ARITH | `filmthick`, `glsthick`, `nums` | `—` |
| `GetRibGlassThickness` | NO_ARITH | `al`, `filmType`, `glsthickMAT`, `glumodule` | `—` |
| `GetSABFt` | NO_ARITH | `H`, `W`, `c`, `q`, `side`, `t` | `—` |
| `GetSCBFt` | NO_ARITH | `a`, `b`, `c`, `n`, `q`, `r`, `s`, `side`, `t` | `—` |
| `GetSDr` | PARTIAL | `$0`, `$1`, `$2`, `$3` | `(((($0) / ((($0) / ((($0) / ((($0) / ((($0) / ((($0) / ((($0) / ($1)) / ($0))) / ($0))) / ($0))) / ($0))) / ($0))) / ($0))) / ($0)) / ($0)) * 0.5` |
| `GetSFAlpha1` | NO_ARITH | `sectype` | `—` |
| `GetSFAlpha2` | NO_ARITH | `lambda`, `sectype` | `—` |
| `GetSFAlpha3` | NO_ARITH | `lambda`, `sectype` | `—` |
| `GetSGPThickness` | NO_ARITH | `al`, `glsthickMAT`, `glumodule` | `—` |
| `GetSHCPanelGama` | NO_ARITH | `bmat`, `fmat` | `—` |
| `GetSLBFt` | PARTIAL | `a`, `b`, `d`, `h`, `n`, `q`, `r`, `side`, `t` | `((n) * 4.0) + ((n) * 4.0)` |
| `GetSLFt` | PARTIAL | `A`, `a`, `b`, `n`, `q`, `r`, `side` | `((n) * 4.0) + ((n) * 4.0)` |
| `GetSMr` | PARTIAL | `$0`, `$1`, `$2`, `$3` | `(((($0) / ((($0) / ($1)) / ($0))) / ($0)) / (($0) / ((($0) / ((($0) / ($1)) / ($0))) / ($0)))) / (((($0) / ((($0) / ($1)) / ($0))) / ($0)) * 0.5)` |
| `GetSNRatio` | NO_ARITH | `$0`, `GLOB_LC_JS` | `—` |
| `GetSSubFormat` | NO_ARITH | `$0`, `$1`, `$2` | `—` |
| `GetSlopeSwMatrix` | NO_ARITH | `angle`, `load1`, `load2`, `mat` | `—` |
| `GetSlopeWindMatrix` | NO_ARITH | `SwMat`, `SwkMat`, `sl`, `slk`, `ss`, `ssk` | `—` |
| `GetSteelShapeRatio` | NO_ARITH | `$0` | `—` |
| `GetStoneType` | NO_ARITH | `$0`, `$1` | `—` |
| `GetStrCopy` | NO_ARITH | `$0` | `—` |
| `GetSupportReForce` | NO_ARITH | `mat`, `name` | `—` |
| `GetSupportReForceWithSFloor` | NO_ARITH | `mat`, `name`, `sfloor` | `—` |
| `GetTroembAsna` | PARTIAL | `S`, `Scrna`, `num` | `(1.0) + (pow(1.0 - (1.0) / (Scrna),1.5))` |
| `GetTroembS` | PARTIAL | `S`, `Scrna`, `curind`, `num`, `theind` | `(double)(int)((uVar15 ^ uVar13) - uVar13) * S` |
| `GetTrueWk` | NO_ARITH | `0`, `gw`, `gwv`, `lim`, `wk` | `—` |
| `GetTwistCenter` | NO_ARITH | `$0` | `—` |
| `GetTwistFEMaxStressN` | NO_ARITH | `MY`, `MZ`, `N`, `doc`, `prefix` | `—` |
| `GetTwistFEMaxVonmises` | NO_ARITH | `MT`, `MY`, `MZ`, `N`, `doc`, `prefix` | `—` |
| `GetTwistMaxStress` | NO_ARITH | `doc`, `mt`, `prefix` | `—` |
| `GetTwistStressDrawing` | NO_ARITH | `BREP`, `bz`, `doc`, `drawsize`, `mt`, `prefix` | `—` |
| `GetUNmax` | NO_ARITH | `$0`, `$1`, `$2` | `—` |
| `GetUmax` | NO_ARITH | `$0`, `$1`, `$2` | `—` |
| `GetVFrameReaction` | NO_ARITH | `gkindex`, `loads`, `model`, `nodename`, `widths` | `—` |
| `GetVFrameReactionInfo` | NO_ARITH | `loads`, `model`, `widths` | `—` |
| `GetVSecInfo` | NO_ARITH | `secdata`, `type` | `—` |
| `GetVr` | TABLE_LOOKUP | `$0` | `table[fun_1802798d0](uVar7)` |
| `GetWaterSealRatio` | NO_ARITH | `$0` | `—` |
| `GetWeldFa` | NO_ARITH | `$0` | `—` |
| `GetWeldNASDesc` | NO_ARITH | `bdouble`, `style`, `type` | `—` |
| `GetWeldNASF` | PARTIAL | `data`, `index` | `(double)0.35 + (double)0.35` |
| `GetWeldNASK` | TABLE_LOOKUP | `index`, `type` | `table[fun_18032e420]((type),(index))` |
| `GetWindG` | NO_ARITH | `$0`, `GLOB_GDCITY`, `GLOB_LC_GD` | `—` |
| `GetWindSpeed` | NO_ARITH | `$0` | `—` |
| `GetYKType` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `HWKGetMinValueOfFunction` | NO_ARITH | `A`, `E`, `L`, `N`, `W`, `gama`, `huai`, `lambda`, `loadn`, `q` | `—` |
| `IsBgzTruncHigh` | NO_ARITH | `$0`, `$1`, `GLOB_GDCITY` | `—` |
| `IsKuzTruncHigh` | NO_ARITH | `$0`, `$1` | `—` |
| `IsLargeConLevel` | NO_ARITH | `$0` | `—` |
| `IsQBMQ` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `IsRivetStress` | NO_ARITH | `$0` | `—` |
| `RailingAddProb` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `RailingDelProb` | NO_ARITH | `handle` | `—` |
| `ShellAddProb` | NO_ARITH | `$0`, `CXStringDefine`, `x` | `—` |
| `ShellDelProb` | NO_ARITH | `handle` | `—` |
| `XDrawProMetalSheet_Face` | NO_ARITH | `methodenum`, `model`, `title`, `up` | `—` |
| `XDrawProMetalSheet_Wire` | NO_ARITH | `$0`, `$1` | `—` |
| `XDrawProfile` | NO_ARITH | `$0`, `$1` | `—` |
| `XDrawProfileEX` | NO_ARITH | `DESC`, `ID`, `SLD` | `—` |
| `XDrawWeldNAS` | NO_ARITH | `data` | `—` |
| `XDrawWeldNMV1` | NO_ARITH | `data` | `—` |
| `XDrawWeldNV` | PARTIAL | `force`, `number`, `orient` | `(orient) + 180.0)` |
