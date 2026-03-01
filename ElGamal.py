import random
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

TOKEN = "tokenBotTG"

P, G, A, MESSAGE, K = range(5)

letter_to_bin = {
    'А': '00000', 'Б': '00001', 'В': '00010', 'Г': '00011',
    'Д': '00100', 'Е': '00101', 'Ж': '00110', 'З': '00111',
    'И': '01000', 'Й': '01001', 'К': '01010', 'Л': '01011',
    'М': '01100', 'Н': '01101', 'О': '01110', 'П': '01111',
    'Р': '10000', 'С': '10001', 'Т': '10010', 'У': '10011',
    'Ф': '10100', 'Х': '10101', 'Ц': '10110', 'Ч': '10111',
    'Ш': '11000', 'Щ': '11001', 'Ъ': '11010', 'Ы': '11011',
    'Ь': '11100', 'Э': '11101', 'Ю': '11110', 'Я': '11111'
}

bin_to_letter = {v: k for k, v in letter_to_bin.items()}


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0 and n != 2:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def find_primitive_root(p):
    required = set(range(1, p))
    for g in range(2, p):
        actual = set(pow(g, i, p) for i in range(1, p))
        if actual == required:
            return g
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите простое число p (или auto):")
    return P


async def get_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text.lower() == "auto":
        while True:
            candidate = random.randint(100, 500)
            if is_prime(candidate):
                context.user_data["p"] = candidate
                break
        await update.message.reply_text(f"Сгенерировано p = {candidate}")
    else:
        try:
            p = int(text)
            if not is_prime(p):
                await update.message.reply_text("p должно быть простым:")
                return P
            context.user_data["p"] = p
        except ValueError:
            await update.message.reply_text("Введите целое число или 'auto':")
            return P

    await update.message.reply_text("Введите примитивный элемент g (или auto):")
    return G


async def get_g(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = context.user_data["p"]
    text = update.message.text

    if text.lower() == "auto":
        g = find_primitive_root(p)
        if g is None:
            await update.message.reply_text(
                "Не удалось найти примитивный корень.")
            return G
        context.user_data["g"] = g
        await update.message.reply_text(f"Сгенерировано g = {g}")
    else:
        try:
            g = int(text)
            if g >= p:
                await update.message.reply_text(f"g должно быть меньше p={p}. Введите снова:")
                return G
            context.user_data["g"] = g
        except ValueError:
            await update.message.reply_text("Введите целое число или 'auto':")
            return G

    await update.message.reply_text("Введите секретный ключ a (или auto):")
    return A


async def get_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = context.user_data["p"]
    text = update.message.text

    if text.lower() == "auto":
        a = random.randint(2, p - 2)
        context.user_data["a"] = a
        await update.message.reply_text(f"Сгенерировано a = {a}")
    else:
        try:
            a = int(text)
            if not (1 < a < p - 1):
                await update.message.reply_text(f"a должно быть в диапазоне (1, {p - 1})")
                return A
            context.user_data["a"] = a
        except ValueError:
            await update.message.reply_text("Ошибка! Введите целое число или 'auto':")
            return A

    await update.message.reply_text("Введите сообщение (буквы без пробелов):")
    return MESSAGE


async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.upper()

    if any(ch not in letter_to_bin for ch in text):
        await update.message.reply_text("Введите снова (только буквы без пробелов):")
        return MESSAGE

    if len(text) == 0:
        await update.message.reply_text("Сообщение не может быть пустым. Введите снова:")
        return MESSAGE

    context.user_data["message"] = text
    p = context.user_data["p"]
    await update.message.reply_text(f"Введите случайное число k (1 < k < {p - 1}) или auto:")
    return K


async def get_k(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = context.user_data["p"]
    text = update.message.text

    if text.lower() == "auto":
        k = random.randint(2, p - 2)
        context.user_data["k"] = k
        await update.message.reply_text(f"Сгенерировано k = {k}")
    else:
        try:
            k = int(text)
            if not (1 < k < p - 1):
                await update.message.reply_text(f"Неверное k. 1 < k < {p - 1}. Введите снова:")
                return K
            context.user_data["k"] = k
        except ValueError:
            await update.message.reply_text("Введите целое число или 'auto':")
            return K

    try:
        result = process_crypto(context.user_data)
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"{str(e)}")
        return ConversationHandler.END

    return ConversationHandler.END


def process_crypto(data):
    p = data["p"]
    g = data["g"]
    a = data["a"]
    k = data["k"]
    text = data["message"]

    y = pow(g, a, p)
    binary_message = ""
    output = "===== Пользователь А =====\n"
    output += f"Простое число p = {p}\n"
    output += f"Примитивный элемент g = {g}\n"
    output += f"Закрытый ключ  a = {a}\n\n"
    output += f"Открытый ключ y = g^a mod p = {g}^{a} mod {p} = {y}\n\n"

    output += "===== Пользователь Б =====\n"
    output += f"Сообщение: {text}\n"
    output += f"k = {k}\n\n"
    output += "Кодирование сообщения:\n"

    for ch in text:
        bin_code = letter_to_bin[ch]
        dec_code = int(bin_code, 2)
        binary_message += bin_code
        output += f"{ch}: двоичное = {bin_code}, десятичное = {dec_code}\n"

    output += f"\nСообщение полностью:\nДвоичное: {binary_message}\n\n"

    y1 = pow(g, k, p)
    yk = pow(y, k, p)
    yk_bin = bin(yk)[2:]

    output += "Пользователь Б вычисляет:\n"
    output += f"y1 = g^k mod p = {g}^{k} mod {p} = {y1}\n"
    output += f"y^k mod p = {y}^{k} mod {p} = {yk}\n"
    output += f"Двоичный ключ: {yk_bin}\n\n"

    L = len(yk_bin)
    if L == 0:
        raise ValueError("Длина двоичного ключа равна 0")

    while len(binary_message) % L != 0:
        binary_message += '0'

    blocks = [binary_message[i:i + L] for i in range(0, len(binary_message), L)]
    cipher_blocks = []

    output += "Шифрование:\n"
    for i, block in enumerate(blocks, 1):
        cipher = ''.join('1' if block[j] != yk_bin[j] else '0' for j in range(L))
        cipher_blocks.append(cipher)
        output += f"y2_{i} = {block} XOR {yk_bin} = {cipher}\n"

    cipher_text = ''.join(cipher_blocks)
    output += f"\nШТ: ({y1}, {cipher_text})\n\n"

    yk_dec = pow(y1, a, p)
    yk_bin_A = bin(yk_dec)[2:]
    output += "===== Пользователь А (Принимает ШТ) =====\n"
    output += f"По формуле m = y_1^a(mod p) XOR y_2\n"
    output += f"y1^a mod p = {y1}^{a} mod {p} = {yk_dec}\n"
    output += f"Двоичный ключ: {yk_bin_A}\n\n"

    # Убедимся, что длина ключа совпадает
    if len(yk_bin_A) != L:
        yk_bin_A = yk_bin_A.zfill(L)
        output += f"Ключ дополнен до длины {L}: {yk_bin_A}\n\n"

    blocks_dec = [cipher_text[i:i + L] for i in range(0, len(cipher_text), L)]
    decrypted = ""

    output += "Расшифрование:\n"
    for i, block in enumerate(blocks_dec, 1):
        m = ''.join('1' if block[j] != yk_bin_A[j] else '0' for j in range(L))
        decrypted += m
        output += f"m_{i} = {yk_bin_A} XOR {block} = {m}\n"

    output += f"\nВосстановленное бинарное сообщение: {decrypted}\n\n"

    blocks5 = [decrypted[i:i + 5] for i in range(0, len(decrypted), 5)]
    decoded = ""

    output += "Декодирование:\n"
    for block in blocks5:
        if block in bin_to_letter:
            decoded += bin_to_letter[block]
            output += f"{block} -> {bin_to_letter[block]}\n"
        else:
            output += f"{block} -> [неизвестный символ]\n"

    output += f"\nВосстановленное сообщение: {decoded}"

    return output


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена. Для начала введите /start")
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            P: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_p)],
            G: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_g)],
            A: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_a)],
            MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_message)],
            K: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_k)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
