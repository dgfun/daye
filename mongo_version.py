#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17/6/2019 2:17 PM
# @Author  : Amos
# @File    : mongo_version.py

import json
import telegram.ext
import telegram
import logging
import time
import pymongo
from telegram import (ParseMode, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)

# enable logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    )

client = pymongo.MongoClient()

db = client.daye


def write_info(collection):
    clt = db[collection]
    with open("config.json", 'r', encoding='utf-8') as f:
        info = json.load(f)
    clt.insert_one(info)


# 搜索
def search(collection, search_key=True, *args):
    clt = db[collection]
    if search_key:
        condition = {}
        for each in args:
            condition[each] = {"$exists": True}
        print(f'filters:{condition}')
        result = clt.find_one(condition)
    elif len(args) == 1:
        result = clt.find_one({"keyword": args[0]})
    else:
        result = None
    return result


def deposit(collection, dict, check=False, *args):
    clt = db[collection]
    if clt.find_one_and_update(
            {"keyword": dict["keyword"]},
            {'$addToSet': {"value": {'$each': dict["value"]}}}
    ):
        msg = "keyword exists, update value succeeded"
    else:
        clt.insert_one(dict)
        msg = "keyword not found, insert succeeded"
    return msg


def group_username(update):
    if update.message.chat.username:
        username = update.message.chat.username
    else:
        username = str(update.message.chat.id)
    return username


# 封禁用户
def ban(update, context):
    msg = update.message
    if db[group_username(update)].find_one({
            str(update.message.from_user.id): {"$exists": True}}) is None:
        update.message.reply_text("只允许管理员进行此等骚操作")
        return
    elif msg.reply_to_message:
        tg_msg = msg.reply_to_message
        context.bot.restrict_chat_member(chat_id=msg.chat_id, user_id=tg_msg.from_user.id,
                                         can_send_messages=False, can_send_media_messages=False,
                                         can_send_other_messages=False, can_add_web_page_previews=False)
        action_feedback = "\n".join(
            [f"用户：{tg_msg.from_user.id}  因骚操作导致封禁", f"执行人：{msg.from_user.first_name}"]
        )
        update.message.reply_text(action_feedback)


# 格式化信息为字典
def info(keyword, value, **kwargs):
    now = time.strftime("%Y/%m/%d", time.localtime())
    conv = {
        "keyword": keyword,
        "value": value,
        "time": now,
        "others": kwargs
            }

    return conv


# 添加触媒
def set(update, context):
    text = update.message.text_markdown.replace('\\','').split(' ', 2)
    print(text)
    key = str(update.message.from_user.id)
    if db[group_username(update)].find_one({
            key: {"$exists": True}}) is None:
        update.message.reply_text("只允许管理员进行此等骚操作")
        return
    elif len(text) == 3:
        print("准备入库")
        keyword = context.args[0]
        value = [text[2]]
        print(value)
        # value = args[1:]
        msg = info(keyword, value)
        deposit(group_username(update), msg)
    elif len(context.args) == 1 and update.message.reply_to_message:
        tg_msg = update.message.reply_to_message.text_markdown.replace('\\', '')
        keyword = context.args[0]
        value = [tg_msg]
        msg = info(keyword, value)
        deposit(group_username(update), msg)
    else:
        update.reply_text("指令错误，使用方式：/set 关键词 内容；或者回复一条消息 /set 关键词 可保存该信息")


def process_msg(update, context):
    keyboard = [[KeyboardButton('新人解禁')]]
    context.chat_data["new_member"] = []
    if update.message.new_chat_members:
        new_user = "\n"
        for each in update.message.new_chat_members:
            if each["is_bot"]:
                update.message.reply_text(f"有新机器人@{each.username} 入群")
            else:
                new_user += "@"+each.username + ' '
                context.chat_data["new_member"].append(each.id)
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, selective=True)
        text = new_user + "\n" + "欢迎入群,新人入群请先解禁。"
        if new_user != "\n":
            context.bot.send_message(chat_id=update.message.chat.id, text=text, reply_markup=reply_markup)
        time.sleep(3.0)
        context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
    elif update.message.from_user.id in context.chat_data["new_member"]:
        if update.message.text != "新人解禁":
            context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
        else:
            context.chat_data["new_member"].remove(update.message.from_user.id)
            update.message.reply_text("新人解禁成功，请开始本群之旅", reply_markup=ReplyKeyboardRemove())
            pass
    elif update.message.left_chat_member:
        context.bot.delete_message(chat_id=update.message.chat.id, message_id=update.message.message_id)
        pass
    elif update.message.text:
        condition = update.message.text
        answer = search(group_username(update), False, condition)
        if answer is not None:
            msg = "\n".join(answer["value"])
            update.message.reply_text(msg, disable_web_preview=True, parse_mode=ParseMode.MARKDOWN)
    else:
        pass


def start(update, context):
    msg = update.message
    chat_type = msg.chat.type
    if chat_type == "private":
        msg.reply_text("大爷上线")
    else:
        admin = context.bot.get_chat_administrators(chat_id=msg.chat_id)
        admin_list = {}
        for each in admin:
            profile = {"user": {"id": each.user.id, "username": each.user.name,
                                "can_restrict_members": each["can_restrict_members"],
                                "status": each["status"]}}
            admin_list[str(each.user.id)] = profile
        db[group_username(update)].insert_one(admin_list)
        update.message.reply_text("加载完成...")


def main():

    write_info("config")

    print("读取配置...")

    token = search("config", True, "Token")["Token"]

    updater = telegram.ext.Updater(token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(telegram.ext.CommandHandler("set", set, pass_user_data=True ))

    dp.add_handler(telegram.ext.CommandHandler("start", start))

    dp.add_handler(telegram.ext.CommandHandler("ban", ban, filters=~telegram.ext.Filters.private))

    dp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.all, process_msg))

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    main()
