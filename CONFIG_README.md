# 配置文件说明

## config.json 配置格式

`config.json` 文件用于存储应用程序的配置信息，包括请求间隔和邮件通知设置。

### 配置示例

```json
{
  "request_interval": 3,
  "notification_email": "your-email@example.com",
  "smtp_host": "smtp.example.com",
  "smtp_port": 465,
  "smtp_username": "your-email@example.com",
  "smtp_password": "your-password",
  "smtp_use_ssl": true,
  "target_price_percentage": 70
}
```

### 配置项说明

| 配置项 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `request_interval` | 整数 | 请求间隔（秒），建议设置为3-10秒，防止被封号 | 3 |
| `notification_email` | 字符串 | 接收通知的邮箱地址 | 空字符串 |
| `smtp_host` | 字符串 | SMTP服务器地址 | 空字符串 |
| `smtp_port` | 整数 | SMTP服务器端口 | 465 |
| `smtp_username` | 字符串 | SMTP登录用户名（通常是邮箱地址） | 空字符串 |
| `smtp_password` | 字符串 | SMTP登录密码（可能是邮箱密码或授权码） | 空字符串 |
| `smtp_use_ssl` | 布尔值 | 是否使用SSL加密连接 | true |
| `target_price_percentage` | 整数 | 目标价格百分比，当前价低于或等于加入价的该百分比时触发抢单（10-100） | 70 |

## 常见邮箱服务配置

### 1. QQ邮箱

```json
{
  "request_interval": 3,
  "notification_email": "your-qq@qq.com",
  "smtp_host": "smtp.qq.com",
  "smtp_port": 465,
  "smtp_username": "your-qq@qq.com",
  "smtp_password": "你的授权码",
  "smtp_use_ssl": true
}
```

**注意**：QQ邮箱需要使用授权码，不是QQ密码。获取方式：
1. 登录QQ邮箱网页版
2. 设置 → 账户 → 开启SMTP服务
3. 生成授权码

### 2. 163邮箱

```json
{
  "request_interval": 3,
  "notification_email": "your-email@163.com",
  "smtp_host": "smtp.163.com",
  "smtp_port": 465,
  "smtp_username": "your-email@163.com",
  "smtp_password": "你的授权码",
  "smtp_use_ssl": true
}
```

**注意**：163邮箱也需要使用授权码。

### 3. Gmail

```json
{
  "request_interval": 3,
  "notification_email": "your-email@gmail.com",
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 465,
  "smtp_username": "your-email@gmail.com",
  "smtp_password": "你的应用专用密码",
  "smtp_use_ssl": true
}
```

**注意**：Gmail需要使用应用专用密码，不是普通密码。

### 4. Outlook/Hotmail

```json
{
  "request_interval": 3,
  "notification_email": "your-email@outlook.com",
  "smtp_host": "smtp-mail.outlook.com",
  "smtp_port": 587,
  "smtp_username": "your-email@outlook.com",
  "smtp_password": "你的密码",
  "smtp_use_ssl": false
}
```

**注意**：Outlook使用587端口和STARTTLS（`smtp_use_ssl: false`）。

### 5. 企业邮箱（以腾讯企业邮箱为例）

```json
{
  "request_interval": 3,
  "notification_email": "your-email@yourcompany.com",
  "smtp_host": "smtp.exmail.qq.com",
  "smtp_port": 465,
  "smtp_username": "your-email@yourcompany.com",
  "smtp_password": "你的密码",
  "smtp_use_ssl": true
}
```

## 创建配置文件

### 方法1：通过GUI界面配置

1. 启动程序后，在右上角"配置"区域填写各项配置
2. 点击"保存配置"按钮
3. 配置会自动保存到 `config.json` 文件

### 方法2：手动创建配置文件

1. 复制 `config.example.json` 为 `config.json`
2. 根据你的邮箱服务修改相应的配置项
3. 保存文件

## 注意事项

1. **请求间隔**：建议设置为3-10秒，过短可能被服务器限制，过长可能错过抢单机会
2. **邮箱密码**：很多邮箱服务需要使用授权码或应用专用密码，而不是登录密码
3. **SSL设置**：
   - 使用465端口时，通常需要 `smtp_use_ssl: true`
   - 使用587端口时，通常需要 `smtp_use_ssl: false`（使用STARTTLS）
4. **安全性**：`config.json` 包含敏感信息，请妥善保管，不要提交到版本控制系统

## 邮件通知内容

当抢单成功时，会发送包含以下信息的邮件：

- 游戏名
- 当前价格
- 加入抢单时最低价
- 价格差
- 折扣率
- 状态：抢单成功
- 抢单时间
- 预计放出时间（抢单时间 + 5分钟）

