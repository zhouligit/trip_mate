
主链第一批“可用实现”已经执行完成了，现在不是占位接口了，已经接了真实 MySQL 读写和 JWT 鉴权（微信/支付先用 mock 适配层）。

你现在得到的能力：

auth：/auth/wechat/login 可创建/登录用户并返回 token
users：人格测试、定位更新入库（user_profiles）
groups：建群、入群、群主发起投票（自动生成3条路线）
votes：投票、查看投票结果（统计 winner）
orders：下单、查单、申请退款（基础规则）
payments：支付回调更新 payments + orders 状态
discovery：查询招募中群组列表
本次新增/改动重点文件
核心能力
app/models.py
app/core/deps.py
app/core/security.py
app/core/database.py
app/main.py
schema
app/schemas/auth.py
app/schemas/users.py
app/schemas/groups.py
app/schemas/votes.py
app/schemas/orders.py
业务接口
app/api/v1/endpoints/auth.py
app/api/v1/endpoints/users.py
app/api/v1/endpoints/discovery.py
app/api/v1/endpoints/groups.py
app/api/v1/endpoints/voi/v1/votes/{vote_id}/cast
POST /api/v1/orders/pay
POST /api/v1/payments/wechat/notify（mock 支付回调）
GET /api/v1/orders
说明（当前阶段刻意简化）
微信 code2session 还没接真实微信服务（目前 mock_{code}）
微信支付验签/幂等 Redis 锁还没加（当前为最小可跑通）
退款审核流、拼团倒计时任务、自动踢未支付、车票核销落库等是下一批
如果你同意，我下一步直接继续第 5 步：
把“支付回调幂等 + Redis 锁 + 拼团/支付超时 Celery 任务”补上，主链就更接近可上测试环境。
