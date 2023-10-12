# 使用说明

## 目录结构
```
快手弹幕
│
├── cookie  # 登录后存放cookie文件
│     └── 手机号.json # cookie文件
├── config.ini  # 配置文件 
├── main.py    # 前端运行文件
├── kuaishou_pb2.py  # 弹幕解析文件
└── requirements.txt # 依赖文件
```
## 安装
- 执行下列命令安装
```
pip install -r requirements.txt
playwright install firefox
```

## 优点
- 速度快
- 可以多线程
## 缺点
- 由于有滑块存在所以暂不支持无头模式

## 配置文件`config.ini`详解
```
live_ids = KPL704668133 多个使用','间隔
thread = 2
phone = 登录的手机号
```

## 待优化
- 移动快手滑块
