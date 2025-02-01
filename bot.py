import os
import nest_asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from youtubesearchpython import VideosSearch


nest_asyncio.apply()


TOKEN = os.getenv('TOKEN')

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Напишите название песни или видео, и я найду его на YouTube.")

async def search_youtube(update: Update, context: CallbackContext):
    query = update.message.text  
    if not query:
        await update.message.reply_text("Пожалуйста, укажите название.")
        return

 
    videos_search = VideosSearch(query, limit=5)  # 5 рузкльтатов
    results = videos_search.result()

    if not results['result']:
        await update.message.reply_text("Видео не найдено. Попробуйте другое название.")
        return

 
    response = "Вот что я нашел:\n"
    for idx, video in enumerate(results['result'], start=1):
        title = video['title']
        link = video['link']
        response += f"{idx}. {title}\n{link}\n\n"

    await update.message.reply_text(response)

async def main():
    application = Application.builder().token(TOKEN).build()


    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), search_youtube))

 
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
