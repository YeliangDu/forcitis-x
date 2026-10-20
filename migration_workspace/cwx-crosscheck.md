# `.cwx` 跨源一致性验证（离线）

- 生成器：`scripts/cwx-crosscheck.py`；类表 4979 个；体系清单 74 个
- C1 类型 ⊆ 二进制类表；C2 `HWKSchema_*` ⊆ 74 体系清单；C3 每个工程必须声明体系

| 工程 | 大小 | 类型数 | 体系 | C1 | C2 | C3 | 判定 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `异型索网幕墙.cwx` | 0.02 MB | 45 | HWKSchema_UnregLinkNet | PASS | PASS | PASS | PASS |
| `玻璃组合优化.cwx` | 0.13 MB | 0 | — | PASS | PASS | N/A | N/A(无 CbArchive 类型) |
| `线材优化例子.cwx` | 0.09 MB | 0 | — | PASS | PASS | N/A | N/A(无 CbArchive 类型) |
| `铝板优化.cwx` | 0.09 MB | 0 | — | PASS | PASS | N/A | N/A(无 CbArchive 类型) |
| `左右面板不同热工.cwx` | 0.67 MB | 22 | HWKSchema_ThermEx | PASS | PASS | PASS | PASS |
| `热工计算例子.cwx` | 1.02 MB | 31 | HWKSchema_TTherm | PASS | PASS | PASS | PASS |
| `线材组合优化例子.cwx` | 0.09 MB | 0 | — | PASS | PASS | N/A | N/A(无 CbArchive 类型) |
| `石材幕墙示例1.cwx` | 0.01 MB | 75 | HWKSchema_StoneBoard | PASS | PASS | PASS | PASS |
| `线材优化示例1.cwx` | 0.09 MB | 0 | — | PASS | PASS | N/A | N/A(无 CbArchive 类型) |
| `各种栏杆样例.cwx` | 6.98 MB | 59 | HWKSchema_Railings | PASS | PASS | PASS | PASS |
| `连续梁立柱计算示例.cwx` | 0.02 MB | 81 | HWKSchema_MKMQ | PASS | PASS | PASS | PASS |
| `栏杆教程.cwx` | 1.48 MB | 59 | HWKSchema_Railings | PASS | PASS | PASS | PASS |
| `索桁架结构.cwx` | 0.01 MB | 45 | HWKSchema_LinkTruss | PASS | PASS | PASS | PASS |
| `玻璃优化示例.cwx` | 0.08 MB | 0 | — | PASS | PASS | N/A | N/A(无 CbArchive 类型) |
| `门窗计算示例1.cwx` | 0.23 MB | 79 | HWKSchema_NormalMC | PASS | PASS | PASS | PASS |

## 汇总

- PASS：9
- N/A（无 CbArchive 类型，属另一套序列化）：6 — `玻璃组合优化.cwx`, `线材优化例子.cwx`, `铝板优化.cwx`, `线材组合优化例子.cwx`, `线材优化示例1.cwx`, `玻璃优化示例.cwx`
- FAIL：0

## 限制

- 只做"名字集合"比对，不验证字段布局与数值。
- 类型抽取依赖 UTF-16 正则；类型名被拆写或加密时会漏检。
