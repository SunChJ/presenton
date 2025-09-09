# FRP 内网穿透配置

## 配置说明

### 笔记本端（客户端）
- `docker-compose.yml` - 笔记本端服务配置
- `frpc.ini` - FRP 客户端配置

### VPS 端（服务端）配置示例

```yaml
version: '3.8'

services:
  app:
    image: 'jc21/nginx-proxy-manager:latest'
    restart: unless-stopped
    ports:
      - '80:80'
      - '81:81'
      - '443:443'
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
    networks:
      - npm-network

  frps:
    image: snowdreamtech/frps:latest
    container_name: frps
    restart: unless-stopped
    ports:
      - "7000:7000"
      - "7500:7500"
      - "8080:8080"
    volumes:
      - ./frps.ini:/etc/frp/frps.ini
    networks:
      - npm-network

networks:
  npm-network:
    driver: bridge
```

VPS端 `frps.ini`:
```ini
[common]
bind_port = 7000
dashboard_port = 7500
dashboard_user = admin
dashboard_pwd = your_password
token = your_secure_token

vhost_http_port = 8080
```

## 部署步骤

### 1. 配置文件修改
修改 `frpc.ini` 中的：
- `server_addr` - VPS IP 地址
- `token` - 与 VPS 端相同的 token
- `custom_domains` - 你的域名

### 2. 环境变量
创建 `.env` 文件：
```
OPENAI_API_KEY=your_openai_api_key
```

### 3. 启动服务
```bash
cd frp
docker-compose up -d
```

### 4. NPM 配置
在 NPM 管理界面（http://vps_ip:81）添加：
- Domain: your-domain.com
- Forward to: frps:8080
- 高级选项添加 SSE 支持配置

## 测试
```bash
curl https://your-domain.com/api/v1/ppt/agent/test/health
```