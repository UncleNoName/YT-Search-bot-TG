import os
import nest_asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from youtubesearchpython import VideosSearch
from http.server import HTTPServer, BaseHTTPRequestHandler  # Для создания фейкового сервера

nest_asyncio.apply()

TOKEN = os.getenv('TOKEN')

# Функция для команды /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Напишите название песни или видео, и я найду его на YouTube.")

# Функция для поиска видео на YouTube
async def search_youtube(update: Update, context: CallbackContext):
    query = update.message.text
    if not query:
        await update.message.reply_text("Пожалуйста, укажите название.")
        return

    videos_search = VideosSearch(query, limit=5)  # 5 результатов
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

# Фейковый HTTP сервер для Render
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')  # Ответ для Render

def run_http_server(port):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Starting fake HTTP server on port {port}")
    httpd.serve_forever()

# Основная функция
async def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), search_youtube))

    PORT = int(os.getenv('PORT', 8080))  # Используем PORT из переменных окружения Render
    from threading import Thread
    server_thread = Thread(target=run_http_server, args=(PORT,))
    server_thread.daemon = True
    server_thread.start()  # Запускаем фейковый HTTP сервер

    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
