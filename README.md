# FastAPI AI项目 简介
一边承接实际业务的同时想把这个项目做成一个AI应用的脚手架,搭建这个项目之前
想去网上找一些脚手架框架,看了一下都不太合适，干脆自己搭一个。

## 目前功能
(2025.07.22)
- API信息管理 存储API信息,提供了便捷的从AI提取API参数到调用的函数,但是结果的处理需要自己实现
- Prompt提示词管理 持久化提示词,提供便捷动态提示词处理，处理完的提示词目前主要服务于openAI库的调用
- openAI库对 千问 豆包 deepseek 进行了封装， 豆包的封装还包含联网搜索
- dify对接 存在一个实际业务的dify对接实例,并且对dify对话内容进行了持久化 保留了用户的历史对话记录
- 用户画像 基于用户的历史对话记录通过定时任务进行用户画像分析

## 部署和启动
(2025.07.22)
目前只需要一个外部mysql服务即可成功启动项目，后期可能会添加redis服务、milvus服务.
部分接口执行会依赖一些初始化数据,可自行去src/db/ddl/dml.sql 中查看 (早期的数据有维护，后面没有维护了)

**需要根据.env.template 创建一个.env文件**

## 文件架构
- src/ai 通用的对Ai库的封装以及常用函数封装，目前只对openAI库进行了封装
- src/common 通用文件夹，打算放一些枚举类或常量
- src/controller 控制层,存放接口
- src/dao 数据访问层,存放数据库操作
- src/db 数据库文件夹,存放数据库的DDL和DML
- src/env 空的，当时AI自动生成的 忘记删了
- src/exception 自定义异常类存放处
- src/myHttp Http相关处理，包括结果封装类，以及http请求封装
- src/mySchedules 定时任务存放处
- src/pojo 实体类、视图类、业务类 存放处
- src/service 业务逻辑层，存放业务逻辑
- src/test 测试类存放处
- src/utils 工具类存放处
- static/ 静态资源存放处,部署到服务器上有时候请求不到swagger的UI资源，干脆把它download到本地了



## 笔记
这是实际开发中打包镜像 部署docker容器时会用的命令  [stone-ai:0.1.5] 镜像名和版本可自行修改 


docker build -t stone-ai:0.1.10 .


docker save -o stone-ai-0.1.10.tar stone-ai:0.1.10


docker load -i stone-ai-0.1.10.tar


docker run -p 8000:8000 --env-file .env -d --name stone-ai-0110 stone-ai:0.1.10

重载ng
nginx -t
nginx -s reload


dify 修改配置文件后
docker-compose down && docker-compose up -d
或者
docker-compose build
docker-compose restart