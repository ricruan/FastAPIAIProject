# FastAPI 项目 Docker 配置

本目录包含用于容器化 FastAPI 应用程序的 Docker 配置文件。
不要看，这是AI生成的

## 文件说明

- `Dockerfile`: 用于构建应用程序 Docker 镜像的配置文件
- `.dockerignore`: 指定构建 Docker 镜像时要忽略的文件和目录
- `docker-compose.yml`: 定义和运行多容器 Docker 应用程序的配置文件

## 使用说明

### 构建和运行 Docker 镜像

1. 确保已安装 Docker 和 Docker Compose

2. 在项目根目录下构建 Docker 镜像:

```bash
docker build -t fastapi-app -f docker/Dockerfile .
```

3. 运行 Docker 容器:

```bash
docker run -p 8000:8000 fastapi-app
```

### 使用 Docker Compose

1. 启动所有服务:

```bash
docker-compose -f docker/docker-compose.yml up
```

2. 在后台启动所有服务:

```bash
docker-compose -f docker/docker-compose.yml up -d
```

3. 停止所有服务:

```bash
docker-compose -f docker/docker-compose.yml down
```

## 数据库配置

默认的 `docker-compose.yml` 包含 PostgreSQL 数据库配置。如果你使用不同的数据库，请相应地修改配置。

### PostgreSQL 配置

- **用户名**: postgres
- **密码**: postgres
- **数据库名**: fastapi_db
- **端口**: 5432
- **连接 URL**: postgresql://postgres:postgres@db:5432/fastapi_db

## 环境变量

你可以在 `docker-compose.yml` 文件中的 `environment` 部分添加或修改环境变量。

## 卷和持久化

PostgreSQL 数据存储在名为 `postgres_data` 的 Docker 卷中，确保数据在容器重启后仍然存在。

## 网络

所有服务都连接到名为 `fastapi_network` 的 Docker 网络，允许它们相互通信。

## 笔记
docker build -t stone-ai:0.1.5 .
docker save -o stone-ai-0.1.5.tar stone-ai:0.1.5
docker load -i stone-ai-0.1.5.tar
docker run -p 8000:8000 --env-file .env -d --name stone-ai-015 stone-ai:0.1.5

重载ng
nginx -t
nginx -s reload


dify 修改配置文件后
docker-compose down && docker-compose up -d
或者
docker-compose build
docker-compose restart