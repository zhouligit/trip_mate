# 好友与群组邀请（接口说明）

Base：`/api` 与 `/api/v1` 均可。

## 好友

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/friends/add` | 添加好友（点心），body：`{ "target_user_id": 123 }`，幂等 |
| GET | `/friends` | 当前用户的好友列表 |
| DELETE | `/friends/{friend_user_id}` | 移除好友 |

推荐列表 `/match/recommendations` 会排除已是好友的用户。

## 群组邀请

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/groups` | 创建群；响应含 `invite_code`（新建库迁移后生效） |
| GET | `/groups/{group_id}/invite` | **群主**获取邀请码与小程序路径占位 `invite_path` |
| POST | `/groups/join-by-invite` | body：`{ "invite_code": "xxx" }`，加入群组（规则同 `/groups/{id}/join`） |

小程序侧：落地页读取 `code` 查询参数，调用 `join-by-invite`。

数据库迁移：`alembic upgrade head`（ revision `20260415_0003`）。
