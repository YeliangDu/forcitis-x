# Serialize@HWKCalc_GlassDisp — 单函数取证包（生成物，勿手改）


来源 DLL：`evidence/baseline/extracted/cab/_F35DC0979FF04306B20773A25268CC58`

- SHA-256：`877057a46c5091aac738bc3b49efc3d9d501bdb69c76098b309a23bec03dbe78`
- ImageBase：`0x180000000`
- 导出命中：1 个带 `Serialize@HWKCalc_GlassDisp` 的导出

## 1. 函数签名元数据

| 项 | 值 | 证据等级 |
| --- | --- | --- |
| 修饰名（原文） | `?Serialize@HWKCalc_GlassDisp@@MEAAXAEAVCbArchive@@@Z` | 导出表实测 |
| 同址别名 | `?Serialize@HWKCalc_GlassArea@@MEAAXAEAVCbArchive@@@Z`, `?Serialize@HWKCalc_GlassStrength@@MEAAXAEAVCbArchive@@@Z`, `?Serialize@HWKCalc_GlassWeight@@MEAAXAEAVCbArchive@@@Z`（导出表里同一地址多个名字，语义归属需人工判断） | 导出表实测 |
| 修饰名尾部 | `MEAAXAEAVCbArchive@@@Z` | 导出表实测 |
| 地址 | `start=0x89be0` `end=0x89c00` `len=0x20` | 导出表邻接实测（未用 .pdata 校正） |
| 函数名 | `Serialize` | 导出表字符串 |
| 固定/可变参数 | 尾部以 `ZZ` 结尾=可变参数；否则未见 varargs 标记 | 修饰名规则 |
| 调用约定 / 返回类型 | `thiscall` / `void` | Ghidra 反编译 |
| nArgs（不含 this） | 1；形参原文 `void __thiscall HWKCalc_GlassArea::Serialize(HWKCalc_GlassArea *this,CbArchive *param_1)` | Ghidra 反编译 |
| 形参名列表 | `param_1` | Ghidra 反编译 |

## 2. 已解析常量表

objdump 的 `# 0x180...` 注释在此处已解析为实际值，下游不要自行猜测十六进制。

| 引用地址 | 类别 | 已解析值 |
| --- | --- | --- |
| `0x18034f0b8` | import | `HWKPlot.dll!?IsStoring@CbArchive@@QEBA_NXZ` |

## 3. 涉及的全局变量

无（未命中可识别的全局数据引用）

## 4. 代码正文

### 4.1 eval 反编译伪代码（Ghidra 输出，非原始源码）

| 取证项 | 值 |
| --- | --- |
| evidence_id | `ev_67bebb42df3b75485e215306c0917aaf7ff7f302fe84117dadee79ddc420cf95` |
| provider | `ghidra` Ghidra 12.1.4 |
| operation | `procedure_pseudo_code` |
| analysis_profile.digest | `23500ca49a1d1c30ade9499cc7ce87c5376277a0bb16225ff60f763f2dcfb2e2` |
| 原始 Evidence | `/Users/yeliang/Projects/YeliangDu/hwk-modern/migration_workspace/raw/Serialize-HWKCalc_GlassDisp--MEAAXAEAVCbArchive---Z.rea.json`（sha256 `08ff701474b7c4b788bcd0864e0a2af3dfba8948ae993179daf1f512bc0a943b`） |
| confidence / authority | `observed` / `shipped-artifact` |

```c

/* protected: virtual void __cdecl HWKCalc_GlassArea::Serialize(class CbArchive & __ptr64) __ptr64
    */

void __thiscall HWKCalc_GlassArea::Serialize(HWKCalc_GlassArea *this,CbArchive *param_1)

{
                    /* 0x89be0  24404  ?Serialize@HWKCalc_GlassArea@@MEAAXAEAVCbArchive@@@Z
                       0x89be0  24406  ?Serialize@HWKCalc_GlassDisp@@MEAAXAEAVCbArchive@@@Z
                       0x89be0  24431  ?Serialize@HWKCalc_GlassStrength@@MEAAXAEAVCbArchive@@@Z
                       0x89be0  24432  ?Serialize@HWKCalc_GlassWeight@@MEAAXAEAVCbArchive@@@Z */
  HWKCalc_GlassBase::Serialize((HWKCalc_GlassBase *)this,param_1);
                    /* WARNING: Could not recover jumptable at 0x000180089bf6. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  CbArchive::IsStoring(param_1);
  return;
}
```

反编译自带限制（原文摘录）：

- The session serves operations only after Ghidra reports default auto-analysis complete; incomplete analysis does not expose partial results.
- The imported Program and temporary project are ephemeral and deleted on close. Annotation operations edit session database metadata; original executable bytes are never written.
- Cancelling an active Ghidra request terminates its ephemeral database and discards session annotations. The selected target remains open; the next provider query imports the original artifact again.
- Default-space addresses use lowercase 0x-prefixed hexadecimal; other address spaces use <percent-encoded-space>:0x<hex>.
- Pseudocode is Ghidra decompiler output, not original source and not text-equivalent to Hopper output.
- External functions and functions without an analyzable body return null; other decompiler failures remain explicit.
- macOS sessions require a matching executable Ghidra native decompiler; REA checks for it but does not build native components or change Gatekeeper quarantine state.

### 4.2 机器码直译（objdump 反汇编，用于核对常量与引用）

```asm
; ?Serialize@HWKCalc_GlassDisp@@MEAAXAEAVCbArchive@@@Z @ 0x89be0
180089be0: 40 53                          pushq %rbx
180089be2: 48 83 ec 20                    subq $0x20, %rsp
180089be6: 48 8b da                       movq %rdx, %rbx
180089be9: e8 92 03 00 00                 callq 0x180089f80 <?Serialize@HWKCalc_GlassBase@@MEAAXAEAVCbArchive@@@Z>
180089bee: 48 8b cb                       movq %rbx, %rcx
180089bf1: 48 83 c4 20                    addq $0x20, %rsp
180089bf5: 5b                             popq %rbx
180089bf6: 48 ff 25 bb 54 2c 00           jmpq *0x2c54bb(%rip)         # 0x18034f0b8
```
