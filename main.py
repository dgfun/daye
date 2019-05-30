#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : Amos
# @FileName: main.py
# @Blog    ：https://daogu.fun


import json, os
import telegram.ext
import telegram
import threading
import logging
import time

# enable logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    )

# 加载预设置项
CONFIG_LOCK = False
def_dir = os.path.join(os.getcwd(), 'config.json')  # 解决Windows和linux路径不一致问题
LANG = json.loads(open(def_dir, 'rb').read())

# 加载对话表
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
        json.dump(data_temp, fw, ensure_ascii=False, indent=4)
    DATA_LOCK = False


# 保存配置到config.json
def save_config():
    global CONFIG_LOCK
    while CONFIG_LOCK:
        time.sleep(0.05)
    CONFIG_LOCK = True
    with open('config.json', 'w', encoding='utf-8') as fw:
        json.dump(LANG, fw, ensure_ascii=False, indent=4)
    CONFIG_LOCK = False


# 从对话表data.json中获取信息
def find(keyword):
    with open('data.json', 'r') as f:
        info = json.load(f)[keyword]
        return info


updater = telegram.ext.Updater(LANG["Token"], use_context=True)
dp = updater.dispatcher

print(LANG["Loading"])

me = updater.bot.get_me()
LANG["bot_username"] = '@' + me.username
print(me["first_name"] + '为您服务')


# 初始化bot配置
def init_bot(user):
    if LANG["Owner"] == "" or str(user.id) not in LANG["Owner"]:
        return False
    if str(user.id) in LANG["Owner"]:
        return True


# 处理命令
def process_command(update, context):
    global data_temp
    # 判断是否为所有者，并提示进行bot设置
    command = update.message.text[1:].replace(LANG["bot_username"], '').split(' ', 2)
    if init_bot(update.message.from_user):
        # 判断是否已设置工作群组，并设置
        if LANG["Group"] == "":
            if command[0] != 'setgroup':
                update.message.reply_text(LANG["GroupNeeded"])
            elif command[0] == 'setgroup':
                LANG["Group"] = str(update.message.chat_id)
                # 获取管理员列表并设置
                p = updater.bot.get_chat_administrators(update.message.chat.id)
                admin0 = ""
                for i in range(0, len(p)):
                    temp = str(p[i]["user"]["id"])
                    admin0 = temp + "," + admin0
                LANG["Admin"] = admin0
                threading.Thread(target=save_config).start()
                updater.bot.sendMessage(chat_id=update.message.chat_id, text=LANG["GroupSeted"])
    else:
        if command[0] == 'setowner':
            if LANG["Owner"] == "":
                LANG["Owner"] = str(update.message.from_user.id)
                threading.Thread(target=save_config).start()
                updater.bot.sendMessage(chat_id=update.message.chat_id, text=LANG["Owner_set_succeed"])
            elif not str(update.message.from_user.id) in LANG["Owner"]:
                # 揪出群里的二五仔！
                updater.bot.sendMessage(chat_id=update.message.chat_id, text=LANG["OwnerExists"])
        elif LANG["Owner"] == "":
            update.message.reply_text(LANG["OwnerNeeded"])
    # 处理日常指令，/set = 设置信息及反馈；/get = 获取反馈;/help获取帮助;/group_id 获取群组id
    if str(update.message.chat_id) in LANG["Group"]:
        # 仅管理员可用指令
        if str(update.message.from_user.id) in LANG["Admin"]:
            if command[0] == 'start':
                update.message.reply_text(LANG["Start"])
            elif command[0] == 'set':
                if len(command) >2:
                    key = command[1]
                    if not command[1] in data_temp:
                        data_temp[key] = command[2]
                        threading.Thread(target=store).start()
                    elif command[1] in data_temp:
                        temp = data_temp[command[1]] + '\n' + command[2]  # 更改方式，替换为字符串叠加
                        data_temp[key] = temp
                        threading.Thread(target=store).start()
                else:
                    updater.bot.sendMessage(chat_id=update.message.chat_id,text=LANG["CommandError"])
            elif command[0] == 'renew' and len(command) == 3:
                key = command[1]
                data_temp[key] = command[2]
                threading.Thread(target=store).start()
            elif command[0] == 'del' and len(command) == 2:
                todel = command[1]
                data_temp.pop(todel)
                threading.Thread(target=store).start()
        # 群员可用
        if command[0] == 'get' and len(command) == 2:
            if command[1] in data_temp:
                keyword = command[1]
                p = find(keyword)
                update.message.reply_text(p)
            else:
                update.message.reply_text(LANG["NotFound"])
        # 获取群组id
        elif command[0] == 'get_id':
            update.message.reply_text(LANG["Get_id"] + str(update.message.chat_id))
        # 获取使用说明
        elif command[0] == 'help':
            update.message.reply_text(LANG["Help"])

    # 获取个人id及@username
    if command[0] == 'get_me':
        myinfo = update.message.from_user
        print(myinfo)
        id = myinfo["id"]
        username = myinfo["username"]
        temp = "id:" +str(id) +'\n' + "username:" + "@" + username
        update.message.reply_text(temp)

    # 自动删除命令
    if update.message.text[0] == '/':
        time.sleep(5.0)
        context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)


# 不通过特殊命令唤醒
def process_message(update, context):
    global data_temp
    if str(update.message.chat_id) in LANG["Group"]:
        info = update.message.text.split()
        if info[0] in data_temp and len(info) == 1:
            output = find(info[0])
            update.message.reply_text(output)
        if info[0] == 'all' and len(info) == 1:
            print(LANG["GetAll"])
            output = []
            for key,value in data_temp.items():
                output.append(f'{key}--{value[:5]}...')
            rs = '\n'.join(output).join(['\n', '\n'])
            update.message.reply_text(rs)


# 添加处理器
dp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.command, process_command))
dp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text
                                           & ~telegram.ext.Filters.private
                                           & ~telegram.ext.Filters.command,
                                           process_message))


updater.start_polling()
print('开始运行')

updater.idle()
print("停止运行...")

store()
save_config()

print('退出')
