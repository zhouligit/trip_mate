# TripMate 全量 API 文档（当前实现）

本文档基于当前代码实现整理，覆盖 `app/api/v1/endpoints` 下所有接口。

## 通用约定

- Base URL 同时支持：
  - `/api`
  - `/api/v1/wm`
- 鉴权：除登录、支付回调、健康检查、DNA题库外，均需
  - `Authorization: Bearer <token>`
- 当前响应格式：**直接返回 JSON 对象**（暂未统一包裹 `code/message/data`）

---

## 1. 健康检查

### `GET /api/v1/wm/health`

### 请求参数

无

### 请求示例

```http
GET /api/v1/wm/health HTTP/1.1
Host: www.wang-hao-hao.cn
```

### 响应示例

```json
{
  "status": "ok"
}
```

---

## 2. 用户与认证

## 2.1 微信登录

### `POST /api/v1/wm/auth/wechat/login`

### 请求参数

| 参数 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| code | body | string | 是 | 微信登录 code（当前用于 mock openid） |
| nickname | body | string | 否 | 用户昵称 |
| avatar_url | body | string | 否 | 头像 URL |

### 请求参数示例（JSON）

```json
{
  "code": "demo_001",
  "nickname": "tester",
  "avatar_url": "https://example.com/avatar.png"
}
```

### 请求示例

```http
POST /api/v1/wm/auth/wechat/login HTTP/1.1
Host: www.wang-hao-hao.cn
Content-Type: application/json
```

### 响应字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| access_token | string | 访问令牌 |
| token | string | 与 `access_token` 相同（前端兼容） |
| token_type | string | 固定 `bearer` |
| user_id | number | 用户 ID |
| userId | number | 用户 ID（前端兼容） |
| profile_completed | boolean | 是否已完成画像 |
| isNewUser | boolean | 是否新用户 |

### 响应示例

```json
{
  "access_token": "xxx",
  "token": "xxx",
  "token_type": "bearer",
  "user_id": 1,
  "userId": 1,
  "profile_completed": false,
  "isNewUser": true
}
```

---

## 2.2 退出登录

### `POST /api/v1/wm/auth/logout`

### 请求参数

无

### 请求示例

```http
POST /api/v1/wm/auth/logout HTTP/1.1
Host: www.wang-hao-hao.cn
Authorization: Bearer <token>
```

### 响应示例

```json
{
  "message": "ok"
}
```

---

## 2.3 获取当前用户信息

### `GET /api/v1/wm/users/me`

### 响应字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| userId | number | 用户 ID |
| nickname | string | 昵称 |
| avatar_url | string/null | 头像 |
| mobile | string/null | 手机号 |
| realname_verified | boolean | 是否实名 |
| profile_completed | boolean | 是否完成画像 |

### 响应示例

```json
{
  "userId": 1,
  "nickname": "tester",
  "avatar_url": null,
  "mobile": "13800000000",
  "realname_verified": false,
  "profile_completed": true
}
```

---

## 2.4 更新当前用户信息

### `PUT /api/v1/wm/users/me`

### 请求参数

| 参数 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| nickname | body | string | 否 | 昵称 |
| avatar_url | body | string | 否 | 头像 URL |
| mobile | body | string | 否 | 手机号 |

### 请求参数示例（JSON）

```json
{
  "mobile": "13800000000"
}
```

### 响应示例

```json
{
  "userId": 1,
  "nickname": "tester",
  "avatar_url": null,
  "mobile": "13800000000"
}
```

---

## 2.5 更新定位

### `POST /api/v1/wm/users/location`

### 请求参数

| 参数 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| city_code | body | string | 是 | 城市编码 |
| district_code | body | string | 否 | 区县编码 |

### 请求参数示例（JSON）

```json
{
  "city_code": "chengdu",
  "district_code": "jinjiang"
}
```

### 响应示例

```json
{
  "city_code": "chengdu",
  "district_code": "jinjiang"
}
```

---

## 3. DNA 测试

## 3.1 获取题库

### `GET /api/v1/wm/dna/questions`

### 请求参数

无

### 响应字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| items | array | 题目列表 |

### 响应示例

```json
{
  "items": [
    {
      "question_id": 1,
      "title": "旅行节奏",
      "options": [
        { "option_id": 1, "label": "早鸟型" },
        { "option_id": 2, "label": "睡到自然醒" }
      ]
    }
  ]
}
```

---

## 3.2 提交 DNA（推荐路径）

### `POST /api/v1/wm/dna/submissions`

### 请求参数

| 参数 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| answers | body | array | 是 | 答题数组，5-8题 |

`answers[]`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| question_id | number | 是 | 题目 ID |
| option_id | number | 是 | 选项 ID |

### 请求参数示例（JSON）

```json
{
  "answers": [
    { "question_id": 1, "option_id": 1 },
    { "question_id": 2, "option_id": 2 },
    { "question_id": 3, "option_id": 1 },
    { "question_id": 4, "option_id": 2 },
    { "question_id": 5, "option_id": 1 }
  ]
}
```

### 响应字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| dnaType | string | 拼接的 DNA 类型 |
| tags | array | 标签列表 |
| preferences | object | 推荐偏好 |

### 响应示例

```json
{
  "dnaType": "q1_o1+q2_o2+q3_o1",
  "tags": ["q1_o1", "q2_o2", "q3_o1", "q4_o2", "q5_o1"],
  "preferences": {
    "pace": "q1_o1"
  }
}
```

---

## 3.3 获取最近一次 DNA

### `GET /api/v1/wm/dna/me/latest`

### 响应示例

```json
{
  "user_id": 1,
  "tags": ["q1_o1", "q2_o2", "q3_o1"],
  "personality_test_done": true
}
```

---

## 3.4 提交人格测试（兼容路径）

### `POST /api/v1/wm/users/personality-test`

说明：与 `POST /api/v1/wm/dna/submissions` 类似，响应为：

```json
{
  "tags": ["q1_o1", "q2_o2", "q3_o1", "q4_o2", "q5_o1"]
}
```

---

## 4. 旅伴推荐

## 4.1 获取推荐列表

### `GET /api/v1/wm/match/recommendations`

### 响应字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| items | array | 推荐列表（最多20） |

`items[]`：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| user_id | number | 用户ID |
| nickname | string | 昵称 |
| avatar_url | string/null | 头像 |
| city_code | string | 城市 |
| tags | array | 标签 |
| match_score | number | 匹配分（0-100） |

### 响应示例

```json
{
  "items": [
    {
      "user_id": 2,
      "nickname": "alice",
      "avatar_url": null,
      "city_code": "chengdu",
      "tags": ["q1_o1", "q2_o2"],
      "match_score": 80
    }
  ]
}
```

---

## 5. 群组与发现

## 5.1 发现页群组

### `GET /api/v1/wm/discovery/groups`

### 响应示例

```json
{
  "items": [
    {
      "group_id": 1,
      "name": "周末轻户外群",
      "city_code": "chengdu",
      "target_count": 30,
      "status": "recruiting"
    }
  ]
}
```

---

## 5.2 创建群组

### `POST /api/v1/wm/groups`

### 请求参数

| 参数 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| name | body | string | 是 | 群名称 |
| city_code | body | string | 是 | 城市 |
| target_count | body | number | 是 | 目标人数（30-100） |
| threshold_count | body | number | 否 | 成团门槛（30-50） |

### 响应示例

```json
{
  "group_id": 1,
  "status": "recruiting"
}
```

---

## 5.3 群详情

### `GET /api/v1/wm/groups/{group_id}`

### 响应示例

```json
{
  "group_id": 1,
  "name": "周末轻户外群",
  "owner_user_id": 1,
  "city_code": "chengdu",
  "target_count": 30,
  "threshold_count": 30,
  "member_count": 1,
  "status": "recruiting"
}
```

---

## 5.4 我的群组

### `GET /api/v1/wm/groups/my?type=created|joined`

### 响应示例

```json
{
  "items": [
    {
      "group_id": 1,
      "name": "周末轻户外群",
      "status": "recruiting",
      "target_count": 30
    }
  ]
}
```

---

## 5.5 加入群组

### `POST /api/v1/wm/groups/{group_id}/join`

### 响应示例

```json
{
  "group_id": 1,
  "joined": true
}
```

---

## 6. 投票

## 6.1 发起投票

### `POST /api/v1/wm/groups/{group_id}/vote/start`

### 请求参数

| 参数 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| duration_hours | body | number | 否 | 投票时长，12-48，默认24 |

### 响应示例

```json
{
  "vote_id": 3,
  "group_status": "voting"
}
```

---

## 6.2 发起投票（前端别名）

### `POST /api/v1/wm/groups/{group_id}/votes/sessions`

说明：等价于 `/vote/start`

---

## 6.3 当前投票会话

### `GET /api/v1/wm/groups/{group_id}/votes/sessions/current`

### 响应示例

```json
{
  "vote_id": 3,
  "status": "open",
  "start_time": "2026-04-14T12:00:00",
  "end_time": "2026-04-15T12:00:00",
  "options": [
    { "option_id": 10, "title": "古镇打卡+咖啡馆", "fee_estimate": 79.0 }
  ]
}
```

---

## 6.4 投票（group 维度）

### `POST /api/v1/wm/groups/{group_id}/votes`

### 请求参数

| 参数 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| routeId | body | number | 是 | 路线选项 ID |

### 响应示例

```json
{
  "vote_id": 3,
  "option_id": 10
}
```

---

## 6.5 投票结果（group 维度）

### `GET /api/v1/wm/groups/{group_id}/votes/result`

### 响应示例

```json
{
  "vote_id": 3,
  "winner_option_id": 10,
  "stats": [
    { "option_id": 10, "count": 1 }
  ]
}
```

---

## 6.6 投票（vote 维度）

### `POST /api/v1/wm/votes/{vote_id}/cast`

### 请求参数

| 参数 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| option_id | body | number | 是 | 选项ID |

---

## 6.7 投票结果（vote 维度）

### `GET /api/v1/wm/votes/{vote_id}/result`

响应结构同上。

---

## 7. 实名认证

## 7.1 查询实名状态

### `GET /api/v1/wm/verification/me/status`

### 响应示例

```json
{
  "userId": 1,
  "realname_verified": false,
  "status": "unverified"
}
```

---

## 7.2 微信实名（MVP mock）

### `POST /api/v1/wm/verification/wechat`

### 请求参数

| 参数 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| real_name | body | string | 是 | 真实姓名 |
| id_no_last4 | body | string | 是 | 身份证后4位 |

### 响应示例

```json
{
  "userId": 1,
  "realname_verified": true,
  "channel": "wechat"
}
```

---

## 7.3 身份证实名（MVP mock）

### `POST /api/v1/wm/verification/idcard`

### 请求参数

| 参数 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| id_number | body | string | 是 | 身份证号 |
| name | body | string | 是 | 姓名 |
| ocr_image_url | body | string | 否 | OCR 图片地址 |

---

## 8. 订单与支付

## 8.1 创建订单

### `POST /api/v1/wm/orders`

### 请求参数

| 参数 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| group_id | body | number | 是 | 群组 ID |

### 响应示例

```json
{
  "order_id": 11,
  "order_no": "TMabc123",
  "amount": 99.0,
  "status": "unpaid"
}
```

---

## 8.2 创建订单+拉起支付（兼容）

### `POST /api/v1/wm/orders/pay`

返回结构同 `POST /api/v1/wm/orders/{order_id}/pay/wechat`。

---

## 8.3 获取微信支付参数（mock）

### `POST /api/v1/wm/orders/{order_id}/pay/wechat`

### 响应示例

```json
{
  "order_id": 11,
  "order_no": "TMabc123",
  "out_trade_no": "WXabc123",
  "wechat_pay_params": {
    "timeStamp": "1710000000",
    "nonceStr": "abcd1234abcd1234",
    "package": "prepay_id=WXabc123",
    "signType": "RSA",
    "paySign": "mock_sign"
  }
}
```

---

## 8.4 订单列表

### `GET /api/v1/wm/orders`

### 响应示例

```json
{
  "items": [
    {
      "order_id": 11,
      "order_no": "TMabc123",
      "group_id": 1,
      "amount": 99.0,
      "status": "paid"
    }
  ]
}
```

---

## 8.5 订单详情

### `GET /api/v1/wm/orders/{order_id}`

### 响应示例

```json
{
  "order_id": 11,
  "order_no": "TMabc123",
  "group_id": 1,
  "amount": 99.0,
  "platform_fee": 12.0,
  "insurance_fee": 5.0,
  "status": "paid",
  "paid_at": "2026-04-14T12:30:00"
}
```

---

## 8.6 申请退款

### `POST /api/v1/wm/orders/{order_id}/refund/apply`

### 响应示例

```json
{
  "order_id": 11,
  "status": "refunding"
}
```

---

## 8.7 微信支付回调（服务端回调）

### `POST /api/v1/wm/payments/wechat/notify`

### 请求参数

| 参数 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| out_trade_no | body | string | 是 | 商户单号 |
| wechat_txn_id | body | string | 是 | 微信交易号 |
| success | body | boolean | 否 | 是否支付成功，默认 true |

### 响应示例

```json
{
  "status": "ok"
}
```

---

## 9. 票据

## 9.1 生成虚拟票

### `POST /api/v1/wm/tickets/generate`

### 请求参数

| 参数 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| order_id | body | number | 是 | 订单 ID（必须 paid） |

### 响应示例

```json
{
  "ticket_id": 5,
  "ticket_no": "TKabc123",
  "ticket_code": "TKabc123",
  "status": "issued"
}
```

---

## 9.2 核销虚拟票

### `POST /api/v1/wm/tickets/verify`

### 请求参数

| 参数 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| ticket_code | body | string | 是 | 票码 |

### 响应示例

```json
{
  "ticket_id": 5,
  "verified": true,
  "verify_time": "2026-04-14T13:00:00"
}
```

---

## 10. 评分

## 10.1 提交评分

### `POST /api/v1/wm/ratings`

### 请求参数

| 参数 | 位置 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- | --- |
| group_id | body | number | 是 | 群组ID |
| mate_score | body | number | 是 | 1-5 |
| route_score | body | number | 是 | 1-5 |
| bus_score | body | number | 是 | 1-5 |
| comment | body | string | 否 | 评价内容 |

### 响应示例

```json
{
  "rating_id": 7,
  "group_id": 1
}
```

---

## 10.2 群组评分汇总

### `GET /api/v1/wm/groups/{group_id}/ratings/summary`

### 响应示例

```json
{
  "group_id": 1,
  "count": 2,
  "avg_mate_score": 4.5,
  "avg_route_score": 4.0,
  "avg_bus_score": 5.0
}
```

---

## 11. 管理后台（占位）

## 11.1 指派车辆

### `POST /api/v1/wm/admin/groups/{group_id}/assign-bus`

### 当前状态

占位接口，返回 TODO。

### 响应示例

```json
{
  "message": "TODO: assign bus for group 1"
}
```

