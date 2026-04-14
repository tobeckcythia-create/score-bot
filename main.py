from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import sqlite3
import os

conn = sqlite3.connect("scores.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS scores (user TEXT PRIMARY KEY, score INTEGER)")
conn.commit()

def get_score(user):
    cursor.execute("SELECT score FROM scores WHERE user=?", (user,))
    result = cursor.fetchone()
    return result[0] if result else 0

def update_score(user, value):
    current = get_score(user)
    new_score = current + value
    cursor.execute("REPLACE INTO scores (user, score) VALUES (?, ?)", (user, new_score))
    conn.commit()
    return new_score

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = context.args[0]
    points = int(context.args[1])
    score = update_score(user, points)
    await update.message.reply_text(f"✅ {user} +{points}分\n当前：{score}")

async def minus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = context.args[0]
    points = int(context.args[1])
    score = update_score(user, -points)
    await update.message.reply_text(f"❌ {user} -{points}分\n当前：{score}")

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        user = context.args[0]
    else:
        user = update.effective_user.username
    s = get_score(user)
    await update.message.reply_text(f"📊 {user}：{s}分")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor.execute("SELECT user, score FROM scores ORDER BY score DESC LIMIT 10")
    rows = cursor.fetchall()
    text = "🏆 排行榜\n"
    for i, (u, s) in enumerate(rows, 1):
        text += f"{i}. {u} - {s}分\n"
    await update.message.reply_text(text)

app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

app.add_handler(CommandHandler("加分", add))
app.add_handler(CommandHandler("扣分", minus))
app.add_handler(CommandHandler("积分", score))
app.add_handler(CommandHandler("排行榜", top))

app.run_polling()
