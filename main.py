#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  : Amos
# @FileName: daye.py.py
# @Blog    ：https://daogu.fun

import json, os
import telegram.ext
import telegram
import threading
import logging


# enable logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


# PATH = os.path.dirname(os.path.realpath(__file__)) + '/'


# 加载预设置项
CONFIG_LOCK = False
def_dir = os.path.join(os.getcwd(), 'config.json')  # 解决Windows和linux路径不一致问题
LANG = json.loads(open(def_dir, 'rb').read())

# 加载信息
DATA_LOCK = False
# data_temp = json.loads(open(PATH + 'data.json', 'r').read())
data_dir = os.path.join(os.getcwd(), 'data.json')
data_temp = json.loads(open(data_dir, 'r').read())


# 将信息存入json 中
def store():
    global DATA_LOCK
    while DATA_LOCK:
        time.sleep(0.05)
    DATA_LOCK = True
    with open('data.json', 'w', encoding='utf-8') as fw:
        json.dump(data_temp, fw, ensure_ascii=False,indent=4)
    DATA_LOCK = False


# 保存配置到config.json
def save_config():
    global CONFIG_LOCK
    while CONFIG_LOCK:
        time.sleep(0.05)
    CONFIG_LOCK = True
    with open('config.json', 'w', encoding='utf-8') as fc:
        json.dump(LANG, fc, ensure_ascii=False, indent=4)
    CONFIG_LOCK = False

# 从json 中查找
def find(keyword):
    with open('data.json', 'r') as f:
        info = json.load(f)[keyword]
        # rs = json.dumps(info, ensure_ascii=False)  # 解决输出中文问题，又注释掉，是因为已存在的key机制更改
        return info


# updater = telegram.ext.Updater('709532596:AAH1hZvDYwM1pj0FgYwM7YnMvYYqawYfDMc', use_context=True)
updater = telegram.ext.Updater(LANG["Token"], use_context=True)
dp = updater.dispatcher

print(LANG["Loading"])

me = updater.bot.get_me()
LANG["bot_username"] = '@' + me.username
print(me["first_name"]+' '+'为您服务')


# 初始化bot配置
def init_bot(user):
    global LANG
    if not str(user.id) in LANG["Admin"]:
        print(user.id)
        return False
    if str(user.id) in LANG["Admin"]:
        return True


# 处理命令
def process_command(update,context):
    global data_temp
    # 判断是否为管理员，并提示进行bot设置
    command = update.message.text[1:].replace(LANG["bot_username"], '').split(' ', 2)
    if init_bot(update.message.from_user):
        if LANG["WhiteList"] == "" and command[0] != 'setgroup':
            update.message.reply_text(LANG["GroupNeeded"])
        elif str(update.message.chat_id) in LANG["WhiteList"]:
            pass
    else:
        update.message.reply_text(LANG["AdminNeeded"])
        if command[0] == 'setadmin':
            LANG["Admin"] = str(update.message.from_user.id)
            updater.bot.sendMessage(chat_id=update.message.chat_id,text=LANG["Admin_set_succeed"])
    # 处理日常指令，/set = 设置信息及反馈；/get = 获取反馈; /setgroup 为设置生效群组
    if str(update.message.chat_id) in LANG["WhiteList"]:
        if command[0] == 'start':
            update.message.reply_text(LANG["Start"])
        elif command[0] == 'set':
            if not command[1] in data_temp:
                key = command[1]
                data_temp[key] = command[2]
                threading.Thread(target=store).start()
            elif command[1] in data_temp:
                temp = data_temp[command[1]] + '\n' + command[2]  # 更改方式，替换为字符串叠加
                data_temp[key] = temp
                threading.Thread(target=store).start()
        elif command[0] == 'get':
            if command[1] in data_temp:
                keyword = command[1]
                p = find(keyword)
                update.message.reply_text(p)
            else:
                update.message.reply_text(LANG["NotFound"])
        elif command[0] == 'del':
            todel = command[1]
            data_temp.pop(todel)
            threading.Thread(target=store).start()
        elif command[0] == 'get_id':
            update.message.reply_text(LANG["Get_id"]+str(update.message.chat_id))
        elif command[0] == 'help':
            update.message.reply_text(LANG["Help"])
    elif LANG["WhiteList"] == "" and command[0] == 'setgroup':
        if init_bot(update.message.from_user):
            LANG["WhiteList"] = str(update.message.chat_id)
            threading.Thread(target=save_config()).start()
            updater.bot.sendMessage(chat_id=update.message.chat_id,text=LANG["GroupSeted"])


# 处理特殊消息,通过'&'唤醒此功能
def process_message(update, context):
    global data_temp
    if str(update.message.chat_id) in LANG["WhiteList"]:
        print(update.message.chat_id)
        info = update.message.text[1:].split()
        if update.message.text[0] == '&':
            print(info[0])
            if info[0] in data_temp:
                output = find(info[0])
                update.message.reply_text(output)
            if info[0] == 'all':
                print(LANG["GetAll"])
                output=[]
                for key in data_temp.keys():
                    output.append(key)
                rs = json.dumps(output, ensure_ascii=False)
                update.message.reply_text(rs)


# 添加处理器
dp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.command, process_command))
dp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.all & ~telegram.ext.Filters.command, process_message))

updater.start_polling()
print('开始运行')

updater.idle()
print("停止运行...")

store()
save_config()

print('退出')


