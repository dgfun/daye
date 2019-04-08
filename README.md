# 传达室大爷:

一个群组辅助机器人，目前只能帮助记录群组常用信息，~~性感火热~~，清爽、成长型bot

# 安 装

```
创建bot，配置bot的图片，名字...
获取bot的token
git clone 
pip install python-telegram-bot==12.0.0b1 --upgrade

```

# 配 置
```
修改config.json中的"Token"为自己的机器人token
例如    "Token": "709532412:AAH1hZvXYwM1Qj0WgYwM7YnMvYYqawYfqMc",
python3 main.py
发送/setowner给机器人，设置自己为管理员
邀请机器人进群组，/setgroup 设置为工作群组
```
# 帮 助
```使用/set keyword value 设置对话表keyword:value，即输入一个关键词keyword，设定对应的反馈value
如：/set amos 菜鸡，扶不起...
使用/get keyword 获取对应的反馈
如：/get amos
会得到回复 菜鸡，扶不起
使用/del keyword 删除keyword对话表
如/del amos
使用/renew keyword vaue 直接替换原来的keyword:value对话表
同时，通过"&"字符后面跟上关键词也可以获得对应的反馈
如：&amos 
会得到回复 菜鸡，扶不起
输入&all则会得到已记录的关键词列表
或者启用关键词匹配功能，直接使用关键词即可获取反馈

amos
菜鸡，扶不起

群组内发送/get_id 可获取群组id
/help 获取帮助
...
```

# TO DO

MARKDOWN消息

优化链接显示方式

改为mongodb存储