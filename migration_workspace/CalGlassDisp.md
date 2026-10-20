# Solve@HWKCalc_GlassDisp — 单函数取证包（生成物，勿手改）


来源 DLL：`evidence/baseline/extracted/cab/_F35DC0979FF04306B20773A25268CC58`

- SHA-256：`877057a46c5091aac738bc3b49efc3d9d501bdb69c76098b309a23bec03dbe78`
- ImageBase：`0x180000000`
- 导出命中：1 个带 `Solve@HWKCalc_GlassDisp` 的导出

## 1. 函数签名元数据

| 项 | 值 | 证据等级 |
| --- | --- | --- |
| 修饰名（原文） | `?Solve@HWKCalc_GlassDisp@@UEAAHXZ` | 导出表实测 |
| 修饰名尾部 | `UEAAHXZ` | 导出表实测 |
| 地址 | `start=0x8a2d0` `end=0x8a7c3` `len=0x4f3` | .pdata RUNTIME_FUNCTION 实测（编译器声明区间） |
| 函数名 | `Solve` | 导出表字符串 |
| 固定/可变参数 | 尾部以 `ZZ` 结尾=可变参数；否则未见 varargs 标记 | 修饰名规则 |
| 调用约定 / 返回类型 | `thiscall` / `int` | Ghidra 反编译 |
| nArgs（不含 this） | 0；形参原文 `int __thiscall HWKCalc_GlassDisp::Solve(HWKCalc_GlassDisp *this)` | Ghidra 反编译 |
| 形参名列表 | 无（无形参） | Ghidra 反编译 |

## 2. 已解析常量表

objdump 的 `# 0x180...` 注释在此处已解析为实际值，下游不要自行猜测十六进制。

| 引用地址 | 类别 | 已解析值 |
| --- | --- | --- |
| `0x18034f280` | import | `HWKPlot.dll!?g_bEmfOut@XPlot@@2_NA` |
| `0x180351438` | import | `api-ms-win-crt-runtime-l1-1-0.dll!_invalid_parameter_noinfo` |
| `0x180351440` | import | `api-ms-win-crt-runtime-l1-1-0.dll!_errno` |
| `0x180351508` | import | `api-ms-win-crt-string-l1-1-0.dll!wcsnlen` |
| `0x180363a08` | symbol | `??_7HWKCalc_AlbCJMStrength@@6B@+0xe0` |
| `0x180364d38` | symbol | `??_7HWKCalc_AnchorArea@@6B@+0x90` |
| `0x18036ee88` | symbol | `??_7HWKCalc_GlassDisp@@6B@+0x78` |
| `0x18036eea8` | symbol | `??_7HWKCalc_GlassDisp@@6B@+0x98` |
| `0x18036eed8` | symbol | `??_7HWKCalc_GlassDisp@@6B@+0xc8` |
| `0x18036ef00` | symbol | `??_7HWKCalc_GlassDisp@@6B@+0xf0` |
| `0x18036ef18` | symbol | `??_7HWKCalc_GlassDisp@@6B@+0x108` |
| `0x18036ef30` | symbol | `??_7HWKCalc_GlassDisp@@6B@+0x120` |
| `0x18036ef58` | symbol | `??_7HWKCalc_GlassDisp@@6B@+0x148` |
| `0x18036ef88` | symbol | `??_7HWKCalc_GlassDisp@@6B@+0x178` |
| `0x18036efc8` | symbol | `??_7HWKCalc_GlassDisp@@6B@+0x1b8` |

## 3. 涉及的全局变量

- `?g_uLoadCodeYear@XPlot@@2JA`：本 DLL 导出=否；本函数引用=否

## 4. 代码正文

### 4.1 eval 反编译伪代码（Ghidra 输出，非原始源码）

| 取证项 | 值 |
| --- | --- |
| evidence_id | `ev_d7c5777867b709405f9c46016b1a7e7cf04b15814dabab24d1d154fd404d55eb` |
| provider | `ghidra` Ghidra 12.1.4 |
| operation | `procedure_pseudo_code` |
| analysis_profile.digest | `23500ca49a1d1c30ade9499cc7ce87c5376277a0bb16225ff60f763f2dcfb2e2` |
| 原始 Evidence | `/Users/yeliang/Projects/YeliangDu/hwk-modern/migration_workspace/raw/Solve-HWKCalc_GlassDisp--UEAAHXZ.rea.json`（sha256 `d82d011f411317facc7b92c6bee37fae9164c71e435362e75b4cf5e0b410919d`） |
| confidence / authority | `observed` / `shipped-artifact` |

```c

/* WARNING: Removing unreachable block (ram,0x00018008a32e) */
/* public: virtual int __cdecl HWKCalc_GlassDisp::Solve(void) __ptr64 */

int __thiscall HWKCalc_GlassDisp::Solve(HWKCalc_GlassDisp *this)

{
  uint uVar1;
  void *pvVar2;
  int iVar3;
  longlong *plVar4;
  HWKGlass *pHVar5;
  longlong lVar6;
  ulonglong uVar7;
  longlong lVar8;
  size_t sVar9;
  int *piVar10;
  wchar_t *pwVar11;
  undefined2 *puVar12;
  int iVar13;
  longlong lVar14;
  longlong *plVar15;
  longlong lStackX_18;
  void *pvStackX_20;
  
                    /* 0x8a2d0  30445  ?Solve@HWKCalc_GlassDisp@@UEAAHXZ */
  plVar4 = (longlong *)FUN_180014a20();
  if (plVar4 == (longlong *)0x0) {
                    /* WARNING: Subroutine does not return */
    FUN_180014740(0x80004005);
  }
  lStackX_18 = (**(code **)(*plVar4 + 0x18))(plVar4);
  lStackX_18 = lStackX_18 + 0x18;
  uVar7 = 0xffffffffffffffff;
  do {
    uVar7 = uVar7 + 1;
  } while (L"WDISPLACEMENT"[uVar7] != L'\0');
  FUN_180015460(&lStackX_18,L"WDISPLACEMENT",uVar7 & 0xffffffff);
  pHVar5 = HWKGlass::Cast();
  lVar6 = _Cast_HWKSubInfo_Glass_SideSupport__SAPEAV1_PEBVCbObject___Z
                    (*(undefined8 *)(pHVar5 + 0x168));
  if ((lVar6 == 0) || (*(int *)(lVar6 + 0x40) != 0)) {
    uVar7 = 0xffffffffffffffff;
    do {
      uVar7 = uVar7 + 1;
    } while (L"WDISPLACEMENTTWOSIDE"[uVar7] != L'\0');
    FUN_180015460(&lStackX_18,L"WDISPLACEMENTTWOSIDE",uVar7 & 0xffffffff);
    pHVar5 = HWKCalc_GlassBase::GetGlassInfo((HWKCalc_GlassBase *)this);
    if (*(int *)(pHVar5 + 0x220) == 3) {
      pwVar11 = L"WDISPLACEMENTTWOSIDETHRLAYER";
      uVar7 = 0xffffffffffffffff;
      do {
        uVar7 = uVar7 + 1;
      } while (L"WDISPLACEMENTTWOSIDETHRLAYER"[uVar7] != L'\0');
    }
    else {
      pHVar5 = HWKCalc_GlassBase::GetGlassInfo((HWKCalc_GlassBase *)this);
      if (*(int *)(pHVar5 + 0x220) != 4) goto LAB_18008a5b6;
      pwVar11 = L"GLS_DISPFOURLAYERTWOSIDE";
      uVar7 = 0xffffffffffffffff;
      do {
        uVar7 = uVar7 + 1;
      } while (L"GLS_DISPFOURLAYERTWOSIDE"[uVar7] != L'\0');
    }
  }
  else {
    pHVar5 = HWKCalc_GlassBase::GetGlassInfo((HWKCalc_GlassBase *)this);
    if (*(int *)(pHVar5 + 0x220) == 3) {
      uVar7 = 0xffffffffffffffff;
      do {
        uVar7 = uVar7 + 1;
      } while (L"WDISPLACEMENTTHRLAYER"[uVar7] != L'\0');
      FUN_180015460(&lStackX_18,L"WDISPLACEMENTTHRLAYER",uVar7 & 0xffffffff);
    }
    lVar8 = (**(code **)(*(longlong *)this + 0x68))(this);
    if (0 < *(int *)(lVar8 + 0x8c)) {
      puVar12 = &DAT_180364d38;
      lVar8 = -1;
      do {
        lVar8 = lVar8 + 1;
      } while ((&DAT_180364d38)[lVar8] != 0);
      uVar7 = (longlong)&DAT_180364d38 - lStackX_18 >> 1;
      uVar1 = *(uint *)(lStackX_18 + -0x10);
      if ((int)lVar8 < 0) {
                    /* WARNING: Subroutine does not return */
        FUN_180014740(0x80070057);
      }
      sVar9 = wcsnlen(L"JD",(longlong)(int)lVar8);
      iVar3 = (int)sVar9;
      if (0x7fffffff - iVar3 < (int)uVar1) {
                    /* WARNING: Subroutine does not return */
        FUN_180014740(0x80070057);
      }
      iVar13 = uVar1 + iVar3;
      if (iVar13 < 0) {
                    /* WARNING: Subroutine does not return */
        FUN_180014740(0x80070057);
      }
      if ((int)(*(int *)(lStackX_18 + -0xc) - iVar13 | 1U - *(int *)(lStackX_18 + -8)) < 0) {
        FUN_180014db0(&lStackX_18,iVar13);
      }
      if (uVar7 <= uVar1) {
        puVar12 = (undefined2 *)(lStackX_18 + uVar7 * 2);
      }
      FUN_180014810(lStackX_18 + (ulonglong)uVar1 * 2,(longlong)iVar3,puVar12,sVar9 & 0xffffffff);
      if (*(int *)(lStackX_18 + -0xc) < iVar13) {
                    /* WARNING: Subroutine does not return */
        FUN_180014740(0x80070057);
      }
      *(int *)(lStackX_18 + -0x10) = iVar13;
      *(undefined2 *)(lStackX_18 + (longlong)iVar13 * 2) = 0;
    }
    if (*(char *)(lVar6 + 0x44) != '\0') {
      uVar7 = 0xffffffffffffffff;
      do {
        uVar7 = uVar7 + 1;
      } while (L"GLS_ASTMDISPMENT"[uVar7] != L'\0');
      FUN_180015460(&lStackX_18,L"GLS_ASTMDISPMENT",uVar7 & 0xffffffff);
      pHVar5 = HWKCalc_GlassBase::GetGlassInfo((HWKCalc_GlassBase *)this);
      if (*(int *)(pHVar5 + 0x220) == 3) {
        FUN_18008a090(&lStackX_18,L"THRLAYER");
      }
      else {
        pHVar5 = HWKCalc_GlassBase::GetGlassInfo((HWKCalc_GlassBase *)this);
        if (*(int *)(pHVar5 + 0x220) == 4) {
          FUN_18008a090(&lStackX_18,L"FOURLAYER");
        }
      }
      goto LAB_18008a5b6;
    }
    pHVar5 = HWKCalc_GlassBase::GetGlassInfo((HWKCalc_GlassBase *)this);
    if (*(int *)(pHVar5 + 0x220) != 4) goto LAB_18008a5b6;
    pwVar11 = L"GLS_DISPFOURLAYER";
    uVar7 = 0xffffffffffffffff;
    do {
      uVar7 = uVar7 + 1;
    } while (L"GLS_DISPFOURLAYER"[uVar7] != L'\0');
  }
  FUN_180015460(&lStackX_18,pwVar11,uVar7 & 0xffffffff);
LAB_18008a5b6:
  if (*g_bEmfOut_exref != (code)0x0) {
    if ((*(longlong **)(lStackX_18 + -0x18) == (longlong *)0x0) ||
       (plVar4 = (longlong *)(**(code **)(**(longlong **)(lStackX_18 + -0x18) + 0x20))(),
       plVar4 == (longlong *)0x0)) {
      plVar4 = (longlong *)FUN_180014a20();
      plVar4 = (longlong *)(**(code **)(*plVar4 + 0x20))(plVar4);
    }
    if (plVar4 == (longlong *)0x0) {
                    /* WARNING: Subroutine does not return */
      FUN_180014740(0x80004005);
    }
    lVar8 = (**(code **)(*plVar4 + 0x18))();
    lVar6 = lStackX_18;
    pvStackX_20 = (void *)(lVar8 + 0x18);
    iVar3 = *(int *)(lStackX_18 + -0x10);
    lVar14 = -1;
    do {
      lVar14 = lVar14 + 1;
    } while ((&DAT_180363a08)[lVar14] != 0);
    iVar13 = (int)lVar14 + iVar3;
    if (iVar13 < 0) {
                    /* WARNING: Subroutine does not return */
      FUN_180014740(0x80070057);
    }
    if ((int)(*(int *)(lVar8 + 0xc) - iVar13 | 1U - *(int *)(lVar8 + 0x10)) < 0) {
      FUN_180014db0(&pvStackX_20,iVar13);
    }
    pvVar2 = pvStackX_20;
    sVar9 = (longlong)(int)lVar14 * 2;
    if (sVar9 != 0) {
      if (pvStackX_20 == (void *)0x0) {
        piVar10 = _errno();
        *piVar10 = 0x16;
        _invalid_parameter_noinfo();
      }
      else {
        memcpy(pvStackX_20,&DAT_180363a08,sVar9);
      }
    }
    FUN_180014810((void *)(sVar9 + (longlong)pvVar2),(longlong)iVar3,lVar6,iVar3);
    lVar6 = lStackX_18;
    if (*(int *)((longlong)pvVar2 + -0xc) < iVar13) {
                    /* WARNING: Subroutine does not return */
      FUN_180014740(0x80070057);
    }
    *(int *)((longlong)pvVar2 + -0x10) = iVar13;
    *(undefined2 *)((longlong)pvVar2 + (longlong)iVar13 * 2) = 0;
    plVar4 = (longlong *)((longlong)pvVar2 + -0x18);
    plVar15 = (longlong *)(lStackX_18 + -0x18);
    if (plVar4 != plVar15) {
      if ((*(int *)(lStackX_18 + -8) < 0) || (*plVar4 != *plVar15)) {
        FUN_180015460(&lStackX_18,pvVar2,*(undefined4 *)((longlong)pvVar2 + -0x10));
      }
      else {
        lVar8 = FUN_180014780(plVar4);
        LOCK();
        piVar10 = (int *)(lVar6 + -8);
        iVar3 = *piVar10;
        *piVar10 = *piVar10 + -1;
        UNLOCK();
        if (iVar3 < 2) {
          (**(code **)(*(longlong *)*plVar15 + 8))((longlong *)*plVar15,plVar15);
        }
        lStackX_18 = lVar8 + 0x18;
      }
    }
    LOCK();
    piVar10 = (int *)((longlong)pvVar2 + -8);
    iVar3 = *piVar10;
    *piVar10 = *piVar10 + -1;
    UNLOCK();
    if (iVar3 < 2) {
      (**(code **)(*(longlong *)*plVar4 + 8))((longlong *)*plVar4,plVar4);
    }
  }
  iVar13 = HWKResultGenerator::DoMySolve((HWKResultGenerator *)this);
  LOCK();
  piVar10 = (int *)(lStackX_18 + -8);
  iVar3 = *piVar10;
  *piVar10 = *piVar10 + -1;
  UNLOCK();
  if (iVar3 < 2) {
    (**(code **)(**(longlong **)(lStackX_18 + -0x18) + 8))();
  }
  return iVar13;
}
```

反编译自带限制（原文摘录）：

- The session serves operations only after Ghidra reports default auto-analysis complete; incomplete analysis does not expose partial results.
- The imported Program and temporary project are ephemeral and deleted on close. Annotation operations edit session database metadata; original executable bytes are never written.
- Cancelling an active Ghidra request terminates its ephemeral database and discards session annotations. The selected target remains open; the next provider query imports the original artifact again.
- Default-space addresses use lowercase 0x-prefixed hexadecimal; other address spaces use <percent-encoded-space>:0x<hex>.
- Pseudocode is Ghidra decompiler output, not original source and not text-equivalent to Hopper output.
- External functions and functions without an analyzable body return null; other decompiler failures remain explicit.
- Ghidra Listing reports a terminal call at 0x18008a770 to 0x180014740 FUN_180014740 (external=false, thunk=false, hasNoReturn=true); fallthrough is excluded by Ghidra's flow model. This records Ghidra's FunctionManager flag, not an independent verification that the callee cannot return.
- Ghidra Listing reports a terminal call at 0x18008a77b to 0x180014740 FUN_180014740 (external=false, thunk=false, hasNoReturn=true); fallthrough is excluded by Ghidra's flow model. This records Ghidra's FunctionManager flag, not an independent verification that the callee cannot return.
- Ghidra Listing reports a terminal call at 0x18008a786 to 0x180014740 FUN_180014740 (external=false, thunk=false, hasNoReturn=true); fallthrough is excluded by Ghidra's flow model. This records Ghidra's FunctionManager flag, not an independent verification that the callee cannot return.
- Ghidra Listing reports a terminal call at 0x18008a791 to 0x180014740 FUN_180014740 (external=false, thunk=false, hasNoReturn=true); fallthrough is excluded by Ghidra's flow model. This records Ghidra's FunctionManager flag, not an independent verification that the callee cannot return.
- Ghidra Listing reports a terminal call at 0x18008a79c to 0x180014740 FUN_180014740 (external=false, thunk=false, hasNoReturn=true); fallthrough is excluded by Ghidra's flow model. This records Ghidra's FunctionManager flag, not an independent verification that the callee cannot return.
- Ghidra Listing reports a terminal call at 0x18008a7a7 to 0x180014740 FUN_180014740 (external=false, thunk=false, hasNoReturn=true); fallthrough is excluded by Ghidra's flow model. This records Ghidra's FunctionManager flag, not an independent verification that the callee cannot return.
- Ghidra Listing reports a terminal call at 0x18008a7b2 to 0x180014740 FUN_180014740 (external=false, thunk=false, hasNoReturn=true); fallthrough is excluded by Ghidra's flow model. This records Ghidra's FunctionManager flag, not an independent verification that the callee cannot return.
- Ghidra Listing reports a terminal call at 0x18008a7bd to 0x180014740 FUN_180014740 (external=false, thunk=false, hasNoReturn=true); fallthrough is excluded by Ghidra's flow model. This records Ghidra's FunctionManager flag, not an independent verification that the callee cannot return.
- macOS sessions require a matching executable Ghidra native decompiler; REA checks for it but does not build native components or change Gatekeeper quarantine state.

### 4.2 机器码直译（objdump 反汇编，用于核对常量与引用）

```asm
; ?Solve@HWKCalc_GlassDisp@@UEAAHXZ @ 0x8a2d0
18008a2d0: 48 89 4c 24 08                 movq %rcx, 0x8(%rsp)
18008a2d5: 55                             pushq %rbp
18008a2d6: 53                             pushq %rbx
18008a2d7: 56                             pushq %rsi
18008a2d8: 57                             pushq %rdi
18008a2d9: 41 54                          pushq %r12
18008a2db: 41 55                          pushq %r13
18008a2dd: 41 56                          pushq %r14
18008a2df: 41 57                          pushq %r15
18008a2e1: 48 8b ec                       movq %rsp, %rbp
18008a2e4: 48 83 ec 38                    subq $0x38, %rsp
18008a2e8: 48 c7 45 e8 fe ff ff ff        movq $-0x2, -0x18(%rbp)
18008a2f0: 4c 8b e1                       movq %rcx, %r12
18008a2f3: 33 c0                          xorl %eax, %eax
18008a2f5: 89 45 50                       movl %eax, 0x50(%rbp)
18008a2f8: e8 23 a7 f8 ff                 callq 0x180014a20 <?GetLength@HWKProfileBase@@QEBANXZ+0x10>
18008a2fd: 48 8b c8                       movq %rax, %rcx
18008a300: 48 85 c0                       testq %rax, %rax
18008a303: 0f 84 78 04 00 00              je 0x18008a781 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x4b1>
18008a309: 48 8b 00                       movq (%rax), %rax
18008a30c: ff 50 18                       callq *0x18(%rax)
18008a30f: 48 83 c0 18                    addq $0x18, %rax
18008a313: 48 89 45 58                    movq %rax, 0x58(%rbp)
18008a317: 48 8d 15 6a 4b 2e 00           leaq 0x2e4b6a(%rip), %rdx    # 0x18036ee88 <??_7HWKCalc_GlassDisp@@6B@+0x78>
18008a31e: 48 c7 c6 ff ff ff ff           movq $-0x1, %rsi
18008a325: 48 81 fa 00 00 01 00           cmpq $0x10000, %rdx          # imm = 0x10000
18008a32c: 73 0e                          jae 0x18008a33c <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x6c>
18008a32e: 0f b7 d2                       movzwl %dx, %edx
18008a331: 48 8d 4d 58                    leaq 0x58(%rbp), %rcx
18008a335: e8 e6 a8 f8 ff                 callq 0x180014c20 <?GetTemperature@HWKAirPropInfo@@QEBANXZ+0x10>
18008a33a: eb 1b                          jmp 0x18008a357 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x87>
18008a33c: 48 8b c6                       movq %rsi, %rax
18008a33f: 90                             nop 
18008a340: 48 ff c0                       incq %rax
18008a343: 66 83 3c 42 00                 cmpw $0x0, (%rdx,%rax,2)
18008a348: 75 f6                          jne 0x18008a340 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x70>
18008a34a: 44 8b c0                       movl %eax, %r8d
18008a34d: 48 8d 4d 58                    leaq 0x58(%rbp), %rcx
18008a351: e8 0a b1 f8 ff                 callq 0x180015460 <?SerializeRelations@HWKWinVFGDrawing@@MEAAXAEAVCbArchive@@QEAPEAVHWKWallContextObject@@@Z+0x20>
18008a356: 90                             nop 
18008a357: 49 8b 8c 24 80 00 00 00        movq 0x80(%r12), %rcx
18008a35f: e8 2c ad 0b 00                 callq 0x180145090 <?Cast@HWKGlass@@SAPEAV1@PEBVCbObject@@@Z>
18008a364: 48 8b 88 68 01 00 00           movq 0x168(%rax), %rcx
18008a36b: e8 20 2b 1b 00                 callq 0x18023ce90 <?Cast@HWKSubInfo_Glass_SideSupport@@SAPEAV1@PEBVCbObject@@@Z>
18008a370: 4c 8b e8                       movq %rax, %r13
18008a373: 48 85 c0                       testq %rax, %rax
18008a376: 0f 84 b8 01 00 00              je 0x18008a534 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x264>
18008a37c: 83 78 40 00                    cmpl $0x0, 0x40(%rax)
18008a380: 0f 85 ae 01 00 00              jne 0x18008a534 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x264>
18008a386: 49 8b cc                       movq %r12, %rcx
18008a389: e8 e2 fb ff ff                 callq 0x180089f70 <?GetGlassInfo@HWKCalc_GlassBase@@QEBAPEAVHWKGlass@@XZ>
18008a38e: 83 b8 20 02 00 00 03           cmpl $0x3, 0x220(%rax)
18008a395: 75 20                          jne 0x18008a3b7 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0xe7>
18008a397: 48 8d 15 0a 4b 2e 00           leaq 0x2e4b0a(%rip), %rdx    # 0x18036eea8 <??_7HWKCalc_GlassDisp@@6B@+0x98>
18008a39e: 48 8b c6                       movq %rsi, %rax
18008a3a1: 48 ff c0                       incq %rax
18008a3a4: 66 83 3c 42 00                 cmpw $0x0, (%rdx,%rax,2)
18008a3a9: 75 f6                          jne 0x18008a3a1 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0xd1>
18008a3ab: 44 8b c0                       movl %eax, %r8d
18008a3ae: 48 8d 4d 58                    leaq 0x58(%rbp), %rcx
18008a3b2: e8 a9 b0 f8 ff                 callq 0x180015460 <?SerializeRelations@HWKWinVFGDrawing@@MEAAXAEAVCbArchive@@QEAPEAVHWKWallContextObject@@@Z+0x20>
18008a3b7: 49 8b 04 24                    movq (%r12), %rax
18008a3bb: 49 8b cc                       movq %r12, %rcx
18008a3be: ff 50 68                       callq *0x68(%rax)
18008a3c1: 83 b8 8c 00 00 00 00           cmpl $0x0, 0x8c(%rax)
18008a3c8: 0f 8e c0 00 00 00              jle 0x18008a48e <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x1be>
18008a3ce: 48 8d 1d 63 a9 2d 00           leaq 0x2da963(%rip), %rbx    # 0x180364d38 <??_7HWKCalc_AnchorArea@@6B@+0x90>
18008a3d5: 48 8b ce                       movq %rsi, %rcx
18008a3d8: 0f 1f 84 00 00 00 00 00        nopl (%rax,%rax)
18008a3e0: 48 ff c1                       incq %rcx
18008a3e3: 66 83 3c 4b 00                 cmpw $0x0, (%rbx,%rcx,2)
18008a3e8: 75 f6                          jne 0x18008a3e0 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x110>
18008a3ea: 4c 8b f3                       movq %rbx, %r14
18008a3ed: 48 8b 45 58                    movq 0x58(%rbp), %rax
18008a3f1: 4c 2b f0                       subq %rax, %r14
18008a3f4: 49 d1 fe                       sarq %r14
18008a3f7: 44 8b 60 f0                    movl -0x10(%rax), %r12d
18008a3fb: 85 c9                          testl %ecx, %ecx
18008a3fd: 0f 88 89 03 00 00              js 0x18008a78c <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x4bc>
18008a403: 48 63 d1                       movslq %ecx, %rdx
18008a406: 48 8b cb                       movq %rbx, %rcx
18008a409: ff 15 f9 70 2c 00              callq *0x2c70f9(%rip)         # 0x180351508
18008a40f: 4c 8b f8                       movq %rax, %r15
18008a412: b9 ff ff ff 7f                 movl $0x7fffffff, %ecx       # imm = 0x7FFFFFFF
18008a417: 2b c8                          subl %eax, %ecx
18008a419: 41 3b cc                       cmpl %r12d, %ecx
18008a41c: 0f 8c 75 03 00 00              jl 0x18008a797 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x4c7>
18008a422: 41 8d 3c 04                    leal (%r12,%rax), %edi
18008a426: 85 ff                          testl %edi, %edi
18008a428: 0f 88 74 03 00 00              js 0x18008a7a2 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x4d2>
18008a42e: 48 8b 45 58                    movq 0x58(%rbp), %rax
18008a432: ba 01 00 00 00                 movl $0x1, %edx
18008a437: 2b 50 f8                       subl -0x8(%rax), %edx
18008a43a: 8b 48 f4                       movl -0xc(%rax), %ecx
18008a43d: 2b cf                          subl %edi, %ecx
18008a43f: 0b ca                          orl %edx, %ecx
18008a441: 7d 0f                          jge 0x18008a452 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x182>
18008a443: 8b d7                          movl %edi, %edx
18008a445: 48 8d 4d 58                    leaq 0x58(%rbp), %rcx
18008a449: e8 62 a9 f8 ff                 callq 0x180014db0 <?GetTemperature@HWKAirPropInfo@@QEBANXZ+0x1a0>
18008a44e: 48 8b 45 58                    movq 0x58(%rbp), %rax
18008a452: 4d 3b f4                       cmpq %r12, %r14
18008a455: 77 04                          ja 0x18008a45b <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x18b>
18008a457: 4a 8d 1c 70                    leaq (%rax,%r14,2), %rbx
18008a45b: 49 63 d7                       movslq %r15d, %rdx
18008a45e: 4a 8d 0c 60                    leaq (%rax,%r12,2), %rcx
18008a462: 45 8b cf                       movl %r15d, %r9d
18008a465: 4c 8b c3                       movq %rbx, %r8
18008a468: e8 a3 a3 f8 ff                 callq 0x180014810 <?VerifyBeforeSave@HWKWallContextObject@@UEAAXXZ+0x10>
18008a46d: 48 8b 45 58                    movq 0x58(%rbp), %rax
18008a471: 3b 78 f4                       cmpl -0xc(%rax), %edi
18008a474: 0f 8f 33 03 00 00              jg 0x18008a7ad <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x4dd>
18008a47a: 89 78 f0                       movl %edi, -0x10(%rax)
18008a47d: 48 63 cf                       movslq %edi, %rcx
18008a480: 48 8b 45 58                    movq 0x58(%rbp), %rax
18008a484: 33 d2                          xorl %edx, %edx
18008a486: 66 89 14 48                    movw %dx, (%rax,%rcx,2)
18008a48a: 4c 8b 65 48                    movq 0x48(%rbp), %r12
18008a48e: 41 80 7d 44 00                 cmpb $0x0, 0x44(%r13)
18008a493: 74 71                          je 0x18008a506 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x236>
18008a495: 48 8d 15 3c 4a 2e 00           leaq 0x2e4a3c(%rip), %rdx    # 0x18036eed8 <??_7HWKCalc_GlassDisp@@6B@+0xc8>
18008a49c: 48 8b c6                       movq %rsi, %rax
18008a49f: 90                             nop 
18008a4a0: 48 ff c0                       incq %rax
18008a4a3: 66 83 3c 42 00                 cmpw $0x0, (%rdx,%rax,2)
18008a4a8: 75 f6                          jne 0x18008a4a0 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x1d0>
18008a4aa: 44 8b c0                       movl %eax, %r8d
18008a4ad: 48 8d 4d 58                    leaq 0x58(%rbp), %rcx
18008a4b1: e8 aa af f8 ff                 callq 0x180015460 <?SerializeRelations@HWKWinVFGDrawing@@MEAAXAEAVCbArchive@@QEAPEAVHWKWallContextObject@@@Z+0x20>
18008a4b6: 49 8b cc                       movq %r12, %rcx
18008a4b9: e8 b2 fa ff ff                 callq 0x180089f70 <?GetGlassInfo@HWKCalc_GlassBase@@QEBAPEAVHWKGlass@@XZ>
18008a4be: 83 b8 20 02 00 00 03           cmpl $0x3, 0x220(%rax)
18008a4c5: 75 15                          jne 0x18008a4dc <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x20c>
18008a4c7: 48 8d 15 32 4a 2e 00           leaq 0x2e4a32(%rip), %rdx    # 0x18036ef00 <??_7HWKCalc_GlassDisp@@6B@+0xf0>
18008a4ce: 48 8d 4d 58                    leaq 0x58(%rbp), %rcx
18008a4d2: e8 b9 fb ff ff                 callq 0x18008a090 <??1HWKCalc_GlassDisp@@UEAA@XZ+0x10>
18008a4d7: e9 da 00 00 00                 jmp 0x18008a5b6 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x2e6>
18008a4dc: 49 8b cc                       movq %r12, %rcx
18008a4df: e8 8c fa ff ff                 callq 0x180089f70 <?GetGlassInfo@HWKCalc_GlassBase@@QEBAPEAVHWKGlass@@XZ>
18008a4e4: 83 b8 20 02 00 00 04           cmpl $0x4, 0x220(%rax)
18008a4eb: 0f 85 c5 00 00 00              jne 0x18008a5b6 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x2e6>
18008a4f1: 48 8d 15 20 4a 2e 00           leaq 0x2e4a20(%rip), %rdx    # 0x18036ef18 <??_7HWKCalc_GlassDisp@@6B@+0x108>
18008a4f8: 48 8d 4d 58                    leaq 0x58(%rbp), %rcx
18008a4fc: e8 8f fb ff ff                 callq 0x18008a090 <??1HWKCalc_GlassDisp@@UEAA@XZ+0x10>
18008a501: e9 b0 00 00 00                 jmp 0x18008a5b6 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x2e6>
18008a506: 49 8b cc                       movq %r12, %rcx
18008a509: e8 62 fa ff ff                 callq 0x180089f70 <?GetGlassInfo@HWKCalc_GlassBase@@QEBAPEAVHWKGlass@@XZ>
18008a50e: 83 b8 20 02 00 00 04           cmpl $0x4, 0x220(%rax)
18008a515: 0f 85 9b 00 00 00              jne 0x18008a5b6 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x2e6>
18008a51b: 48 8d 15 0e 4a 2e 00           leaq 0x2e4a0e(%rip), %rdx    # 0x18036ef30 <??_7HWKCalc_GlassDisp@@6B@+0x120>
18008a522: 48 8b c6                       movq %rsi, %rax
18008a525: 48 ff c0                       incq %rax
18008a528: 66 83 3c 42 00                 cmpw $0x0, (%rdx,%rax,2)
18008a52d: 75 f6                          jne 0x18008a525 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x255>
18008a52f: e9 76 00 00 00                 jmp 0x18008a5aa <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x2da>
18008a534: 48 8d 15 1d 4a 2e 00           leaq 0x2e4a1d(%rip), %rdx    # 0x18036ef58 <??_7HWKCalc_GlassDisp@@6B@+0x148>
18008a53b: 48 8b c6                       movq %rsi, %rax
18008a53e: 66 90                          nop 
18008a540: 48 ff c0                       incq %rax
18008a543: 66 83 3c 42 00                 cmpw $0x0, (%rdx,%rax,2)
18008a548: 75 f6                          jne 0x18008a540 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x270>
18008a54a: 44 8b c0                       movl %eax, %r8d
18008a54d: 48 8d 4d 58                    leaq 0x58(%rbp), %rcx
18008a551: e8 0a af f8 ff                 callq 0x180015460 <?SerializeRelations@HWKWinVFGDrawing@@MEAAXAEAVCbArchive@@QEAPEAVHWKWallContextObject@@@Z+0x20>
18008a556: 49 8b cc                       movq %r12, %rcx
18008a559: e8 12 fa ff ff                 callq 0x180089f70 <?GetGlassInfo@HWKCalc_GlassBase@@QEBAPEAVHWKGlass@@XZ>
18008a55e: 83 b8 20 02 00 00 03           cmpl $0x3, 0x220(%rax)
18008a565: 75 16                          jne 0x18008a57d <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x2ad>
18008a567: 48 8d 15 1a 4a 2e 00           leaq 0x2e4a1a(%rip), %rdx    # 0x18036ef88 <??_7HWKCalc_GlassDisp@@6B@+0x178>
18008a56e: 48 8b c6                       movq %rsi, %rax
18008a571: 48 ff c0                       incq %rax
18008a574: 66 83 3c 42 00                 cmpw $0x0, (%rdx,%rax,2)
18008a579: 75 f6                          jne 0x18008a571 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x2a1>
18008a57b: eb 2d                          jmp 0x18008a5aa <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x2da>
18008a57d: 49 8b cc                       movq %r12, %rcx
18008a580: e8 eb f9 ff ff                 callq 0x180089f70 <?GetGlassInfo@HWKCalc_GlassBase@@QEBAPEAVHWKGlass@@XZ>
18008a585: 83 b8 20 02 00 00 04           cmpl $0x4, 0x220(%rax)
18008a58c: 75 28                          jne 0x18008a5b6 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x2e6>
18008a58e: 48 8d 15 33 4a 2e 00           leaq 0x2e4a33(%rip), %rdx    # 0x18036efc8 <??_7HWKCalc_GlassDisp@@6B@+0x1b8>
18008a595: 48 8b c6                       movq %rsi, %rax
18008a598: 0f 1f 84 00 00 00 00 00        nopl (%rax,%rax)
18008a5a0: 48 ff c0                       incq %rax
18008a5a3: 66 83 3c 42 00                 cmpw $0x0, (%rdx,%rax,2)
18008a5a8: 75 f6                          jne 0x18008a5a0 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x2d0>
18008a5aa: 44 8b c0                       movl %eax, %r8d
18008a5ad: 48 8d 4d 58                    leaq 0x58(%rbp), %rcx
18008a5b1: e8 aa ae f8 ff                 callq 0x180015460 <?SerializeRelations@HWKWinVFGDrawing@@MEAAXAEAVCbArchive@@QEAPEAVHWKWallContextObject@@@Z+0x20>
18008a5b6: 48 8b 05 c3 4c 2c 00           movq 0x2c4cc3(%rip), %rax    # 0x18034f280
18008a5bd: 80 38 00                       cmpb $0x0, (%rax)
18008a5c0: 0f 84 68 01 00 00              je 0x18008a72e <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x45e>
18008a5c6: 48 8b 45 58                    movq 0x58(%rbp), %rax
18008a5ca: 48 8b 48 e8                    movq -0x18(%rax), %rcx
18008a5ce: 48 85 c9                       testq %rcx, %rcx
18008a5d1: 74 0e                          je 0x18008a5e1 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x311>
18008a5d3: 48 8b 01                       movq (%rcx), %rax
18008a5d6: ff 50 20                       callq *0x20(%rax)
18008a5d9: 48 8b c8                       movq %rax, %rcx
18008a5dc: 48 85 c0                       testq %rax, %rax
18008a5df: 75 11                          jne 0x18008a5f2 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x322>
18008a5e1: e8 3a a4 f8 ff                 callq 0x180014a20 <?GetLength@HWKProfileBase@@QEBANXZ+0x10>
18008a5e6: 48 8b 10                       movq (%rax), %rdx
18008a5e9: 48 8b c8                       movq %rax, %rcx
18008a5ec: ff 52 20                       callq *0x20(%rdx)
18008a5ef: 48 8b c8                       movq %rax, %rcx
18008a5f2: 48 85 c9                       testq %rcx, %rcx
18008a5f5: 0f 84 bd 01 00 00              je 0x18008a7b8 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x4e8>
18008a5fb: 48 8b 01                       movq (%rcx), %rax
18008a5fe: ff 50 18                       callq *0x18(%rax)
18008a601: 48 8d 58 18                    leaq 0x18(%rax), %rbx
18008a605: 48 89 5d 60                    movq %rbx, 0x60(%rbp)
18008a609: b9 01 00 00 00                 movl $0x1, %ecx
18008a60e: 89 4d 50                       movl %ecx, 0x50(%rbp)
18008a611: 4c 8b 6d 58                    movq 0x58(%rbp), %r13
18008a615: 4d 63 7d f0                    movslq -0x10(%r13), %r15
18008a619: 48 8d 15 e8 93 2d 00           leaq 0x2d93e8(%rip), %rdx    # 0x180363a08 <??_7HWKCalc_AlbCJMStrength@@6B@+0xe0>
18008a620: 48 8b fe                       movq %rsi, %rdi
18008a623: 48 ff c7                       incq %rdi
18008a626: 66 83 3c 7a 00                 cmpw $0x0, (%rdx,%rdi,2)
18008a62b: 75 f6                          jne 0x18008a623 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x353>
18008a62d: 46 8d 34 3f                    leal (%rdi,%r15), %r14d
18008a631: 45 85 f6                       testl %r14d, %r14d
18008a634: 0f 88 31 01 00 00              js 0x18008a76b <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x49b>
18008a63a: 2b 4b f8                       subl -0x8(%rbx), %ecx
18008a63d: 8b 43 f4                       movl -0xc(%rbx), %eax
18008a640: 41 2b c6                       subl %r14d, %eax
18008a643: 0b c1                          orl %ecx, %eax
18008a645: 7d 17                          jge 0x18008a65e <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x38e>
18008a647: 41 8b d6                       movl %r14d, %edx
18008a64a: 48 8d 4d 60                    leaq 0x60(%rbp), %rcx
18008a64e: e8 5d a7 f8 ff                 callq 0x180014db0 <?GetTemperature@HWKAirPropInfo@@QEBANXZ+0x1a0>
18008a653: 48 8b 5d 60                    movq 0x60(%rbp), %rbx
18008a657: 48 8d 15 aa 93 2d 00           leaq 0x2d93aa(%rip), %rdx    # 0x180363a08 <??_7HWKCalc_AlbCJMStrength@@6B@+0xe0>
18008a65e: 48 63 c7                       movslq %edi, %rax
18008a661: 48 8d 3c 00                    leaq (%rax,%rax), %rdi
18008a665: 48 85 ff                       testq %rdi, %rdi
18008a668: 74 24                          je 0x18008a68e <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x3be>
18008a66a: 48 85 db                       testq %rbx, %rbx
18008a66d: 75 14                          jne 0x18008a683 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x3b3>
18008a66f: ff 15 cb 6d 2c 00              callq *0x2c6dcb(%rip)         # 0x180351440
18008a675: c7 00 16 00 00 00              movl $0x16, (%rax)
18008a67b: ff 15 b7 6d 2c 00              callq *0x2c6db7(%rip)         # 0x180351438
18008a681: eb 0b                          jmp 0x18008a68e <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x3be>
18008a683: 4c 8b c7                       movq %rdi, %r8
18008a686: 48 8b cb                       movq %rbx, %rcx
18008a689: e8 34 0f 2a 00                 callq 0x18032b5c2 <?rpLast@LoadProxyIterator@HWKLoadexBase@@CAAEAPEAV12@XZ+0x21a2>
18008a68e: 49 8b d7                       movq %r15, %rdx
18008a691: 48 8d 0c 1f                    leaq (%rdi,%rbx), %rcx
18008a695: 45 8b cf                       movl %r15d, %r9d
18008a698: 4d 8b c5                       movq %r13, %r8
18008a69b: e8 70 a1 f8 ff                 callq 0x180014810 <?VerifyBeforeSave@HWKWallContextObject@@UEAAXXZ+0x10>
18008a6a0: 44 3b 73 f4                    cmpl -0xc(%rbx), %r14d
18008a6a4: 0f 8f cc 00 00 00              jg 0x18008a776 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x4a6>
18008a6aa: 44 89 73 f0                    movl %r14d, -0x10(%rbx)
18008a6ae: 49 63 c6                       movslq %r14d, %rax
18008a6b1: 33 c9                          xorl %ecx, %ecx
18008a6b3: 66 89 0c 43                    movw %cx, (%rbx,%rax,2)
18008a6b7: 48 8d 7b e8                    leaq -0x18(%rbx), %rdi
18008a6bb: 4c 8b 75 58                    movq 0x58(%rbp), %r14
18008a6bf: 49 83 c6 e8                    addq $-0x18, %r14
18008a6c3: 49 3b fe                       cmpq %r14, %rdi
18008a6c6: 74 4e                          je 0x18008a716 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x446>
18008a6c8: 41 39 4e 10                    cmpl %ecx, 0x10(%r14)
18008a6cc: 7c 37                          jl 0x18008a705 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x435>
18008a6ce: 49 8b 06                       movq (%r14), %rax
18008a6d1: 48 39 07                       cmpq %rax, (%rdi)
18008a6d4: 75 2f                          jne 0x18008a705 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x435>
18008a6d6: 48 8b cf                       movq %rdi, %rcx
18008a6d9: e8 a2 a0 f8 ff                 callq 0x180014780 <??4HWKREditInnerFunc@@QEAAAEAV0@AEBV0@@Z+0x10>
18008a6de: 48 8b d8                       movq %rax, %rbx
18008a6e1: 8b ce                          movl %esi, %ecx
18008a6e3: f0                             lock 
18008a6e4: 41 0f c1 4e 10                 xaddl %ecx, 0x10(%r14)
18008a6e9: 83 e9 01                       subl $0x1, %ecx
18008a6ec: 7f 0d                          jg 0x18008a6fb <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x42b>
18008a6ee: 49 8b 0e                       movq (%r14), %rcx
18008a6f1: 4c 8b 01                       movq (%rcx), %r8
18008a6f4: 49 8b d6                       movq %r14, %rdx
18008a6f7: 41 ff 50 08                    callq *0x8(%r8)
18008a6fb: 48 8d 43 18                    leaq 0x18(%rbx), %rax
18008a6ff: 48 89 45 58                    movq %rax, 0x58(%rbp)
18008a703: eb 11                          jmp 0x18008a716 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x446>
18008a705: 44 8b 43 f0                    movl -0x10(%rbx), %r8d
18008a709: 48 8b d3                       movq %rbx, %rdx
18008a70c: 48 8d 4d 58                    leaq 0x58(%rbp), %rcx
18008a710: e8 4b ad f8 ff                 callq 0x180015460 <?SerializeRelations@HWKWinVFGDrawing@@MEAAXAEAVCbArchive@@QEAPEAVHWKWallContextObject@@@Z+0x20>
18008a715: 90                             nop 
18008a716: 8b c6                          movl %esi, %eax
18008a718: f0                             lock 
18008a719: 0f c1 47 10                    xaddl %eax, 0x10(%rdi)
18008a71d: 83 e8 01                       subl $0x1, %eax
18008a720: 7f 0c                          jg 0x18008a72e <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x45e>
18008a722: 48 8b 0f                       movq (%rdi), %rcx
18008a725: 48 8b 01                       movq (%rcx), %rax
18008a728: 48 8b d7                       movq %rdi, %rdx
18008a72b: ff 50 08                       callq *0x8(%rax)
18008a72e: 48 8d 55 58                    leaq 0x58(%rbp), %rdx
18008a732: 49 8b cc                       movq %r12, %rcx
18008a735: e8 26 4f 17 00                 callq 0x1801ff660 <?DoMySolve@HWKResultGenerator@@IEAAHAEBV?$CStringT@_WV?$StrTraitATL@_WV?$ChTraitsCRT@_W@ATL@@@ATL@@@ATL@@@Z>
18008a73a: 8b d8                          movl %eax, %ebx
18008a73c: 48 8b 55 58                    movq 0x58(%rbp), %rdx
18008a740: 48 83 c2 e8                    addq $-0x18, %rdx
18008a744: f0                             lock 
18008a745: 0f c1 72 10                    xaddl %esi, 0x10(%rdx)
18008a749: 83 ee 01                       subl $0x1, %esi
18008a74c: 7f 0a                          jg 0x18008a758 <?Solve@HWKCalc_GlassDisp@@UEAAHXZ+0x488>
18008a74e: 48 8b 0a                       movq (%rdx), %rcx
18008a751: 4c 8b 01                       movq (%rcx), %r8
18008a754: 41 ff 50 08                    callq *0x8(%r8)
18008a758: 8b c3                          movl %ebx, %eax
18008a75a: 48 83 c4 38                    addq $0x38, %rsp
18008a75e: 41 5f                          popq %r15
18008a760: 41 5e                          popq %r14
18008a762: 41 5d                          popq %r13
18008a764: 41 5c                          popq %r12
18008a766: 5f                             popq %rdi
18008a767: 5e                             popq %rsi
18008a768: 5b                             popq %rbx
18008a769: 5d                             popq %rbp
18008a76a: c3                             retq 
18008a76b: b9 57 00 07 80                 movl $0x80070057, %ecx       # imm = 0x80070057
18008a770: e8 cb 9f f8 ff                 callq 0x180014740 <??OHWKAirPropInfo@@QEBAHAEBV0@@Z+0x200>
18008a775: cc                             int3 
18008a776: b9 57 00 07 80                 movl $0x80070057, %ecx       # imm = 0x80070057
18008a77b: e8 c0 9f f8 ff                 callq 0x180014740 <??OHWKAirPropInfo@@QEBAHAEBV0@@Z+0x200>
18008a780: 90                             nop 
18008a781: b9 05 40 00 80                 movl $0x80004005, %ecx       # imm = 0x80004005
18008a786: e8 b5 9f f8 ff                 callq 0x180014740 <??OHWKAirPropInfo@@QEBAHAEBV0@@Z+0x200>
18008a78b: 90                             nop 
18008a78c: b9 57 00 07 80                 movl $0x80070057, %ecx       # imm = 0x80070057
18008a791: e8 aa 9f f8 ff                 callq 0x180014740 <??OHWKAirPropInfo@@QEBAHAEBV0@@Z+0x200>
18008a796: cc                             int3 
18008a797: b9 57 00 07 80                 movl $0x80070057, %ecx       # imm = 0x80070057
18008a79c: e8 9f 9f f8 ff                 callq 0x180014740 <??OHWKAirPropInfo@@QEBAHAEBV0@@Z+0x200>
18008a7a1: cc                             int3 
18008a7a2: b9 57 00 07 80                 movl $0x80070057, %ecx       # imm = 0x80070057
18008a7a7: e8 94 9f f8 ff                 callq 0x180014740 <??OHWKAirPropInfo@@QEBAHAEBV0@@Z+0x200>
18008a7ac: cc                             int3 
18008a7ad: b9 57 00 07 80                 movl $0x80070057, %ecx       # imm = 0x80070057
18008a7b2: e8 89 9f f8 ff                 callq 0x180014740 <??OHWKAirPropInfo@@QEBAHAEBV0@@Z+0x200>
18008a7b7: 90                             nop 
18008a7b8: b9 05 40 00 80                 movl $0x80004005, %ecx       # imm = 0x80004005
18008a7bd: e8 7e 9f f8 ff                 callq 0x180014740 <??OHWKAirPropInfo@@QEBAHAEBV0@@Z+0x200>
```
