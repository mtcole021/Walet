import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from tronpy import Tron
import requests

# توکن ربات تلگرام
TOKEN = "7989787294:AAEvfYAphjhmBh-6bUQEvBuJaW2WDeBynL0"

# آدرس‌های ولت
tron_address = 'TVWuPAYCPGHu4hYfs9dgH9ynxgwcFfS3pz'
ton_address = 'UQC5S1zwtK0Mr2UihzpfXpSAmUCEcLtxt_zLT4UghLZQ-o1d'

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! لطفاً ولت خود را متصل کنید. (ترون یا تون)"
    )

# مدیریت پیام ها
async def handle_wallet_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wallet_link = update.message.text.strip()

    if wallet_link.startswith('T'):  # ترون ولت
        await update.message.reply_text('کیف پول ترون شناسایی شد.')
        context.user_data['wallet'] = wallet_link
        context.user_data['network'] = 'tron'
        await confirm_transaction(update, context)

    elif len(wallet_link) > 40:  # تون ولت
        await update.message.reply_text('کیف پول تون شناسایی شد.')
        context.user_data['wallet'] = wallet_link
        context.user_data['network'] = 'ton'
        await confirm_transaction(update, context)
    else:
        await update.message.reply_text('لطفاً آدرس معتبر ولت وارد کنید.')

# گرفتن موجودی ترون
def get_tron_balance(address):
    tron = Tron()
    balance = tron.get_account_balance(address)
    return balance

# گرفتن موجودی تون
def get_ton_balance(address):
    response = requests.get(f'https://testnet.toncenter.com/api/v2/accounts/{address}')
    if response.status_code == 200:
        data = response.json()
        return int(data.get('result', {}).get('balance', 0)) / 1e9
    return 0

# تایید و انتقال
async def confirm_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wallet = context.user_data.get('wallet')
    network = context.user_data.get('network')

    if network == 'tron':
        balance = get_tron_balance(wallet)
        await update.message.reply_text(f'موجودی ولت ترون: {balance} TRX')

    elif network == 'ton':
        balance = get_ton_balance(wallet)
        await update.message.reply_text(f'موجودی ولت تون: {balance} TON')

# شروع ربات
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet_link))

    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
