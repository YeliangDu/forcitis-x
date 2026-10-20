# 安装包全量清点（静态，不含运行）

- 顶层目录：`vendor/64位网络版V5.4.25.1220`
- MSI File 表条目：458；合计 506.6 MB
- 其中 PE 二进制：139；非 PE：319

## 1. 顶层安装产物（现场哈希）

| 名称 | 文件数 | 大小 | SHA-256 |
| --- | --- | --- | --- |
| `SqlLocalDB2012_x64_WithNCLI/` | 2 | 40.0 MB | `（目录）` |
| `XWALL.CAB` | 1 | 142.5 MB | `1085e1802d686962ebb349090d6a777586e883377bab1f82f9e828f5d14629d1` |
| `XWallClientX64.msi` | 1 | 1.8 MB | `d4af9e739f623c2332d0d184bfda4f6bb2f10cbeece951c90b009e35fee4ce35` |
| `setup.exe` | 1 | 0.6 MB | `c1baacf52ce73ca36c9b94af95922890355feb98e2c0795edc71fd27aa811e28` |
| `vcredist_x64/` | 1 | 14.6 MB | `（目录）` |
| `vcredist_x86/` | 1 | 14.0 MB | `（目录）` |
| `快捷卸载HWK(X64).exe` | 1 | 0.1 MB | `b1085b03818772853ac15ae1714955db3e411949884da93033c9a9e48e3c0dac` |
| `网络版安装方法.rtf` | 1 | 5.1 MB | `f31e0b85f6ecbb9845e9b51e86c15aa286aae0b84045f8247ad575d9af979f41` |
| `豪沃克修复工具.exe` | 1 | 0.2 MB | `99a8fcaf77f874396ced519192e14a0d815d71af72001f459a785ea11853924a` |

## 2. 安装布局（MSI 目标路径，按目录聚合）

| 目标目录 | 文件数 | 大小 |
| --- | --- | --- |
| `LocalAppDataFolder/HWKSoft/XWall` | 8 | 218.3 MB |
| `XWallClient` | 83 | 112.9 MB |
| `XWallClient/X64` | 40 | 80.5 MB |
| `XWallClient/示例` | 56 | 41.1 MB |
| `XWallClient/X86` | 29 | 35.0 MB |
| `XWallClient/XWallCommonFiles` | 4 | 12.6 MB |
| `XWallClient/Support` | 118 | 2.5 MB |
| `LocalAppDataFolder/HWKSoft/XWindow` | 1 | 1.7 MB |
| `XWallClient/字体` | 2 | 1.1 MB |
| `XWallClient/SchemaData` | 74 | 0.4 MB |
| `LocalAppDataFolder/HWKSoft/XWall/X86` | 1 | 0.1 MB |
| `XWallClient/XWallCommonFiles/X86` | 1 | 0.1 MB |
| `XWallClient/XWallCommonFiles/X64` | 1 | 0.1 MB |
| `LocalAppDataFolder/HWKSoft/XWall/X64` | 1 | 0.1 MB |
| `XWallClient/Custom` | 7 | 0.1 MB |
| `LocalAppDataFolder/HWKSoft/XWindow/X86` | 1 | 0.0 MB |
| `XWallClient/XWindowCommonFiles/X86` | 1 | 0.0 MB |
| `XWallClient/XWindowCommonFiles/X64` | 1 | 0.0 MB |
| `LocalAppDataFolder/HWKSoft/XWindow/X64` | 1 | 0.0 MB |
| `XWallClient/Template` | 26 | 0.0 MB |
| `LocalAppDataFolder/HWKSoft/XWall/ProjectTemplate` | 1 | 0.0 MB |
| `XWallClient/ProjectTemplate` | 1 | 0.0 MB |

## 3. 扩展名分布

| 扩展名 | 数量 | 合计大小 |
| --- | --- | --- |
| `.xdf` | 106 | 0.5 MB |
| `.xml` | 82 | 0.5 MB |
| `.dll` | 75 | 71.2 MB |
| `.txt` | 41 | 0.2 MB |
| `.doc` | 22 | 26.8 MB |
| `.arx` | 16 | 44.1 MB |
| `.cwx` | 15 | 11.0 MB |
| `.exe` | 15 | 16.2 MB |
| `.zrx` | 13 | 32.7 MB |
| `.grx` | 11 | 34.5 MB |
| `.xda` | 9 | 1.6 MB |
| `.rtf` | 9 | 0.7 MB |
| `.ini` | 8 | 0.1 MB |
| `.mdf` | 4 | 200.2 MB |
| `.ldf` | 4 | 30.6 MB |
| `.dwg` | 4 | 3.3 MB |
| `.mnr` | 4 | 0.5 MB |
| `.dat` | 2 | 0.0 MB |
| `.lib` | 2 | 2.0 MB |
| `.cuix` | 2 | 0.1 MB |
| `.cui` | 2 | 1.5 MB |
| `.chm` | 2 | 13.1 MB |
| `.cwt` | 2 | 0.0 MB |
| `.shx` | 2 | 1.1 MB |
| `.pdf` | 2 | 13.6 MB |
| `.xdb` | 1 | 0.1 MB |
| `.xfe` | 1 | 0.0 MB |
| `.xdl` | 1 | 0.4 MB |
| `.chi` | 1 | 0.0 MB |

## 4. PE 二进制（139 个）

| 安装名 | 大小 | 导出数 | 自报 DLL 名 | 产品名 |
| --- | --- | --- | --- | --- |
| `XWall.exe` | 11448320 | 32 | `XWall.exe` | 豪沃克幕墙工程软件 |
| `HWKKernal.dll` | 7548416 | 32314 | `HWKKernal.dll` | — |
| `structmodule.dll` | 7232000 | 8205 | `Structmodule.dll` | — |
| `HWKWallUtil.dll` | 5715968 | 748 | `HWKWallUtil.dll` | — |
| `XGeomAlgo.dll` | 4654592 | 7534 | `XGeomAlgo.dll` | — |
| `XGeomBase.dll` | 4336640 | 4996 | `XGeomBase.dll` | — |
| `HWUtil21.grx` | 4035072 | 819 | `HWUtil21.grx` | Util Application |
| `HWUtil20.grx` | 4006400 | 803 | `HWUtil20.grx` | Util Application |
| `HWUtil22.grx` | 3976192 | 819 | `HWUtil22.grx` | Util Application |
| `XBool.dll` | 3893248 | 5905 | `XBool.dll` | — |
| `XBO.dll` | 3856384 | 6418 | `XBO.dll` | — |
| `HWUtil2026.zrx` | 3795968 | 818 | `HWUtil2019.ZRX` | Util Application |
| `HWUtil2025.zrx` | 3793920 | 818 | `HWUtil2019.ZRX` | Util Application |
| `HWUtil2021.zrx` | 3787264 | 868 | `HWUtil2019.ZRX` | Util Application |
| `HWUtil2024.zrx` | 3787264 | 868 | `HWUtil2019.ZRX` | Util Application |
| `HWUtil24.grx` | 3787264 | 818 | `HWUtil24.grx` | Util Application |
| `HWUtil2023.zrx` | 3787264 | 868 | `HWUtil2019.ZRX` | Util Application |
| `HWUtil23.grx` | 3785728 | 818 | `HWUtil23.grx` | Util Application |
| `HWUtil23.arx` | 3785216 | 814 | `HWUtil.dll` | Util Application |
| `HWUtil25.grx` | 3780608 | 818 | `HWUtil25.grx` | Util Application |
| `HWUtil21.arx` | 3738624 | 814 | `HWUtil.dll` | Util Application |
| `HWUtil22.arx` | 3737088 | 814 | `HWUtil.dll` | Util Application |
| `HWUtil18.arx` | 3691008 | 818 | `HWUtil.dll` | Util Application |
| `HWUtil25.arx` | 3536896 | 814 | `HWUtil.dll` | Util Application |
| `HWUtil24.arx` | 3515904 | 814 | `HWUtil.dll` | Util Application |
| `XV3d.dll` | 3435008 | 10658 | `XV3d.dll` | — |
| `HWUtil20.grx` | 3229184 | — | `—` | Util Application |
| `HWUtil23.arx` | 3132928 | — | `—` | Util Application |
| `HWUtil22.arx` | 3098624 | — | `—` | Util Application |
| `HWUtil21.arx` | 3089920 | — | `—` | Util Application |
| `HWUtil18.arx` | 2828288 | — | `—` | Util Application |
| `XTopAlgo.dll` | 2793984 | 4513 | `XTopAlgo.dll` | — |
| `HWUtil19.grx` | 2788864 | 803 | `HWUtil19.grx` | Util Application |
| `HWUtil18.grx` | 2565120 | 803 | `HWUtil18.grx` | Util Application |
| `HWUtil19.arx` | 2554880 | 818 | `HWUtil.dll` | Util Application |
| `HWKGUI.dll` | 2529792 | 6793 | `HWKGUI.dll` | HWKControlBar Professional Dynamic Link Library |
| `HWUtil2019.zrx` | 2529280 | 818 | `HWUtil2019.ZRX` | Util Application |
| `HWUtil2020.Zrx` | 2529280 | 818 | `HWUtil2019.ZRX` | Util Application |
| `HWUtil20.arx` | 2493952 | 818 | `HWUtil.dll` | Util Application |
| `HWKGraphModelLib.dll` | 2296320 | 6345 | `HWKGraphModelLib.dll` | — |
| `XFillet.dll` | 2221056 | 2743 | `XFillet.dll` | — |
| `HWUtil19.grx` | 2205696 | — | `—` | Util Application |
| `HWUtil17.arx` | 2199552 | — | `—` | Util Application |
| `XWindow.exe` | 2158592 | 0 | `—` | 门窗设计软件 |
| `HWUtil20.arx` | 2137600 | — | `—` | Util Application |
| `HWUtil19.arx` | 2125312 | — | `—` | Util Application |
| `HWUtil2020.ZRX` | 2080256 | — | `—` | Util Application |
| `HWUtil2019.zrx` | 2080256 | — | `—` | Util Application |
| `HWUtil18.grx` | 2048000 | — | `—` | Util Application |
| `NGLib.dll` | 1894400 | 517 | `NGLib.dll` | — |
| `XMath.dll` | 1884672 | 4327 | `XMath.dll` | — |
| `HWUtil2018.zrx` | 1773568 | 78 | `HWUtil19.ZRX` | Util Application |
| `XGeom.dll` | 1558016 | 5973 | `XGeom.dll` | — |
| `HWKPlot.dll` | 1531392 | 2029 | `HWKPlot.dll` | — |
| `HWUtil2018.zrx` | 1470464 | — | `—` | Util Application |
| `XOffset.dll` | 1460224 | 954 | `XOffset.dll` | — |
| `HWUtil2015.zrx` | 1433600 | — | `—` | Util Application |
| `HWUtil2012.zrx` | 1415680 | — | `—` | Util Application |
| `XStrCal.exe` | 1232384 | 0 | `—` | 幕墙工程计算软件 |
| `XOpenGl.dll` | 1170944 | 2119 | `XOpenGl.dll` | — |
| `HWKModelClass.dll` | 1062400 | 2260 | `HWKModelClass.dll` | — |
| `HWKFeUtil.dll` | 982528 | 1873 | `HWKFeUtil.dll` | — |
| `XService.dll` | 952832 | 1370 | `XService.dll` | — |
| `XHLR.dll` | 887296 | 2364 | `XHLR.dll` | — |
| `XBrep.dll` | 833536 | 2551 | `XBrep.dll` | — |
| `adap_archstrength.xda` | 730112 | 91 | `adap_archstrength.dll` | TODO: <产品名> |
| `XFoundation.dll` | 702464 | 3297 | `XFoundation.dll` | — |
| `freetype.dll` | 687104 | 216 | `freetype.dll` | FreeType |
| `CHAI3D.dll` | 618496 | 1066 | `CHAI3D.dll` | — |
| `HWKCAD.dll` | 539136 | 1856 | `HWKCAD.dll` | — |
| `HWUtil17.arx` | 530944 | 801 | `HWUtil17.arx` | Util Application |
| `HWKThermUtil.exe` | 527360 | 0 | `—` | 热工信息文件修改工具 |
| `图库迁移工具.exe` | 434688 | 0 | `—` | 豪沃克图库迁移助手 |
| `HWKUtil.dll` | 434176 | 1224 | `HWKUtil.dll` | — |
| `HWKSciCal.dll` | 415232 | 605 | `HWKSciCal.dll` | — |
| `adap_plainpole.xda` | 394752 | 19 | `adap_plainpole.dll` | TODO: <产品名> |
| `HWKShSolve.dll` | 386560 | 141 | `HWKShSolve.dll` | — |
| `WallUtilPlug1.xdl` | 374272 | 1 | `WallUtilPlug1.xdl` | — |
| `SparseSolve.dll` | 369152 | 274 | `SparseSolve.dll` | — |
| `HWKOptim.dll` | 365568 | 866 | `HWKOptim.dll` | — |
| `HWKThermData.dll` | 356352 | 1012 | `HWKThermData.dll` | — |
| `HWKIOUtil.dll` | 333824 | 89 | `HWKIOUtil.dll` | — |
| `XGridCtrl.dll` | 326144 | 1045 | `XGridCtrl.dll` | TODO: <产品名> |
| `XPrim.dll` | 305664 | 653 | `XPrim.dll` | — |
| `HWKAutoUpdate.exe` | 290304 | 0 | `—` | TODO: <产品名> |
| `glut64.dll` | 272896 | 119 | `glut64.dll` | — |
| `HWKArchPoleInfo.dll` | 194560 | 741 | `HWKArchPoleInfo.dll` | — |
| `adap_boardfe.xda` | 193024 | 19 | `adap_boardfe.dll` | TODO: <产品名> |
| `HWKCADBag.exe` | 186880 | 0 | `—` | HWKCADBag 应用程序 |
| `豪沃克修复工具.exe` | 186368 | 0 | `—` | TODO: <产品名> |
| `HWKUtilRibbon22.dll` | 160256 | — | `—` | HWKUtilRibbon |
| `HWKUtilRibbon22.dll` | 160256 | — | `—` | HWKUtilRibbon |
| `HWKUtilRibbon23.dll` | 160256 | — | `—` | HWKUtilRibbon |
| `HWKUtilRibbon23.dll` | 160256 | — | `—` | HWKUtilRibbon |
| `HWKUtilRibbon24.dll` | 158208 | 0 | `—` | HWKUtilRibbon |
| `HWKShellInfo.dll` | 158208 | 622 | `HWKShellInfo.dll` | — |
| `hwkcalc.exe` | 143872 | — | `—` | — |
| `HWKUtilRibbon20.dll` | 137216 | — | `—` | HWKUtilRibbon |
| `HWKUtilRibbon19.dll` | 137216 | — | `—` | HWKUtilRibbon |
| `HWKUtilRibbon21.dll` | 137216 | — | `—` | HWKUtilRibbon |
| `HWKUtilRibbon20.dll` | 137216 | — | `—` | HWKUtilRibbon |
| `HWKUtilRibbon19.dll` | 137216 | — | `—` | HWKUtilRibbon |
| `HWKUtilRibbon18.dll` | 137216 | — | `—` | HWKUtilRibbon |
| `HWKUtilRibbon18.dll` | 137216 | — | `—` | HWKUtilRibbon |
| `HWKUtilRibbon21.dll` | 137216 | — | `—` | HWKUtilRibbon |
| `SPARSE.dll` | 131584 | 30 | `SPARSE.dll` | — |
| `豪沃克网络版客户端配置工具.exe` | 129536 | 0 | `—` | TODO: <产品名> |
| `libexpatw.dll` | 126464 | 65 | `libexpatw.dll` | — |
| `HWKGI.dll` | 117248 | 260 | `HWKGI.dll` | TODO: <产品名> |
| `ResizableLib.dll` | 103424 | 254 | `ResizableLib.dll` | TODO: <产品名> |
| `HWKXmlReader.dll` | 102400 | 326 | `HWKXmlReader.dll` | — |
| `豪沃克网络版服务端配置工具.exe` | 102400 | 0 | `—` | TODO: <产品名> |
| `HWKShData.dll` | 93184 | 350 | `HWKShData.dll` | — |
| `XRegDll.dll` | 77824 | — | `—` | — |
| `adap_archload.xda` | 74240 | 55 | `adap_archload.dll` | TODO: <产品名> |
| `msiexec.exe` | 73216 | — | `—` | Windows Installer - Unicode |
| `XRegDll.dll` | 72704 | 2 | `XRegDll.dll` | — |
| `HWKInfoAdap.dll` | 65536 | 118 | `HWKInfoAdap.dll` | HWKInfoAdap.dll |
| `adap_antinoise.xda` | 62464 | 19 | `adap_antinoise.dll` | TODO: <产品名> |
| `adap_holdblock.xda` | 59392 | 20 | `adap_holdblock.dll` | TODO: <产品名> |
| `Pthread.dll` | 57856 | 141 | `Pthread.dll` | — |
| `hwk.dll` | 57344 | — | `—` | — |
| `HWK.dll` | 57344 | — | `—` | — |
| `HWK.dll` | 54784 | 0 | `—` | — |
| `hwk.dll` | 54784 | 0 | `—` | — |
| `adap_midglassglue.xda` | 52224 | 19 | `adap_midglassglue.dll` | TODO: <产品名> |
| `xwindow.dll` | 45568 | — | `—` | — |
| `XWindow.dll` | 45568 | — | `—` | — |
| `XWindow.dll` | 44032 | 0 | `—` | — |
| `xwindow.dll` | 44032 | 0 | `—` | — |
| `adap_watertight.xda` | 39936 | 19 | `adap_watertight.dll` | TODO: <产品名> |
| `adap_regap.xda` | 34304 | 19 | `adap_regap.dll` | TODO: <产品名> |
| `HWKSoft.dll` | 14336 | — | `—` | — |
| `HWKSoft.dll` | 14336 | — | `—` | — |
| `HWKSoft2007.dll` | 14336 | — | `—` | — |
| `HWKSoft2007.dll` | 14336 | — | `—` | — |
| `HWKStartLocalDBInstance.exe` | 12800 | 0 | `—` | — |
| `HWKStartLocalDBInstance.exe` | 12800 | 0 | `—` | — |
| `HWKStartLocalDBInstance.exe` | 12800 | 0 | `—` | — |

## 5. 非 PE 数据/资源文件（152 个，按扩展名）

| 扩展名 | 数量 | 示例 |
| --- | --- | --- |
| `.xdf` | 106 | `gbeam.xdf` |
| `.cwx` | 15 | `异型索网幕墙.cwx` |
| `.mdf` | 4 | `XWallTem.mdf` |
| `.ldf` | 4 | `XWallTem_log.ldf` |
| `.dwg` | 4 | `热工节点例子.dwg` |
| `.mnr` | 4 | `HWKSoft2007.mnr` |
| `.dat` | 2 | `lexi_expr.dat` |
| `.lib` | 2 | `xwindow.lib` |
| `.cuix` | 2 | `HWKSoft.cuix` |
| `.cui` | 2 | `HWKSoft2007.cui` |
| `.cwt` | 2 | `空白工程.cwt` |
| `.shx` | 2 | `hwkchn.shx` |
| `.xdb` | 1 | `hwkutildata.xdb` |
| `.xfe` | 1 | `桁架计算.xfe` |
| `.chi` | 1 | `xwall.chi` |

## 6. 口径与未验项

- 成员名在 CAB 内是 `_<32位十六进制>`，真实名只能由 MSI `File` 表的 `FileName` 得到；本表用 `symbolic_target` 作为安装落点，未经安装验证。
- 大小与 sha256 来自既有取证产物 `file-map.json` / `file-inventory.json`，本轮未重新解包。
- 目录聚合是字符串聚合，不代表 MSI 实际目录层级（Feature/Component 结构未展开）。
- 未做：DLL 依赖闭合、注册表写入、服务/COM 注册、字体与运行库安装顺序、卸载清理。
