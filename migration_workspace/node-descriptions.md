# 节点结构描述（L5/A 路线第 4 步）

- 覆盖：379 个节点全部
- 内容只描述**结构**（入参、主要动作、返回类型），**不含业务语义推断**

| 节点 | 类别 | 算式 | 入参 | 业务相关调用 | 分支数 | 返回 |
| --- | --- | --- | --- | --- | --- | --- |
| `AwningAddProb` | COLLECTION | NO_ARITH | $0 | `CXBase::CXBase`, `CXTypePtr::CXTypePtr`, `XYUtil::StringPointer::StringPointer` | 13 | `CXConstant *` |
| `AwningDelProb` | GETTER | NO_ARITH | handle | `CXBasePtr::CXBasePtr`, `CXBasePtr::Nullify`, `XYUtil::CXConstant::CXConstant` | 15 | `CXConstant *` |
| `CalGlassDisp` | ARITH | EXPR | ms, qwk, aw, dw, theta, prefix | `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `CalGlassPSDisp` | ARITH | EXPR | ms, qwk, aw, dw, theta, num | `XYUtil::CXConstant::CXConstant` | 14 | `CXConstant *` |
| `CalGlassPSStress` | ARITH | EXPR | sw, qw, aw, tw, num, theta | `XYUtil::CXConstant::CXConstant` | 14 | `CXConstant *` |
| `CalGlassStress` | ARITH | EXPR | sw, qw, aw, tw, theta, prefix | `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `CalcGlassShadeCoef` | GETTER | NO_ARITH | handle, calcinfo, calrad, layids, thicks, gopparam | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `HWKDoubleArray::HWKDoubleArray` | 16 | `CXConstant *` |
| `CalcGlassUFactor` | GETTER | NO_ARITH | handle, calcinfo, calrad, layids, thicks, gopparam | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `HWKDoubleArray::HWKDoubleArray` | 16 | `CXConstant *` |
| `CheckHasHollowBeforeLayer` | PREDICATE | NO_ARITH | ta, layer | `XYUtil::CXConstant::CXConstant` | 19 | `CXConstant *` |
| `CheckPoleIsSimpleSup` | GETTER | NO_ARITH | poleinfo | `CXPoleDataIOInfo::CXPoleDataIOInfo`, `CXPoleDataIOInfo::ReadData`, `XYUtil::CXConstant::CXConstant` | 15 | `CXConstant *` |
| `ClayPlateAddProb` | COLLECTION | NO_ARITH | $0 | `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess`, `XYUtil::CXConstant::CXConstant` | 16 | `CXBase *` |
| `ClayPlateDelProb` | GETTER | NO_ARITH | handle | `CXBasePtr::CXBasePtr`, `CXBasePtr::Nullify`, `XYUtil::CXConstant::CXConstant` | 15 | `CXConstant *` |
| `DoCalcAwning3d` | STRING | NO_ARITH | hand, loads, GAK, model, drawsize, material | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CXBasePtr::CXBasePtr` | 26 | `CXStringDefine *` |
| `DoCalcClayPlate3d` | STRING | NO_ARITH | hand, loads, model, drawsize, material, bz | `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess`, `XYUtil::CXStringDefine::CXStringDefine` | 28 | `CXStringDefine *` |
| `DoCalcRailing3d` | STRING | NO_ARITH | hand, loads, model, drawsize, hmaterial, vmaterial | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CXBasePtr::CXBasePtr` | 31 | `CXStringDefine *` |
| `DoCalcShell` | STRING | NO_ARITH | hand, thickinfo, shellinfo, bz | `XYUtil::StringPointer::StringPointer`, `CXBasePtr::CXBasePtr`, `CXBasePtr::Access` | 32 | `CXStringDefine *` |
| `DoDrawVSec` | DRAW | NO_ARITH | secdata, bz | `XYUtil::CXStringDefine::CXStringDefine` | 9 | `CXStringDefine *` |
| `DoGetAwning3dReaction` | GETTER | NO_ARITH | hand, loads, GAK, model, gkindex, material | `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess`, `XYUtil::CXMatrix::CXMatrix` | 16 | `CXMatrix *` |
| `DoGetAwning3dReactionInfo` | GETTER | NO_ARITH | hand, loads, GAK, model, material | `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess`, `XYUtil::CXMatrix::CXMatrix` | 16 | `CXMatrix *` |
| `DoGetAwning3dReactionMatrix` | GETTER | NO_ARITH | hand, loads, GAK, model, material | `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess`, `XYUtil::CXMatrix::CXMatrix` | 16 | `CXMatrix *` |
| `DrawGlassTempInfo` | DRAW | NO_ARITH | uhandle, shandle, calcinfo, calrad, layids, thicks | `XYUtil::CXStringDefine::CXStringDefine` | 9 | `CXStringDefine *` |
| `DrawGlassUInfo` | DRAW | NO_ARITH | uhandle, calcinfo, calrad, layids, thicks, ugopparam | `XYUtil::CXStringDefine::CXStringDefine` | 9 | `CXStringDefine *` |
| `DrawHoldingBlock` | DRAW | NO_ARITH | L0, L, H0, H, T, D | `XYUtil::CXStringDefine::CXStringDefine` | 9 | `CXStringDefine *` |
| `DrawWallUTable` | DRAW | NO_ARITH | kvalues, types, areas, descs, type | `XYUtil::CXStringDefine::CXStringDefine` | 19 | `CXStringDefine *` |
| `DtoK` | GETTER | NO_ARITH | $0 | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `FEAddAnaOfAluBoardProb` | COLLECTION | NO_ARITH | $0 | `CXBase::CXBase`, `CXTypePtr::CXTypePtr`, `XYUtil::StringPointer::StringPointer` | 13 | `CXConstant *` |
| `FEAddAnaOfCylinderProb` | COLLECTION | NO_ARITH | $0 | `CXBase::CXBase`, `CXTypePtr::CXTypePtr`, `XYUtil::StringPointer::StringPointer` | 13 | `CXConstant *` |
| `FEAddAnaOfQuadMindlinSProb` | COLLECTION | NO_ARITH | $0 | `CXBase::CXBase`, `CXTypePtr::CXTypePtr`, `XYUtil::StringPointer::StringPointer` | 13 | `CXConstant *` |
| `FEAddBDLoad` | COLLECTION | NO_ARITH | hand, lcid, BID, val, spos, epos | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 20 | `CXConstant *` |
| `FEAddBFLoad` | COLLECTION | NO_ARITH | hand, lcid, BID, pos, val, name | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 21 | `CXConstant *` |
| `FEAddBTDLoad` | COLLECTION | NO_ARITH | hand, lcid, BID, val, spos, epos | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 19 | `CXConstant *` |
| `FEAddBTULoad` | COLLECTION | NO_ARITH | hand, lcid, BID, val, spos, epos | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 19 | `CXConstant *` |
| `FEAddBeamExModelProb` | COLLECTION | NO_ARITH | $0 | `CXBase::CXBase`, `CXTypePtr::CXTypePtr`, `XYUtil::StringPointer::StringPointer` | 12 | `CXConstant *` |
| `FEAddBoardModelProb` | COLLECTION | NO_ARITH | $0 | `CXBase::CXBase`, `CXTypePtr::CXTypePtr`, `XYUtil::StringPointer::StringPointer` | 12 | `CXConstant *` |
| `FEAddCBProb` | COLLECTION | NO_ARITH | $0 | `CCrossBeam::CCrossBeam`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 15 | `CXConstant *` |
| `FEAddCFrameModelProb` | COLLECTION | NO_ARITH | $0 | `CXBase::CXBase`, `CXTypePtr::CXTypePtr`, `XYUtil::StringPointer::StringPointer` | 12 | `CXConstant *` |
| `FEAddGBeamModelProb` | COLLECTION | NO_ARITH | $0 | `CXBase::CXBase`, `CXTypePtr::CXTypePtr`, `XYUtil::StringPointer::StringPointer` | 12 | `CXConstant *` |
| `FEAddGOPProb` | COLLECTION | NO_ARITH | $0 | `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess`, `XYUtil::CXConstant::CXConstant` | 14 | `CXConstant *` |
| `FEAddGraphModelProb` | COLLECTION | NO_ARITH | $0 | `CXBase::CXBase`, `CXTypePtr::CXTypePtr`, `XYUtil::StringPointer::StringPointer` | 12 | `CXConstant *` |
| `FEAddLnkNetProb` | COLLECTION | NO_ARITH | — | `CLinkNetCalc::CLinkNetCalc`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 6 | `CXConstant *` |
| `FEAddLnkTrussProb` | COLLECTION | NO_ARITH | — | `CLinkTrussCalc::CLinkTrussCalc`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 6 | `CXConstant *` |
| `FEAddLoadcase` | FE_DATA | NO_ARITH | hand, name | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 17 | `CXConstant *` |
| `FEAddMat` | COLLECTION | TABLE_LOOKUP | hand, mname | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 13 | `CXConstant *` |
| `FEAddNode` | COLLECTION | NO_ARITH | hand, name, x, y, DOF, IsCon | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 11 | `CXConstant *` |
| `FEAddPlaneStressProb` | COLLECTION | NO_ARITH | $0 | `CXBase::CXBase`, `CXTypePtr::CXTypePtr`, `XYUtil::StringPointer::StringPointer` | 12 | `CXConstant *` |
| `FEAddProb` | FE_DATA | NO_ARITH | $0, $1 | `CFEProblem::CFEProblem`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 11 | `CXConstant *` |
| `FEAddShellProb` | COLLECTION | NO_ARITH | $0 | `CFEShellInfo::CFEShellInfo`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 14 | `CXConstant *` |
| `FEAddThermProb` | COLLECTION | NO_ARITH | $0 | `CThermFEAnalysisCalc::CThermFEAnalysisCalc`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 14 | `CXConstant *` |
| `FEAddUnregLnkNetProb` | COLLECTION | NO_ARITH | $0 | `CUnregLinkNetCalc::CUnregLinkNetCalc`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 17 | `CXConstant *` |
| `FEAddVFrameModelProb` | COLLECTION | NO_ARITH | $0 | `CXBase::CXBase`, `CXTypePtr::CXTypePtr`, `XYUtil::StringPointer::StringPointer` | 12 | `CXConstant *` |
| `FEAnalysisOfAluBoard` | STRING | NO_ARITH | hand, model, drawsize, bz | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CXBasePtr::CXBasePtr` | 32 | `CXStringDefine *` |
| `FEAnalysisOfCylinder` | STRING | NO_ARITH | hand, model, drawsize, bz | `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess`, `XYUtil::CXStringDefine::CXStringDefine` | 28 | `CXStringDefine *` |
| `FEAnalysisOfQuadMindlinSimple` | STRING | NO_ARITH | hand, model, drawsize, bz | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CXBasePtr::CXBasePtr` | 32 | `CXStringDefine *` |
| `FEArchDraw` | STRING | NO_ARITH | hand, sec, loads, poleinfo, drawbz, drawsize | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 36 | `CXStringDefine *` |
| `FEBIniSecData` | FE_DATA | NO_ARITH | hand | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 14 | `CXConstant *` |
| `FEBeamDraw` | STRING | NO_ARITH | hand1, sec1, hand2, sec2, loads, beaminfo | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CFEProblem::Exist` | 40 | `CXStringDefine *` |
| `FECBeamDraw` | STRING | VARARG_GET | hand, mat, sec, loads, cbeaminfo, drawbz | `CCrossBeam::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::IsNull` | 36 | `CXStringDefine *` |
| `FEClear` | FE_DATA | NO_ARITH | hand | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 9 | `CXConstant *` |
| `FEClearBLoad` | FE_DATA | NO_ARITH | hand, BID | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 9 | `CXConstant *` |
| `FEClearCBProb` | FE_DATA | NO_ARITH | handle | `CCrossBeam::Clear`, `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `FEClearProb` | FE_DATA | NO_ARITH | handle | `CFEProblem::Clear`, `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `FEDelAnaOfAluBoardProb` | FE_DATA | NO_ARITH | handle | `CXBasePtr::CXBasePtr`, `CXBasePtr::Nullify`, `XYUtil::CXConstant::CXConstant` | 15 | `CXConstant *` |
| `FEDelAnaOfCylinderProb` | FE_DATA | NO_ARITH | handle | `CXBasePtr::CXBasePtr`, `CXBasePtr::Nullify`, `XYUtil::CXConstant::CXConstant` | 15 | `CXConstant *` |
| `FEDelAnaOfQuadMindlinSProb` | FE_DATA | NO_ARITH | handle | `CXBasePtr::CXBasePtr`, `CXBasePtr::Nullify`, `XYUtil::CXConstant::CXConstant` | 15 | `CXConstant *` |
| `FEDelBeamExModelProb` | FE_DATA | NO_ARITH | handle | `CXBasePtr::CXBasePtr`, `CXBasePtr::Nullify`, `XYUtil::CXConstant::CXConstant` | 14 | `CXConstant *` |
| `FEDelBoardModelProb` | FE_DATA | NO_ARITH | handle | `CXBasePtr::CXBasePtr`, `CXBasePtr::Nullify`, `XYUtil::CXConstant::CXConstant` | 14 | `CXConstant *` |
| `FEDelCBProb` | COLLECTION | NO_ARITH | handle | `CCrossBeam::Remove`, `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `FEDelCFrameModelProb` | FE_DATA | NO_ARITH | handle | `CXBasePtr::CXBasePtr`, `CXBasePtr::Nullify`, `XYUtil::CXConstant::CXConstant` | 14 | `CXConstant *` |
| `FEDelGBeamModelProb` | FE_DATA | NO_ARITH | handle | `CXBasePtr::CXBasePtr`, `CXBasePtr::Nullify`, `XYUtil::CXConstant::CXConstant` | 14 | `CXConstant *` |
| `FEDelGOPProb` | FE_DATA | NO_ARITH | handle | `XYUtil::CXConstant::CXConstant` | 11 | `NCollection_ListNode *` |
| `FEDelGraphModelProb` | FE_DATA | NO_ARITH | handle | `CXBasePtr::CXBasePtr`, `CXBasePtr::Nullify`, `XYUtil::CXConstant::CXConstant` | 14 | `CXConstant *` |
| `FEDelLnkNetProb` | COLLECTION | NO_ARITH | handle | `CLinkNetCalc::Remove`, `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `FEDelLnkTrussProb` | COLLECTION | NO_ARITH | handle | `CLinkTrussCalc::Remove`, `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `FEDelLoad` | COLLECTION | NO_ARITH | hand, BID, fid | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 10 | `CXConstant *` |
| `FEDelPlaneStressProb` | FE_DATA | NO_ARITH | handle | `CXBasePtr::CXBasePtr`, `CXBasePtr::Nullify`, `XYUtil::CXConstant::CXConstant` | 14 | `CXConstant *` |
| `FEDelProb` | COLLECTION | NO_ARITH | handle | `CFEProblem::Remove`, `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `FEDelShellProb` | COLLECTION | NO_ARITH | handle | `CFEShellInfo::Remove`, `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `FEDelThermProb` | COLLECTION | NO_ARITH | handle | `CThermFEAnalysisCalc::Remove`, `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `FEDelUnregLnkNetProb` | COLLECTION | NO_ARITH | handle | `CUnregLinkNetCalc::Remove`, `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `FEDelVFrameModelProb` | FE_DATA | NO_ARITH | handle | `CXBasePtr::CXBasePtr`, `CXBasePtr::Nullify`, `XYUtil::CXConstant::CXConstant` | 14 | `CXConstant *` |
| `FEDoAll` | FE_DATA | FE_OP | hand, sec, loads, mcinfo, mcfginfo, mcfgleft | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::Access` | 16 | `CFELoadCase *` |
| `FEDoArchPole` | FE_DATA | NO_ARITH | hand, sec, loads, poleinfo | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::Access` | 22 | `CFELoadCase *` |
| `FEDoBeam` | FE_DATA | FE_OP | hand1, hand2, sec1, sec2, loads, poleinfo | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::Access` | 18 | `CFELoadCase *` |
| `FEDoBeamEx` | STRING | NO_ARITH | hand, model, loads, widths, controls, drawsize | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CXBasePtr::CXBasePtr` | 33 | `CXStringDefine *` |
| `FEDoBoardAnalysisMitc4` | STRING | NO_ARITH | hand, model, loads, widths, drawsize, bz | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CXBasePtr::CXBasePtr` | 32 | `CXStringDefine *` |
| `FEDoCBeam` | FE_DATA | FE_OP | hand, mat, sec, loads, cbeaminfo | `CCrossBeam::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::Access` | 16 | `CXBase *` |
| `FEDoCFrame` | STRING | FE_OP | hand, model, loads, widths, containweight, drawsize | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CXBasePtr::CXBasePtr` | 36 | `CXStringDefine *` |
| `FEDoCPole` | STRING | FE_OP | hand, model, loads, drawsize, polepos | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CXBasePtr::CXBasePtr` | 31 | `CXStringDefine *` |
| `FEDoGBeam` | STRING | NO_ARITH | hand, model, loads, widths, drawsize, polepos | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CXBasePtr::CXBasePtr` | 34 | `CXStringDefine *` |
| `FEDoGrilleVPole` | FE_DATA | NO_ARITH | hand, sec, loads, poleinfo | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::Access` | 18 | `CXBase *` |
| `FEDoGrilleVPoleDraw` | STRING | NO_ARITH | hand, sec, loads, poleinfo, drawbz, drawsize | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CFEProblem::Exist` | 45 | `CXStringDefine *` |
| `FEDoLGAPole` | FE_DATA | FE_OP | hand, sec1, sec2, pos, loads, poleinfo | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::Access` | 18 | `CFELoadCase *` |
| `FEDoLinkNet` | STRING | NO_ARITH | hand, preloads, loads, temps, lnkinfo, matxinfo | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CLinkNetCalc::Exist` | 37 | `CXStringDefine *` |
| `FEDoLinkTruss` | STRING | NO_ARITH | hand, context, loads, temps, widthinfo, coninfo | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CLinkTrussCalc::Exist` | 32 | `CXStringDefine *` |
| `FEDoLockPointShell` | STRING | FE_OP | hand, load, thickinfo, width, height, shelllockinfo | `CFEShellInfo::Exist`, `CXBasePtr::CXBasePtr`, `CXBase::CXBase` | 36 | `CXStringDefine *` |
| `FEDoPXTPole` | FE_DATA | NO_ARITH | hand, sec, loads, poleinfo, polepos | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::Access` | 17 | `CFELoadCase *` |
| `FEDoPlaneStressAnalysisMitc4` | STRING | NO_ARITH | hand, model, loads, widths, drawsize, bz | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CXBasePtr::CXBasePtr` | 32 | `CXStringDefine *` |
| `FEDoPole` | FE_DATA | NO_ARITH | hand, sec, loads, poleinfo, polepos | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::Access` | 19 | `CXBase *` |
| `FEDoShell` | STRING | NO_ARITH | hand, loads, thickinfo, shellinfo, angle, weight | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CFEShellInfo::Exist` | 56 | `CXStringDefine *` |
| `FEDoTherm` | STRING | NO_ARITH | hand, structinfo, modelinfo, controlinfo, linetemp, drawline | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CThermFEAnalysisCalc::Exist` | 37 | `CXStringDefine *` |
| `FEDoUnregLinkNet` | STRING | NO_ARITH | hand, context, loads, temps, calcweight, coninfo | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CUnregLinkNetCalc::Exist` | 37 | `CXStringDefine *` |
| `FEDoVFrame` | STRING | FE_OP | hand, model, loads, widths, containweight, drawsize | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CXBasePtr::CXBasePtr` | 36 | `CXStringDefine *` |
| `FEDoVOLGPole` | FE_DATA | FE_OP | hand, sec, sec2, loads, height, poleinfo | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::Access` | 18 | `CFELoadCase *` |
| `FEDoVPXTPole` | FE_DATA | NO_ARITH | hand, sec, loads, poleinfo, polepos | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::Access` | 17 | `CFELoadCase *` |
| `FEDoXTPole` | FE_DATA | FE_OP | hand, sec, loads, polelength | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::Access` | 17 | `CFELoadCase *` |
| `FEGetDData` | FE_DATA | NO_ARITH | hand, bid | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 16 | `CXMatrix *` |
| `FEGetDMax` | FE_DATA | NO_ARITH | hand, bid | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 18 | `CXConstant *` |
| `FEGetMData` | FE_DATA | NO_ARITH | hand, bid | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 17 | `CXConstant *` |
| `FEGetMMax` | FE_DATA | NO_ARITH | hand, bid | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 18 | `CXConstant *` |
| `FEGetPiece` | FE_DATA | NO_ARITH | hand, bid | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 14 | `CXConstant *` |
| `FEGetQData` | FE_DATA | NO_ARITH | hand, bid | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 16 | `CXMatrix *` |
| `FEGetQMax` | FE_DATA | NO_ARITH | hand, bid | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 18 | `CXConstant *` |
| `FELGAPoleDraw` | STRING | NO_ARITH | hand, sec1, sec2, loads, pos, beaminfo | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CFEProblem::Exist` | 26 | `CXStringDefine *` |
| `FEMCDraw` | STRING | NO_ARITH | hand, sec, loads, mcinfo, mcfginfo, mcfgleft | `CFEProblem::Exist`, `XYUtil::CXStringDefine::CXStringDefine` | 13 | `CXStringDefine *` |
| `FEMCDrawStress` | STRING | NO_ARITH | hand, ghand, ratio, gratio | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CFEProblem::Exist` | 15 | `CXStringDefine *` |
| `FEMCGHDoAll` | ARITH | PARTIAL | hand, sec, loads, mcinfo, mcfginfo, mcsupinfo | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::Access` | 17 | `CFELoadCase *` |
| `FEMCGHDraw` | ARITH | PARTIAL | hand, sec, loads, mcinfo, mcfginfo, supinfo | `CFEProblem::Exist`, `XYUtil::CXStringDefine::CXStringDefine` | 10 | `CXStringDefine *` |
| `FEMCHDoAll` | FE_DATA | FE_OP | hand, sec, loads, mcinfo, mcfginfo | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::Access` | 17 | `CXBase *` |
| `FEMCHDraw` | STRING | NO_ARITH | hand, sec, loads, mcinfo, mcfginfo, drawbz | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CFEProblem::Exist` | 15 | `CXStringDefine *` |
| `FEMCMaxStress` | FE_DATA | FE_OP | hand, ghand, ratio, gratio | `CFEProblem::Exist`, `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `FEPXTPoleDraw` | STRING | NO_ARITH | hand, sec, loads, beaminfo, drawbz, drawsize | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CFEProblem::Exist` | 26 | `CXStringDefine *` |
| `FEPoleDraw` | STRING | NO_ARITH | hand, sec, loads, poleinfo, drawbz, drawsize | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CFEProblem::Exist` | 63 | `CXStringDefine *` |
| `FERun` | FE_DATA | NO_ARITH | hand, lcid, bids, lds | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 16 | `CXConstant *` |
| `FERunMax` | FE_DATA | NO_ARITH | hand, bid, lcids, bids, lds | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `XYUtil::CXTMatrix::CXTMatrix` | 30 | `NCollection_ListNode *` |
| `FESetENode` | FE_DATA | NO_ARITH | hand, name, n1, n2 | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CFEBaseElementPtr::CFEBaseElementPtr` | 11 | `CXConstant *` |
| `FESetESec` | FE_DATA | NO_ARITH | hand, name, sec | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CFEBaseElementPtr::CFEBaseElementPtr` | 11 | `CXConstant *` |
| `FESetEle` | FE_DATA | NO_ARITH | hand, name, sec, n1, n2 | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CFEBaseElementPtr::CFEBaseElementPtr` | 21 | `CXConstant *` |
| `FESetFixState` | FE_DATA | NO_ARITH | hand, name, x, y, r | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 13 | `CXConstant *` |
| `FESetLPos` | FE_DATA | NO_ARITH | hand, BID, fid, spos, epos | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 13 | `CXConstant *` |
| `FESetLValue` | FE_DATA | NO_ARITH | hand, BID, fid, val | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 13 | `CXConstant *` |
| `FESetNPos` | COLLECTION | NO_ARITH | hand, name, x, y | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 11 | `CXConstant *` |
| `FESetSec` | COLLECTION | TABLE_LOOKUP | hand, sname, mname, I, A, t | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 13 | `CXConstant *` |
| `FESetSecMat` | COLLECTION | TABLE_LOOKUP | hand, sname, mname | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 13 | `CXConstant *` |
| `FESetSecN` | COLLECTION | TABLE_LOOKUP | hand, sname, mname, I, Iy, A | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess` | 15 | `CXConstant *` |
| `FEVOLGPoleDraw` | STRING | NO_ARITH | hand, sec, sec2, loads, height, beaminfo | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CFEProblem::Exist` | 32 | `CXStringDefine *` |
| `FEVPXTPoleDraw` | STRING | NO_ARITH | hand, sec, loads, beaminfo, drawbz, drawsize | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CFEProblem::Exist` | 28 | `CXStringDefine *` |
| `FEWinFanDoAll` | FE_DATA | NO_ARITH | hand, sec, loads, supinfo, height, width | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::Access` | 15 | `CFELoadCase *` |
| `FEWinFanDraw` | STRING | NO_ARITH | hand, sec, loads, supinfo, height, width | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `XYUtil::CXStringDefine::CXStringDefine` | 12 | `CXStringDefine *` |
| `FEXTPoleDraw` | STRING | NO_ARITH | hand, sec, loads, poleinfo, drawbz, drawsize | `CHWKThreadJobImpl::IsAbortState`, `XYUtil::CXStringDefine::CXStringDefine`, `CFEProblem::Exist` | 25 | `CXStringDefine *` |
| `GetAAs1` | ARITH | EXPR | M, N, V, ar, av, ab | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetAAs2` | ARITH | EXPR | M, N, ar, ab, z, fy | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetACFt` | ARITH | SELECTED | q, H, W, t, side | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetAMJRatio` | ARITH | EXPR | thickness, diameter | `XYUtil::CXConstant::CXConstant` | 11 | `CXConstant *` |
| `GetAVmax` | ARITH | PARTIAL | $0, $1, $2 | `XYUtil::CXConstant::CXConstant` | 15 | `CXConstant *` |
| `GetAddDRm` | ARITH | EXPR | $0, $1 | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXStringDefine::CXStringDefine`, `XYUtil::CXConstant::CXConstant` | 21 | `CXMatrix *` |
| `GetAddHs` | ARITH | EXPR | $0 | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXStringDefine::CXStringDefine`, `XYUtil::CXConstant::CXConstant` | 20 | `CXMatrix *` |
| `GetAirAn` | GETTER | NO_ARITH | $0 | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 15 | `CXConstant *` |
| `GetAl` | GETTER | TABLE_LOOKUP | $0 | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetAlpha` | GETTER | NO_ARITH | $0 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 15 | `CXConstant *` |
| `GetAmax` | ARITH | PARTIAL | $0, $1, $2 | `XYUtil::CXConstant::CXConstant` | 17 | `CXConstant *` |
| `GetAmaxFa` | GETTER | TABLE_LOOKUP | $0, $1 | `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `GetAnchorAcnFormula` | DRAW | NO_ARITH | c4, c1, c2, c3, layout, Scrn | `HWKDoubleArray::HWKDoubleArray`, `XYUtil::CXStringDefine::CXStringDefine`, `XYUtil::CXConstant::CXConstant` | 39 | `CXStringDefine *` |
| `GetAntiEQLevelString` | STRING | NO_ARITH | $0 | `XYUtil::CXStringDefine::CXStringDefine` | 15 | `CXStringDefine *` |
| `GetAntiNoiseDrawing` | STRING | NO_ARITH | $0 | `XYUtil::CXStringDefine::CXStringDefine` | 9 | `CXStringDefine *` |
| `GetAr` | COLLECTION | NO_ARITH | $0 | `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMapVariableArguments::CXMapVariableArguments`, `XYUtil::CXParameter::CXParameter` | 14 | `CXConstant *` |
| `GetArchBLen` | ARITH | PARTIAL | $0, $1 | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetArchHeight` | ARITH | PARTIAL | $0, $1 | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetArchShapeRatio` | ARITH | EXPR | f, L, type | `XYUtil::CXConstant::CXConstant` | 15 | `CXConstant *` |
| `GetArchSnowRatio` | ARITH | EXPR | f, L | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetAvKValue` | ARITH | EXPR | gk, ga, pk, pa | `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `GetBF` | GETTER | NO_ARITH | m, q, b, t | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetBackSlotStressRatio` | GETTER | NO_ARITH | SlotCount | `XYUtil::CXConstant::CXConstant` | 17 | `CXConstant *` |
| `GetBeamDflim` | ARITH | EXPR | $0, $1, $2 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 33 | `CXConstant *` |
| `GetBeamDfnum` | ARITH | EXPR | $0, $1, $2 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 32 | `CXConstant *` |
| `GetBeamTriHeight` | ARITH | EXPR | bfecal, beamcalmode, width, height | `XYUtil::CXConstant::CXConstant` | 11 | `CXConstant *` |
| `GetBeamUNmax` | GETTER | NO_ARITH | $0, $1, $2 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 20 | `CXConstant *` |
| `GetBeamUmax` | GETTER | NO_ARITH | $0, $1, $2 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 20 | `CXConstant *` |
| `GetBeamWTMax` | GETTER | NO_ARITH | $0, $1 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 16 | `CXConstant *` |
| `GetBgz` | GETTER | TABLE_LOOKUP | $0, $1, $2 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `GetBgzcal` | ARITH | PARTIAL | $0, $1, $2 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 12 | `CXConstant *` |
| `GetBoardMaterial` | STRING | NO_ARITH | x | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXStringDefine::CXStringDefine` | 10 | `CXStringDefine *` |
| `GetBoardType` | STRING | NO_ARITH | x | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXStringDefine::CXStringDefine` | 10 | `CXStringDefine *` |
| `GetBoltAn` | ARITH | NO_ARITH | layout, length, D0, index | `XYUtil::CXConstant::CXConstant` | 13 | `CXConstant *` |
| `GetBoltLength` | GETTER | NO_ARITH | layout | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetBoltLinkDrawing` | STRING | NO_ARITH | layout, length, width, title | `XYUtil::CXStringDefine::CXStringDefine` | 11 | `CXStringDefine *` |
| `GetBoltNRatio` | ARITH | EXPR | $0, $1 | `XYUtil::CXConstant::CXConstant` | 12 | `CXConstant *` |
| `GetBoltNcb` | GETTER | STRING_TABLE | $0, $1, $2 | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetBoltNumber` | GETTER | NO_ARITH | layout | `XYUtil::CXConstant::CXConstant` | 21 | `CXConstant *` |
| `GetBoltNvb` | GETTER | TABLE_LOOKUP | $0, $1, $2 | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetBoltPullState` | ARITH | EXPR | n, myc | `XYUtil::CXConstant::CXConstant` | 15 | `CXConstant *` |
| `GetBoltShearDesc` | STRING | NO_ARITH | simpleshear | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXStringDefine::CXStringDefine` | 11 | `CXStringDefine *` |
| `GetBoltTForceTable` | STRING | TABLE_BUILDER | layout, vs, t, fn | `XYUtil::CXStringDefine::CXStringDefine`, `XYUtil::CXConstant::CXConstant` | 12 | `CXStringDefine *` |
| `GetBoltVXYNum` | ARITH | EXPR | $0 | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 14 | `CXConstant *` |
| `GetCBoltLayoutNTable` | GETTER | NO_ARITH | N, M, layout | — | 6 | `longlong *` |
| `GetCBoltLayoutRR` | ARITH | PARTIAL | $0 | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 49 | `CXConstant *` |
| `GetCBoltLayoutTotalN` | GETTER | NO_ARITH | N, M, layout | — | 6 | `longlong *` |
| `GetCBoltTForceTable` | STRING | TABLE_BUILDER | layout, hs, vs, t, fn | `XYUtil::CXStringDefine::CXStringDefine`, `XYUtil::CXConstant::CXConstant` | 12 | `CXStringDefine *` |
| `GetCFrameReaction` | GETTER | NO_ARITH | hand, model, loads, widths, gkindex | `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess`, `XYUtil::CXMatrix::CXMatrix` | 19 | `CXMatrix *` |
| `GetCFrameReactionInfo` | GETTER | NO_ARITH | model, loads, widths | `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess`, `XYUtil::CXMatrix::CXMatrix` | 19 | `CXMatrix *` |
| `GetCLayoutS12` | GETTER | NO_ARITH | $0, $1 | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 24 | `CXConstant *` |
| `GetCLayoutSMin` | ARITH | EXPR | $0 | `XYUtil::CXConstant::CXConstant` | 12 | `CXConstant *` |
| `GetCPoleReaction` | GETTER | NO_ARITH | hand, model, loads, nodeindex | `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess`, `XYUtil::CXMatrix::CXMatrix` | 20 | `CXMatrix *` |
| `GetClosedShapeCoef` | GETTER | NO_ARITH | $0, $1, $2 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 13 | `CXConstant *` |
| `GetCommonBoltDrawing` | STRING | NO_ARITH | layout, length, width, title | `XYUtil::CXStringDefine::CXStringDefine` | 9 | `CXStringDefine *` |
| `GetCommonLayoutRRzox` | ARITH | PARTIAL | $0 | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 48 | `CXConstant *` |
| `GetCompKtheta` | ARITH | PARTIAL | w, a, De, t | `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `GetCompMetalPlateDe` | GETTER | NO_ARITH | $0, $1 | `HWKCompMetalPlateStrengthMap::GetDe`, `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `GetCompMetalPlateTe` | GETTER | NO_ARITH | $0, $1 | `HWKCompMetalPlateStrengthMap::GetTe`, `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `GetCompMetalPlateWe` | GETTER | NO_ARITH | $0, $1 | `HWKCompMetalPlateStrengthMap::GetWe`, `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `GetCurrentGlassName` | STRING | NO_ARITH | index, struct, nameo, namem, namei | `XYUtil::CXStringDefine::CXStringDefine` | 19 | `CXStringDefine *` |
| `GetDBFromT` | ARITH | PARTIAL | $0 | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetDSlopeShapeRatio` | ARITH | EXPR | rtype, H, D, angle, FM, DM | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 81 | `CXConstant *` |
| `GetDSlopeShapeRatioRegionText` | STRING | NO_ARITH | rtype | `XYUtil::CXStringDefine::CXStringDefine` | 25 | `CXStringDefine *` |
| `GetDe` | COLLECTION | INTERPOLATION | $0 | `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMapVariableArguments::CXMapVariableArguments`, `XYUtil::CXParameter::CXParameter` | 12 | `CXConstant *` |
| `GetDesity` | GETTER | NO_ARITH | $0 | `HWKWallMaterialDensity::GetMidu`, `XYUtil::Debug::log`, `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `GetDflim` | ARITH | EXPR | $0, $1, $2 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 35 | `CXConstant *` |
| `GetDfnum` | ARITH | EXPR | $0, $1, $2 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 32 | `CXConstant *` |
| `GetDispOfDistri` | ARITH | PARTIAL | qx, lx, Ex, Ix | `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `GetDispOfTrape` | ARITH | PARTIAL | qx, lx, ax, Ex, Ix | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetDispOfTriang` | ARITH | PARTIAL | qx, lx, Ex, Ix | `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `GetE` | GETTER | TABLE_LOOKUP | $0, $1 | `XYUtil::CXConstant::CXConstant` | 12 | `CXConstant *` |
| `GetEQFormat` | STRING | NO_ARITH | $0, $1 | `XYUtil::CXStringDefine::CXStringDefine` | 28 | `CXStringDefine *` |
| `GetEQSSubFormat` | STRING | NO_ARITH | $0, $1, $2 | `XYUtil::StringPointer::StringPointer`, `CXBasePtr::ControlAccess`, `XYUtil::CXMapDongdong::ChangeMap` | 21 | `CXStringDefine *` |
| `GetEarBoardDrawing` | STRING | NO_ARITH | index | `XYUtil::CXStringDefine::CXStringDefine` | 9 | `CXStringDefine *` |
| `GetEarthQuakeLevelString` | STRING | NO_ARITH | $0 | `XYUtil::CXStringDefine::CXStringDefine` | 15 | `CXStringDefine *` |
| `GetF02` | GETTER | NO_ARITH | $0, $1 | `HWKAlumStrengthMap::GetF02`, `HWKHRBFeStrength::GetFyk`, `HWKFeStrengthMap::GetFyk` | 22 | `CXConstant *` |
| `GetFEArchReaction` | GETTER | NO_ARITH | hand, sec, loads, poleinfo, gkindex, nodename | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `XYUtil::CXMatrix::CXMatrix` | 8 | `CXMatrix *` |
| `GetFc` | GETTER | NO_ARITH | $0 | `HWKConcreteStrength::GetFc`, `HWKFeStrengthMap::GetFce`, `XYUtil::CXConstant::CXConstant` | 13 | `CXConstant *` |
| `GetFcuk` | GETTER | NO_ARITH | $0, $1 | `HWKConcreteStrength::GetFcuk`, `XYUtil::CXConstant::CXConstant` | 13 | `CXConstant *` |
| `GetFp` | GETTER | TABLE_LOOKUP | $0, $1 | `XYUtil::CXConstant::CXConstant` | 11 | `CXConstant *` |
| `GetFrictionBoltAntiSlip` | GETTER | NO_ARITH | $0, $1 | `HWKAntiSlipRatioMap::GetMiu`, `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetFrictionBoltNtb` | GETTER | NO_ARITH | $0, $1 | `HWKFBoltPForceMap::GetF`, `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetFrictionBoltNvb` | GETTER | NO_ARITH | a, b, c | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetFrictionBoltPreForce` | GETTER | NO_ARITH | $0, $1 | `HWKFBoltPForceMap::GetF`, `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetFstk` | GETTER | NO_ARITH | $0, $1 | `HWKHRBFeStrength::GetFstk`, `HWKFeStrengthMap::GetFstk`, `HWKTSAnchorStrength::GetFstk` | 21 | `CXConstant *` |
| `GetFt` | GETTER | TABLE_LOOKUP | $0, $1 | `XYUtil::CXConstant::CXConstant` | 12 | `CXConstant *` |
| `GetFvk` | GETTER | NO_ARITH | $0 | `HWKStructGlueStrength::GetFvk`, `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetFyk` | GETTER | NO_ARITH | $0, $1 | `HWKHRBFeStrength::GetFyk`, `HWKFeStrengthMap::GetFyk`, `HWKTSAnchorStrength::GetFyk` | 21 | `CXConstant *` |
| `GetGama` | COLLECTION | NO_ARITH | $0 | `XYUtil::CXMapVariableArguments::CXMapVariableArguments`, `XYUtil::CXParameter::CXParameter`, `XYUtil::CXParameter::setDataType` | 10 | `CXConstant *` |
| `GetGlassDesc` | STRING | NO_ARITH | xdata, wo, wm, wi | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXStringDefine::CXStringDefine` | 28 | `CXStringDefine *` |
| `GetGlassLayerDesc` | STRING | NO_ARITH | $0 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXStringDefine::CXStringDefine` | 14 | `CXStringDefine *` |
| `GetGlassLayerThickness` | ARITH | PARTIAL | $0 | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetGlassName` | STRING | NO_ARITH | ta | `XYUtil::CXStringDefine::CXStringDefine` | 21 | `CXStringDefine *` |
| `GetGlassRatioMat` | ARITH | PARTIAL | ta, prefix | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant` | 30 | `CXConstant *` |
| `GetGlassThickMat` | GETTER | NO_ARITH | ta, prefix | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant` | 19 | `CXMatrix *` |
| `GetGlassThickMatT` | GETTER | NO_ARITH | ta | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 21 | `CXConstant *` |
| `GetGlassXDesc` | STRING | NO_ARITH | xo, xm, xi, wm, nm, ish | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXStringDefine::CXStringDefine` | 11 | `CXStringDefine *` |
| `GetGlueF1` | GETTER | NO_ARITH | $0 | `HWKGlassGlueStrength::GetF1`, `XYUtil::CXConstant::CXConstant` | 12 | `CXConstant *` |
| `GetGlueF2` | GETTER | NO_ARITH | $0 | `HWKGlassGlueStrength::GetF2`, `XYUtil::CXConstant::CXConstant` | 12 | `CXConstant *` |
| `GetGr` | GETTER | NO_ARITH | $0 | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 13 | `CXConstant *` |
| `GetHDr` | ARITH | EXPR | $0, $1 | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 14 | `CXConstant *` |
| `GetHasAirLayer` | GETTER | NO_ARITH | $0 | `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `GetHasHollow` | GETTER | NO_ARITH | ta | `XYUtil::CXConstant::CXConstant` | 14 | `CXConstant *` |
| `GetHc` | ARITH | EXPR | $0, $1 | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 14 | `CXTMatrix *` |
| `GetHr` | ARITH | EXPR | $0, $1, $2 | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::StringPointer::StringPointer`, `XYUtil::equals` | 15 | `CXConstant *` |
| `GetI10` | GETTER | NO_ARITH | $0 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 12 | `CXConstant *` |
| `GetInterpolation` | STRING | INTERPOLATION | MATA, MATV, pos | `HWKDoubleArray::HWKDoubleArray`, `HWKDoubleArray::append`, `HWKDoubleArray::asArrayPtr` | 15 | `CXConstant *` |
| `GetIz` | ARITH | EXPR | $0, $1 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 12 | `CXConstant *` |
| `GetKk` | GETTER | NO_ARITH | $0 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 12 | `CXConstant *` |
| `GetKtheta` | ARITH | PARTIAL | w, a, Ew, t | `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `GetKuf` | ARITH | PARTIAL | $0, $1 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 11 | `CXConstant *` |
| `GetKuh` | GETTER | NO_ARITH | $0 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 16 | `CXConstant *` |
| `GetKuz` | GETTER | NO_ARITH | $0, $1 | `XYUtil::StringPointer::StringPointer`, `CXBasePtr::ControlAccess`, `XYUtil::CXMapDongdong::ChangeMap` | 19 | `CXConstant *` |
| `GetKuzcal` | GETTER | TABLE_LOOKUP | $0, $1 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetLGAForceData` | GETTER | NO_ARITH | hand, checkpos | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::Access` | 17 | `CXMatrix *` |
| `GetLMCBeamDfGMax` | COLLECTION | NO_ARITH | $0 | `XYUtil::CXMapVariableArguments::CXMapVariableArguments`, `XYUtil::CXParameter::CXParameter`, `XYUtil::CXParameter::setDataType` | 14 | `CXConstant *` |
| `GetLMCBeamDflim` | GETTER | NO_ARITH | $0, $1 | `XYUtil::CXConstant::CXConstant` | 19 | `CXConstant *` |
| `GetLMCBeamDfnum` | GETTER | NO_ARITH | $0, $1 | `XYUtil::CXConstant::CXConstant` | 18 | `CXConstant *` |
| `GetLMCDflim` | GETTER | STRING_TABLE | $0, $1, $2 | `XYUtil::CXConstant::CXConstant` | 19 | `CXConstant *` |
| `GetLMCDfnum` | GETTER | STRING_TABLE | $0, $1, $2 | `XYUtil::CXConstant::CXConstant` | 22 | `CXConstant *` |
| `GetLPAngle` | ARITH | EXPR | angle, PRJ | `XYUtil::CXConstant::CXConstant` | 12 | `CXConstant *` |
| `GetLambda` | GETTER | NO_ARITH | $0, $1 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 15 | `CXConstant *` |
| `GetLarge` | STRING | NO_ARITH | $0, $1 | `XYUtil::CXStringDefine::CXStringDefine` | 18 | `CXStringDefine *` |
| `GetLayoutCenter` | ARITH | PARTIAL | $0 | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 122 | `CXConstant *` |
| `GetLayoutRR` | GETTER | NO_ARITH | $0 | — | 7 | `longlong *` |
| `GetLayoutRRzox` | GETTER | NO_ARITH | $0 | — | 7 | `longlong *` |
| `GetLayoutS2` | ARITH | NO_ARITH | $0, $1 | `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `GetLess` | STRING | NO_ARITH | $0, $1 | `XYUtil::CXStringDefine::CXStringDefine` | 18 | `CXStringDefine *` |
| `GetLockPointCount` | GETTER | NO_ARITH | width, height, left, top, right, bottom | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 20 | `CXMatrix *` |
| `GetM` | GETTER | TABLE_LOOKUP | $0, $1 | `XYUtil::CXConstant::CXConstant` | 13 | `CXConstant *` |
| `GetMCBoltFcb` | COLLECTION | NO_ARITH | $0 | `XYUtil::CXMapVariableArguments::CXMapVariableArguments`, `XYUtil::CXParameter::CXParameter`, `XYUtil::CXParameter::setDataType` | 17 | `CXConstant *` |
| `GetMatrixLength` | GETTER | NO_ARITH | $0 | `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `GetMatrixMul` | GETTER | NO_ARITH | $0, $1 | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 12 | `CXMatrix *` |
| `GetMaxBoltPullForce` | ARITH | NO_ARITH | n, myc, FORCEN, FORCEM, center | `XYUtil::CXConstant::CXConstant` | 15 | `CXConstant *` |
| `GetMaxBoltTForceData` | GETTER | NO_ARITH | layout, vs, t | `XYUtil::CXMatrix::CXMatrix` | 8 | `CXMatrix *` |
| `GetMaxCBoltTForceData` | GETTER | NO_ARITH | layout, hs, vs, t | `XYUtil::CXMatrix::CXMatrix` | 8 | `CXMatrix *` |
| `GetMetalNg` | GETTER | INTERPOLATION | $0, $1 | `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `GetMetalPlateFt` | GETTER | NO_ARITH | $0, $1 | `HWKMetalPlateStrength::GetFt`, `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `GetMetalPlateFv` | GETTER | NO_ARITH | $0, $1 | `HWKMetalPlateStrength::GetFv`, `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `GetMidLayerANoise` | GETTER | NO_ARITH | $0 | `XYUtil::CXConstant::CXConstant` | 24 | `CXConstant *` |
| `GetNextAirIndex` | ARITH | EXPR | $0, $1, $2 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXStringDefine::CXStringDefine` | 65 | `CXConstant *` |
| `GetNg` | GETTER | INTERPOLATION | $0, $1 | `XYUtil::CXConstant::CXConstant` | 15 | `CXConstant *` |
| `GetNu` | ARITH | PARTIAL | $0, $1 | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 15 | `CXConstant *` |
| `GetOKStr` | STRING | NO_ARITH | x | `XYUtil::CXStringDefine::CXStringDefine`, `CXBasePtr::ControlAccess`, `XYUtil::CXMapDongdong::ChangeMap` | 18 | `CXStringDefine *` |
| `GetOKString` | STRING | NO_ARITH | x | `CXBasePtr::ControlAccess`, `XYUtil::CXMapDongdong::ChangeMap`, `XYUtil::CXStringDefine::CXStringDefine` | 15 | `CXStringDefine *` |
| `GetOuterThicknessOfHollowGlass` | ARITH | EXPR | ta | `XYUtil::CXConstant::CXConstant` | 13 | `CXConstant *` |
| `GetPXTForceData` | GETTER | NO_ARITH | hand, checkpos | `CFEProblem::Exist`, `CXBasePtr::CXBasePtr`, `CXBasePtr::Access` | 17 | `CXMatrix *` |
| `GetPlateLoadString` | GETTER | NO_ARITH | wp, wkp, wn, wkn | `XYUtil::StringPointer::StringPointer` | 7 | `longlong *` |
| `GetPoleCalcStab` | ARITH | NO_ARITH | poleinfo | `CXPoleDataIOInfo::CXPoleDataIOInfo`, `CXPoleDataIOInfo::ReadData`, `XYUtil::CXConstant::CXConstant` | 25 | `CXConstant *` |
| `GetPoleDflim` | ARITH | EXPR | $0, $1, $2 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 35 | `CXConstant *` |
| `GetPoleDfnum` | ARITH | EXPR | $0, $1, $2 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 34 | `CXConstant *` |
| `GetPoleLambda` | ARITH | PARTIAL | L, Ix, Iy, A, Mat, sectype | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 22 | `CXConstant *` |
| `GetPr` | GETTER | NO_ARITH | $0 | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 13 | `CXConstant *` |
| `GetProjCodeInfo` | STRING | NO_ARITH | $0 | `XYUtil::equals`, `XYUtil::StringPointer::StringPointer`, `XYUtil::Debug::log` | 8 | `CXStringDefine *` |
| `GetRBoardEmitData` | GETTER | NO_ARITH | name | `CXBasePtr::ControlAccess`, `CADOEXRecordset::CADOEXRecordset`, `CADOEXRecordset::Open` | 12 | `CXConstant *` |
| `GetRDis` | ARITH | PARTIAL | wk, B, H, E, t, Hr | `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `GetRGlass` | ARITH | EXPR | ta, prefix | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXTMatrix::CXTMatrix` | 60 | `CXConstant *` |
| `GetRMidHollowGlass` | ARITH | PARTIAL | ta | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 27 | `CXConstant *` |
| `GetRecip` | GETTER | NO_ARITH | $0 | `XYUtil::CXConstant::CXConstant` | 11 | `CXConstant *` |
| `GetRibGlassThickMatrix` | GETTER | NO_ARITH | nums, glsthick, filmthick | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 28 | `CXConstant *` |
| `GetRibGlassThickness` | GETTER | NO_ARITH | glsthickMAT, al, glumodule, filmType | `XYUtil::CXConstant::CXConstant` | 11 | `CXConstant *` |
| `GetSABFt` | ARITH | NO_ARITH | q, H, W, t, c, side | `XYUtil::CXConstant::CXConstant` | 11 | `CXConstant *` |
| `GetSCBFt` | ARITH | NO_ARITH | q, a, b, r, n, t | `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `GetSDr` | ARITH | PARTIAL | $0, $1, $2, $3 | `XYUtil::CXConstant::CXConstant` | 52 | `CXConstant *` |
| `GetSFAlpha1` | GETTER | NO_ARITH | sectype | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 14 | `CXConstant *` |
| `GetSFAlpha2` | GETTER | NO_ARITH | lambda, sectype | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 17 | `CXConstant *` |
| `GetSFAlpha3` | GETTER | NO_ARITH | lambda, sectype | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 17 | `CXConstant *` |
| `GetSGPThickness` | GETTER | NO_ARITH | glsthickMAT, al, glumodule | `XYUtil::CXMatrix::CXMatrix` | 7 | `CXMatrix *` |
| `GetSHCPanelGama` | GETTER | NO_ARITH | fmat, bmat | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 13 | `CXConstant *` |
| `GetSLBFt` | ARITH | PARTIAL | q, a, b, r, n, t | `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `GetSLFt` | ARITH | PARTIAL | q, a, b, n, A, r | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetSMr` | ARITH | PARTIAL | $0, $1, $2, $3 | `XYUtil::CXConstant::CXConstant` | 54 | `CXConstant *` |
| `GetSNRatio` | GETTER | NO_ARITH | $0 | `XYUtil::CXConstant::CXConstant` | 28 | `CXConstant *` |
| `GetSSlopeShapeRatio` | ARITH | EXPR | rtype, angle, FM | `XYUtil::CXConstant::CXConstant` | 34 | `CXConstant *` |
| `GetSSubFormat` | STRING | NO_ARITH | $0, $1, $2 | `XYUtil::StringPointer::StringPointer`, `CXBasePtr::ControlAccess`, `XYUtil::CXMapDongdong::ChangeMap` | 19 | `CXStringDefine *` |
| `GetShapeCoefCalc` | ARITH | EXPR | zv, fv, vv, a, zf | `XYUtil::CXConstant::CXConstant` | 17 | `CXConstant *` |
| `GetSlopeShapeRatio` | ARITH | EXPR | a, type | `XYUtil::CXConstant::CXConstant` | 21 | `CXConstant *` |
| `GetSlopeSnowRatio` | ARITH | EXPR | a | `XYUtil::CXConstant::CXConstant` | 22 | `CXConstant *` |
| `GetSlopeSwMatrix` | GETTER | NO_ARITH | load1, load2, angle, mat | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 12 | `CXConstant *` |
| `GetSlopeWKP` | ARITH | EXPR | bgz, uz, w0, shapes, wlimitPos, wlimintNeg | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 14 | `CXConstant *` |
| `GetSlopeWindMatrix` | GETTER | NO_ARITH | ssk, ss, slk, sl, SwkMat, SwMat | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 18 | `CXConstant *` |
| `GetStabFactor` | ARITH | EXPR | lambda, sectype | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 22 | `CXConstant *` |
| `GetSteelShapeRatio` | GETTER | NO_ARITH | $0 | `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `GetStoneBoardAl` | ARITH | EXPR | Hw, Bw, SLOTTYPE, LINKSIDE, Hsl, Bsl | `XYUtil::CXConstant::CXConstant` | 40 | `CXConstant *` |
| `GetStoneBoardBl` | ARITH | EXPR | Hw, Bw, SLOTTYPE, LINKSIDE, Hsl, Bsl | `XYUtil::CXConstant::CXConstant` | 40 | `CXConstant *` |
| `GetStoneType` | GETTER | NO_ARITH | $0, $1 | `XYUtil::CXConstant::CXConstant` | 36 | `CXConstant *` |
| `GetStrCopy` | STRING | NO_ARITH | $0 | `XYUtil::CXStringDefine::CXStringDefine` | 8 | `CXStringDefine *` |
| `GetSupportReForce` | GETTER | NO_ARITH | mat, name | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant` | 17 | `CXMatrix *` |
| `GetSupportReForceWithSFloor` | GETTER | NO_ARITH | mat, name, sfloor | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant` | 18 | `CXMatrix *` |
| `GetTFromDB` | ARITH | EXPR | $0 | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetTeglass` | ARITH | EXPR | ta | `XYUtil::CXConstant::CXConstant` | 19 | `CXConstant *` |
| `GetTroembAsna` | ARITH | PARTIAL | num, Scrna, S | `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `GetTroembS` | ARITH | PARTIAL | curind, theind, num, Scrna, S | `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `GetTrueNvf` | ARITH | EXPR | t1, t, D, f | `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `GetTrueWk` | GETTER | NO_ARITH | gw, gwv, wk, lim | `XYUtil::CXConstant::CXConstant` | 32 | `CXConstant *` |
| `GetTwistCenter` | STRING | NO_ARITH | $0 | `XYUtil::CXPointerContainer::pointer`, `XYUtil::CXStringDefine::CXStringDefine` | 16 | `CXStringDefine *` |
| `GetTwistFEMaxStressN` | GETTER | NO_ARITH | prefix, doc, N, MY, MZ | `XYUtil::CXPointerContainer::pointer`, `XYUtil::CXConstant::CXConstant`, `HWKTwistInfoDocument::CalNormalStressOfMy` | 16 | `CXConstant *` |
| `GetTwistFEMaxVonmises` | GETTER | NO_ARITH | prefix, doc, N, MY, MZ, MT | `XYUtil::CXPointerContainer::pointer`, `XYUtil::CXConstant::CXConstant`, `HWKTwistInfoDocument::CalNormalStressOfMy` | 16 | `CXConstant *` |
| `GetTwistMaxStress` | GETTER | NO_ARITH | prefix, doc, mt | `XYUtil::CXPointerContainer::pointer`, `XYUtil::CXConstant::CXConstant`, `HWKTwistInfoDocument::GetNodeStressExtent` | 43 | `CXConstant *` |
| `GetTwistStressDrawing` | STRING | NO_ARITH | prefix, doc, mt, drawsize, bz | `XYUtil::CXPointerContainer::pointer`, `XYUtil::CXStringDefine::CXStringDefine` | 17 | `CXStringDefine *` |
| `GetUNmax` | GETTER | NO_ARITH | $0, $1, $2 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 17 | `CXConstant *` |
| `GetUSupportReForce` | ARITH | EXPR | mat1, mat2, name, truesimple | `XYUtil::StringPointer::StringPointer`, `XYUtil::equals`, `XYUtil::CXTMatrix::CXTMatrix` | 25 | `CXConstant *` |
| `GetUmax` | GETTER | NO_ARITH | $0, $1, $2 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 17 | `CXConstant *` |
| `GetVFrameReaction` | GETTER | NO_ARITH | model, loads, widths, gkindex, nodename | `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess`, `XYUtil::CXMatrix::CXMatrix` | 19 | `CXMatrix *` |
| `GetVFrameReactionInfo` | GETTER | NO_ARITH | model, loads, widths | `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess`, `XYUtil::CXMatrix::CXMatrix` | 19 | `CXMatrix *` |
| `GetVSecInfo` | GETTER | NO_ARITH | secdata, type | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 19 | `CXConstant *` |
| `GetVr` | GETTER | TABLE_LOOKUP | $0 | `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `GetWFD` | ARITH | EXPR | wf, B, H, T, mlen, E | `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `GetWFM` | ARITH | EXPR | wf, B, H, T, mlen | `XYUtil::CXConstant::CXConstant` | 11 | `CXConstant *` |
| `GetWFQ` | ARITH | EXPR | wf, B, H, T, mlen | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetWallUValue` | ARITH | EXPR | kvalues, types, areas | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 66 | `CXConstant *` |
| `GetWaterSealRatio` | GETTER | NO_ARITH | $0 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `GetWeldFa` | GETTER | NO_ARITH | $0 | `XYUtil::StringPointer::StringPointer`, `HWKFeStrengthMap::GetWeldFt`, `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetWeldNASDesc` | STRING | NO_ARITH | style, type, bdouble | `XYUtil::CXStringDefine::CXStringDefine` | 16 | `CXStringDefine *` |
| `GetWeldNASF` | ARITH | PARTIAL | data, index | `XYUtil::CXConstant::CXConstant` | 22 | `CXConstant *` |
| `GetWeldNASK` | GETTER | TABLE_LOOKUP | type, index | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetWeldNMVF` | ARITH | EXPR | mfy, vfa, mfx, nfa | `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `GetWeldNMVI` | ARITH | EXPR | length, b, hf, index | `XYUtil::CXConstant::CXConstant` | 12 | `CXConstant *` |
| `GetWindG` | GETTER | NO_ARITH | $0 | `XYUtil::CXConstant::CXConstant` | 13 | `CXConstant *` |
| `GetWindSpeed` | GETTER | NO_ARITH | $0 | `XYUtil::CXConstant::CXConstant` | 10 | `CXConstant *` |
| `GetYKType` | COLLECTION | NO_ARITH | $0 | `XYUtil::CXMapVariableArguments::CXMapVariableArguments`, `XYUtil::CXParameter::CXParameter`, `XYUtil::CXParameter::setDataType` | 11 | `CXConstant *` |
| `HWKGetMinValueOfFunction` | GETTER | NO_ARITH | q, L, W, N, loadn, E | `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXMatrix::CXMatrix` | 16 | `CXMatrix *` |
| `IsBgzTruncHigh` | GETTER | NO_ARITH | $0, $1 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant` | 43 | `CXConstant *` |
| `IsKuzTruncHigh` | GETTER | NO_ARITH | $0, $1 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXTMatrix::CXTMatrix`, `XYUtil::CXConstant::CXConstant` | 30 | `CXConstant *` |
| `IsLargeConLevel` | GETTER | NO_ARITH | $0 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant` | 8 | `CXConstant *` |
| `IsQBMQ` | COLLECTION | NO_ARITH | $0 | `XYUtil::CXMapVariableArguments::CXMapVariableArguments`, `XYUtil::CXParameter::CXParameter`, `XYUtil::CXParameter::setDataType` | 10 | `CXConstant *` |
| `IsRivetStress` | GETTER | NO_ARITH | $0 | `XYUtil::StringPointer::StringPointer`, `HWKRivetStrengthMap::GetFt`, `XYUtil::CXConstant::CXConstant` | 9 | `CXConstant *` |
| `RailingAddProb` | COLLECTION | NO_ARITH | $0 | `CXBasePtr::CXBasePtr`, `CXBasePtr::ControlAccess`, `XYUtil::CXConstant::CXConstant` | 16 | `CXBase *` |
| `RailingDelProb` | GETTER | NO_ARITH | handle | `CXBasePtr::CXBasePtr`, `CXBasePtr::Nullify`, `XYUtil::CXConstant::CXConstant` | 15 | `CXConstant *` |
| `ShellAddProb` | COLLECTION | NO_ARITH | $0 | `CXBase::CXBase`, `CXTypePtr::CXTypePtr`, `XYUtil::StringPointer::StringPointer` | 13 | `CXConstant *` |
| `ShellDelProb` | GETTER | NO_ARITH | handle | `CXBasePtr::CXBasePtr`, `CXBasePtr::Nullify`, `XYUtil::CXConstant::CXConstant` | 15 | `CXConstant *` |
| `StartAirIndex` | ARITH | EXPR | $0, $1, $2 | `XYUtil::StringPointer::StringPointer`, `XYUtil::CXConstant::CXConstant`, `XYUtil::CXStringDefine::CXStringDefine` | 65 | `CXConstant *` |
| `XDrawProMetalSheet_Face` | STRING | NO_ARITH | model, up, methodenum, title | `XYUtil::CXPointerContainer::pointer`, `HWKFEStructInfo::GetHWKGraphBaseCount`, `XYUtil::CXStringDefine::CXStringDefine` | 23 | `CXStringDefine *` |
| `XDrawProMetalSheet_Wire` | STRING | NO_ARITH | $0, $1 | `XYUtil::CXPointerContainer::pointer`, `XYUtil::CXStringDefine::CXStringDefine` | 11 | `CXStringDefine *` |
| `XDrawProfile` | STRING | NO_ARITH | $0, $1 | `XDBReader::XDBReader`, `XPlot::XPlot`, `XDBReader::GetSldData` | 15 | `CXStringDefine *` |
| `XDrawProfileEX` | DRAW | NO_ARITH | ID, SLD, DESC | `XYUtil::CXPointerContainer::pointer`, `XPlotSld::XPlotSld`, `XPlot::XPlot` | 10 | `CXStringDefine *` |
| `XDrawWeldNAS` | STRING | NO_ARITH | data | `XYUtil::CXStringDefine::CXStringDefine` | 9 | `CXStringDefine *` |
| `XDrawWeldNMV1` | STRING | NO_ARITH | data | `XYUtil::CXStringDefine::CXStringDefine` | 9 | `CXStringDefine *` |
| `XDrawWeldNV` | ARITH | PARTIAL | force, orient, number | `XYUtil::CXStringDefine::CXStringDefine` | 9 | `CXStringDefine *` |
