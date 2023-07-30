# 使用说明

## 目录结构
```
main
├── danmu
│   └── cookie  # 登录后存放cookie文件
│       └── 手机号.json # cookie文件
│   └── config.ini  # 配置文件 
│   └── cookie.txt  # cookie文件，用于获取用户年龄、性别
│   └── main.py    # 前端运行文件
│   └── kuaishou_pb2.py  # 弹幕解析文件
└── requirements.txt # 依赖文件
```

## 配置文件`config.ini`详解
```
live_ids = KPL704668133
thread = 2
phone = 登录的手机号
```