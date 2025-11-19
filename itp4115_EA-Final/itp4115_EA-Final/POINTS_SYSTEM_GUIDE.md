# 會員積分系統 - Member Points System

## 概述 Overview

實現了完整的會員積分系統，用戶購買電影票時可獲得積分，積分可用於兌換優惠券。

## 功能特性 Features

### 1. 積分獲取 (Points Earning)
- **兌換比率**: HK$1 = 5 積分
- **獲取方式**: 購買電影票時自動累積
- **即時反饋**: 購票成功後顯示獲得的積分數量

### 2. 積分兌換 (Points Exchange)
用戶可使用積分兌換以下優惠券：

| 優惠券類型 | 所需積分 | 折扣內容 | 最低消費 |
|-----------|---------|---------|---------|
| 10%折扣券 | 500點 | 10% OFF | HK$100 |
| 20%折扣券 | 1000點 | 20% OFF | HK$200 |
| HK$30優惠券 | 600點 | HK$30 OFF | HK$150 |
| HK$50優惠券 | 1000點 | HK$50 OFF | HK$250 |
| 免費電影票 | 2000點 | HK$100 OFF | 無限制 |

### 3. 積分顯示 (Points Display)
- **會員中心**: 顯示當前積分總數
- **積分兌換頁面**: 實時顯示可用積分和可兌換項目

## 修改的檔案 Modified Files

### 1. 資料庫模型 (Database Model)
**檔案**: `app/models.py`
- 新增 `points` 欄位到 `User` 模型
- 預設值為 0

### 2. 資料庫遷移 (Database Migration)
- 自動生成遷移檔案: `migrations/versions/0a2afc9c5d47_add_points_to_user_model.py`
- 已執行 `flask db upgrade`

### 3. 購票邏輯 (Ticket Purchase Logic)
**檔案**: `app/routes.py`
- 修改 `cinema_buy_ticket()` 函數
- 購票成功後自動計算並累積積分
- 更新成功訊息，顯示獲得的積分

### 4. 優惠券系統 (Coupon System)
**檔案**: `app/data/coupon_system.py`

#### 新增功能:
- `get_points_coupons()`: 獲取可兌換的優惠券列表
- `exchange_points_for_coupon()`: 處理積分兌換邏輯

#### 新增優惠券類型:
- `POINTS_10OFF`: 10%折扣券 (500點)
- `POINTS_20OFF`: 20%折扣券 (1000點)
- `POINTS_FIXED30`: HK$30優惠券 (600點)
- `POINTS_FIXED50`: HK$50優惠券 (1000點)
- `POINTS_FREETICKET`: 免費電影票 (2000點)

### 5. 路由 (Routes)
**檔案**: `app/routes.py`

新增路由:
- `/exchange_points` (GET): 顯示積分兌換頁面
- `/exchange_points/<coupon_type>` (POST): 處理積分兌換請求

### 6. 模板 (Templates)

#### 新增模板:
**檔案**: `app/templates/exchange_points.html.j2`
- 積分兌換介面
- 顯示用戶當前積分
- 顯示所有可兌換的優惠券
- 兌換按鈕（積分不足時禁用）

#### 修改模板:
**檔案**: `app/templates/profile.html.j2`
- 在帳號資訊卡片中顯示會員積分
- 新增"積分兌換"快速功能按鈕

**檔案**: `app/templates/my_coupons.html.j2`
- 在頁面標題列新增"積分兌換"按鈕

## 使用流程 User Flow

### 賺取積分:
1. 用戶登入系統
2. 選擇電影並購買電影票
3. 完成付款後，系統自動計算積分 (總金額 × 5)
4. 積分即時累積到用戶帳戶
5. 頁面顯示: "✅ 購票成功！獲得 XXX 積分"

### 兌換優惠券:
1. 進入「會員中心」
2. 點擊「🌟 積分兌換」按鈕
3. 查看當前積分和可兌換優惠券
4. 選擇想要的優惠券，點擊「立即兌換」
5. 系統扣除相應積分，生成優惠券
6. 優惠券自動添加到「我的優惠券」
7. 有效期為 30 天

### 使用優惠券:
1. 進入「我的優惠券」查看已兌換的優惠券
2. 購買電影票時輸入優惠券代碼
3. 系統自動計算折扣
4. 完成購票

## 技術細節 Technical Details

### 積分計算邏輯:
```python
# 1美元 = 5積分
points_earned = int(total_price * 5)
current_user.points += points_earned
db.session.commit()
```

### 積分兌換邏輯:
```python
# 檢查積分是否足夠
if user.points < points_cost:
    return error

# 扣除積分
user.points -= points_cost

# 生成優惠券
coupon = create_coupon_for_user(user.id, coupon_type)

# 提交到資料庫
db.session.commit()
```

### 優惠券有效期:
- 所有積分兌換的優惠券有效期為 30 天
- 可在 `COUPON_TYPES` 中的 `valid_days` 設定

## 測試建議 Testing Recommendations

1. **積分累積測試**:
   - 購買不同價格的電影票
   - 驗證積分計算是否正確 (價格 × 5)
   - 檢查積分是否正確累積到用戶帳戶

2. **積分兌換測試**:
   - 測試積分足夠時的兌換
   - 測試積分不足時的錯誤提示
   - 驗證兌換後積分是否正確扣除
   - 檢查優惠券是否成功生成

3. **優惠券使用測試**:
   - 使用兌換的優惠券購買電影票
   - 驗證折扣計算是否正確
   - 確認購票後仍能獲得積分（基於折後價格）

## 未來擴展建議 Future Enhancements

1. **積分歷史記錄**:
   - 記錄積分獲得和使用的歷史
   - 顯示積分變動明細

2. **會員等級制度**:
   - 根據累積積分設定會員等級
   - 不同等級享有不同優惠

3. **積分過期機制**:
   - 設定積分有效期
   - 到期自動清除

4. **積分活動**:
   - 雙倍積分日
   - 生日月額外積分
   - 推薦好友獎勵積分

5. **更多兌換選項**:
   - 實體商品兌換
   - 會員特權兌換
   - 合作商家優惠

## 注意事項 Notes

1. 積分計算使用 `int()` 取整，確保積分為整數
2. 積分兌換為原子操作，使用資料庫事務確保一致性
3. 優惠券代碼自動生成，確保唯一性
4. 所有金額單位為 HK$（港幣）
5. 積分不能轉讓或退款

## 相關路由 Related Routes

- `/profile` - 會員中心（顯示積分）
- `/exchange_points` - 積分兌換頁面
- `/my_coupons` - 我的優惠券
- `/cinema/buy_ticket` - 購票（獲得積分）
