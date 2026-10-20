# 截面库（Section Library）规格

**定位（用户 2026-10-21 决定）**：不照搬旧系统的 BREP 存储；改为**批量导入截面图纸（DWG/DXF）→ 自动计算参数 → 入库 → 计算时按引用调用**。
新设计截面由设计师导入设计图，计算参数后参与计算。

## 1. 流水线

```text
图纸(DWG/DXF) → 实体抽取 → 段/弧 → 端点在容差内吸附 → 闭合环 → 外环/内环(孔)分类
              → 参数计算 → 校验 → 审核 → 入库(不可变版本) → 计算模型按引用取用
```

| 阶段 | 规则 | 失败处理 |
| --- | --- | --- |
| 输入格式 | **用户直接上传 DWG**（DXF 也支持）；DWG 由服务端转换，用户端无需任何操作 | 转换器缺失/失败 → 明确报错，不静默 |
| 转换器 | `dwg2dxf`（LibreDWG，GPL-3，本地已验证）或商业 ODA SDK；转换器名称+版本写入 `source` | 自制对象（HWK 自定义实体）转换不出几何 → 单独报"无可转换实体" |
| 单位 | 取 `$INSUNITS`；缺省按 mm；不猜 | 单位缺失 → 警告并要求人工确认 |
| 实体 | `LINE` / `ARC` / `LWPOLYLINE`(bulge) / `POLYLINE` / `CIRCLE`；`INSERT` 递归展开 ≤4 层 | 不支持的实体 → 报清单，不静默丢弃 |
| 环 | 端点吸附 0.02 mm；每个段只用一次；只保留闭合环 | 未闭合 → 报告缺口位置，拒绝入库 |
| 孔 | 由"包含关系 + 面积大小"判定，不依赖方向 | 嵌套异常（互相包含）→ 报告并要求人工判定 |
| 参数 | 面积/重心/Ix/Iy/Ixy/主轴/W/回转半径/周长/包围盒/静矩 | 与解析解或旧值偏差超容差 → 拒绝入库 |
| 校验 | ①解析解自检 ②与旧系统 `型材参数表` 对照（可获取时）≤0.5% ③几何自洽（闭合、无自交、面积>0） | 任一不过 → 待人工复核 |

## 2. 数据模型

```text
SectionAsset {
  id, name, tags[], materialRef?,
  source: { file, format: dwg|dxf, sha256, importedAt, parserVersion },
  geometry: { units, entities, rings[] },        // 不可变
  properties: { areaMm2, cxMm, cyMm, ixMm4, iyMm4, ixyMm4, i1Mm4, i2Mm4,
                wxTopMm3, wxBottomMm3, wyLeftMm3, wyRightMm3, perimeterMm, bboxMm,
                staticMoment?[], torsionJ? },
  validation: { analyticOk, oldSystemDelta?[], reviewer, reviewedAt },
  status: draft | approved | deprecated,
  version, supersedes?
}
```

引用规则：计算模型只存 `sectionAssetId + version`（不内联几何），结果里记录该版本，保证可复现。

## 3. 与旧系统的关系

| 项 | 处理 |
| --- | --- |
| 旧 `型材参数表`/`图库数据表` | **只读对照来源**，不再作为新系统存储格式 |
| 旧 BREP 编码 | **不再需要**（已解的 line/arc 编码仅作为历史证据保留） |
| 旧 `JA/CJ/TCX`（扭转/扇性） | 新系统单独实现并**用旧列锚定**后才可入库；未验证前 `torsionJ` 为空 |
| 旧 DWG 列 | 可作为"历史截面图纸"批量导入的一次性来源（bzip2+AC1024，需先解压） |

## 4. 批量导入

- 输入：目录或清单（DWG/DXF），输出：`SectionAsset[]` + 导入报告（成功/待复核/失败原因）。
- 幂等：以 `几何哈希(geometry rings)` 去重；同几何不同名字 → 合并为别名。
- 批处理失败不阻塞其它文件；每份图纸有独立结果行。

## 5. 验收（对应 MVP）

| 项 | 判据 |
| --- | --- |
| 解析覆盖 | 常见 5 类实体 + 块引用全覆盖；不支持的实体必须报错而非静默 |
| 数值正确 | 解析解自检 ≤1e-9；可获取旧值时 ≤0.5% |
| 幂等与去重 | 同一图纸导入两次 → 同一 `SectionAsset` |
| 可追溯 | 每份参数可回溯到源文件哈希 + 解析器版本 + 审核人 |
| 不可变 | 已批准版本不可改；修改产生新版本 |
