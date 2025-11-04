import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def ban_user_after_delay(context: CallbackContext):
    user_id = context.job.data.get("user_id")
    chat_id = context.job.data.get("chat_id")

    if not user_id or not chat_id:
        logger.error("Не удалось извлечь user_id или chat_id из context.job.data")
        return

    try:
        # Блокируем пользователя
        await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        logger.info(f"Пользователь {user_id} был заблокирован в группе {chat_id}")
    except Exception as e:
        logger.error(f"Ошибка при блокировке пользователя {user_id}: {e}")

async def new_member(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    for user in update.message.new_chat_members:
        user_id = user.id

        context.job_queue.run_once(
            ban_user_after_delay,
            300,
            data={"user_id": user_id, "chat_id": chat_id},
        )
        logger.info(f"Пользователь {user_id} добавлен в очередь на блокировку в группе {chat_id}")

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Бот запущен и готов блокировать новых пользователей через 5 минут.")


async def error(update: Update, context: CallbackContext):
    logger.warning(f'Update {update} caused error {context.error}')

def main():
    application = ApplicationBuilder().token("7798229597:AAEJcMLLiueXrLr8AGopbZq1sLVEzinf2QM").build()

    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))
    application.add_handler(CommandHandler("start", start))

    application.add_error_handler(error)

    application.run_polling()

if __name__ == "__main__":
    main()