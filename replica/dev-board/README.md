# HWK 开发看板

工程辅助看板，读取当前仓库的开发调度与验收状态；不实现HWK产品功能。

本机：http://127.0.0.1:18743

前端：React + TypeScript + Vite + oxlint。

```sh
npm ci
npm test
npm run build
npm run lint
```

服务位于 `scripts/scheduler/dashboard.py`，由 `board_service.py` 管理。每3秒轮询只读快照；打开详情可查看会话与证据。界面以台账展示业务状态，不从执行轮次数量推导产品完成比例。
