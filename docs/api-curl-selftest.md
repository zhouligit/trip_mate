# TripMate 接口自测 Curl 文档

本文档用于后端接口自测与联调，统一使用域名：

- `https://www.wang-hao-hao.cn`

建议在 Linux/macOS 终端执行，依赖 `curl` 和 `jq`。

---

## 0. 初始化变量

```bash
HOST="https://www.wang-hao-hao.cn"
```

---

## 1. 健康检查

```bash
curl -s "$HOST/api/v1/wm/health"
```

---

## 2. 登录拿 Token

```bash
LOGIN=$(curl -s -X POST "$HOST/api/v1/wm/auth/wechat/login" \
  -H "Content-Type: application/json" \
  -d '{"code":"demo_001","nickname":"tester_a"}')

echo "$LOGIN" | jq
TOKEN=$(echo "$LOGIN" | jq -r '.token')
USER_ID=$(echo "$LOGIN" | jq -r '.userId')
echo "TOKEN=$TOKEN"
echo "USER_ID=$USER_ID"
```

---

## 3. 用户与 DNA

### 3.1 获取当前用户

```bash
curl -s "$HOST/api/v1/wm/users/me" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 3.2 更新用户信息

```bash
curl -s -X PUT "$HOST/api/v1/wm/users/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mobile":"13800000000"}' | jq
```

### 3.3 DNA 题库

```bash
curl -s "$HOST/api/v1/wm/dna/questions" | jq
```

### 3.4 提交 DNA

```bash
curl -s -X POST "$HOST/api/v1/wm/dna/submissions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "answers":[
      {"question_id":1,"option_id":1},
      {"question_id":2,"option_id":2},
      {"question_id":3,"option_id":1},
      {"question_id":4,"option_id":2},
      {"question_id":5,"option_id":1}
    ]
  }' | jq
```

### 3.5 获取最新 DNA

```bash
curl -s "$HOST/api/v1/wm/dna/me/latest" \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## 4. 定位、推荐、发现

### 4.1 更新定位

```bash
curl -s -X POST "$HOST/api/v1/wm/users/location" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"city_code":"chengdu","district_code":"jinjiang"}' | jq
```

### 4.2 旅伴推荐

```bash
curl -s "$HOST/api/v1/wm/match/recommendations" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 4.3 发现页群组

```bash
curl -s "$HOST/api/v1/wm/discovery/groups" \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## 5. 实名认证（P1）

### 5.1 查看状态

```bash
curl -s "$HOST/api/v1/wm/verification/me/status" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 5.2 微信实名

```bash
curl -s -X POST "$HOST/api/v1/wm/verification/wechat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"real_name":"张三","id_no_last4":"1234"}' | jq
```

### 5.3 再次查看状态

```bash
curl -s "$HOST/api/v1/wm/verification/me/status" \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## 6. 群组与投票（P0）

### 6.1 创建群组

```bash
CREATE_GROUP=$(curl -s -X POST "$HOST/api/v1/wm/groups" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"周末轻户外群","city_code":"chengdu","target_count":30,"threshold_count":30}')

echo "$CREATE_GROUP" | jq
GROUP_ID=$(echo "$CREATE_GROUP" | jq -r '.group_id')
echo "GROUP_ID=$GROUP_ID"
```

### 6.2 我的群组

```bash
curl -s "$HOST/api/v1/wm/groups/my?type=created" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 6.3 群详情

```bash
curl -s "$HOST/api/v1/wm/groups/$GROUP_ID" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 6.4 发起投票

```bash
START_VOTE=$(curl -s -X POST "$HOST/api/v1/wm/groups/$GROUP_ID/vote/start" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"duration_hours":24}')

echo "$START_VOTE" | jq
VOTE_ID=$(echo "$START_VOTE" | jq -r '.vote_id')
echo "VOTE_ID=$VOTE_ID"
```

### 6.5 当前投票会话

```bash
CURRENT=$(curl -s "$HOST/api/v1/wm/groups/$GROUP_ID/votes/sessions/current" \
  -H "Authorization: Bearer $TOKEN")

echo "$CURRENT" | jq
ROUTE_ID=$(echo "$CURRENT" | jq -r '.options[0].option_id')
echo "ROUTE_ID=$ROUTE_ID"
```

### 6.6 投票（组内路径）

```bash
curl -s -X POST "$HOST/api/v1/wm/groups/$GROUP_ID/votes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"routeId\":$ROUTE_ID}" | jq
```

### 6.7 投票结果

```bash
curl -s "$HOST/api/v1/wm/groups/$GROUP_ID/votes/result" \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## 7. 订单与支付（P1）

### 7.1 创建订单

```bash
CREATE_ORDER=$(curl -s -X POST "$HOST/api/v1/wm/orders" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"group_id\":$GROUP_ID}")

echo "$CREATE_ORDER" | jq
ORDER_ID=$(echo "$CREATE_ORDER" | jq -r '.order_id')
echo "ORDER_ID=$ORDER_ID"
```

### 7.2 拉起微信支付参数（mock）

```bash
PAY=$(curl -s -X POST "$HOST/api/v1/wm/orders/$ORDER_ID/pay/wechat" \
  -H "Authorization: Bearer $TOKEN")

echo "$PAY" | jq
OUT_TRADE_NO=$(echo "$PAY" | jq -r '.out_trade_no')
echo "OUT_TRADE_NO=$OUT_TRADE_NO"
```

### 7.3 支付回调（mock）

```bash
curl -s -X POST "$HOST/api/v1/wm/payments/wechat/notify" \
  -H "Content-Type: application/json" \
  -d "{\"out_trade_no\":\"$OUT_TRADE_NO\",\"wechat_txn_id\":\"wx_txn_001\",\"success\":true}" | jq
```

### 7.4 订单详情与列表

```bash
curl -s "$HOST/api/v1/wm/orders/$ORDER_ID" \
  -H "Authorization: Bearer $TOKEN" | jq

curl -s "$HOST/api/v1/wm/orders" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 7.5 退款申请

```bash
curl -s -X POST "$HOST/api/v1/wm/orders/$ORDER_ID/refund/apply" \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## 8. 票据与评分（P2）

### 8.1 生成虚拟票

```bash
TICKET=$(curl -s -X POST "$HOST/api/v1/wm/tickets/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"order_id\":$ORDER_ID}")

echo "$TICKET" | jq
TICKET_CODE=$(echo "$TICKET" | jq -r '.ticket_code')
echo "TICKET_CODE=$TICKET_CODE"
```

### 8.2 核销车票

```bash
curl -s -X POST "$HOST/api/v1/wm/tickets/verify" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"ticket_code\":\"$TICKET_CODE\"}" | jq
```

### 8.3 提交评分

```bash
curl -s -X POST "$HOST/api/v1/wm/ratings" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"group_id\":$GROUP_ID,\"mate_score\":5,\"route_score\":4,\"bus_score\":5,\"comment\":\"nice\"}" | jq
```

### 8.4 评分汇总

```bash
curl -s "$HOST/api/v1/wm/groups/$GROUP_ID/ratings/summary" \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## 9. 常见问题

- `401 Unauthorized`：Token 缺失或过期，重新登录获取新 token。
- `404 Not Found`：路径不对，确认是否使用 `/api/v1/wm` 前缀。
- `500 Internal Server Error`：优先看服务日志：
  - `journalctl -u tripmate-api -f`
- 支付流程异常：先确认支付回调接口入参 `out_trade_no` 是否来自 `/orders/{id}/pay/wechat` 的返回值。
