# ElGamal-cryptosystem
1. **User A** selects a large prime number `p`
2. **User B** selects a primitive element `g` mod `p`
3. **User A** computes the secret key: `y = g^a mod p` (where `a` is private)
4. Public parameters `(p, g, y)` are sent over the open channel

### Message Encoding
Messages in Cyrillic are converted to 5-bit binary representation according to the mapping table:

| Letter | Binary | Letter | Binary | Letter | Binary | Letter | Binary |
|--------|--------|--------|--------|--------|--------|--------|--------|
| А | 00000 | И | 01000 | Р | 10000 | Ш | 11000 |
| Б | 00001 | Й | 01001 | С | 10001 | Щ | 11001 |
| В | 00010 | К | 01010 | Т | 10010 | Ъ | 11010 |
| Г | 00011 | Л | 01011 | У | 10011 | Ы | 11011 |
| Д | 00100 | М | 01100 | Ф | 10100 | Ь | 11100 |
| Е | 00101 | Н | 01101 | Х | 10101 | Э | 11101 |
| Ж | 00110 | О | 01110 | Ц | 10110 | Ю | 11110 |
| З | 00111 | П | 01111 | Ч | 10111 | Я | 11111 |

### Encryption Process (User B)
1. Select a random integer `k` (ephemeral key)
2. Compute `y₁ = g^k mod p`
3. Compute the shared secret: `key = y^k mod p` (where `y` is User A's public key)
4. Convert `key` to binary representation
5. Compute `y₂ = m ⊕ key` (XOR operation)
6. Send ciphertext `(y₁, y₂)` to User A

### Decryption Process (User A)
Upon receiving the ciphertext `(y₁, y₂)`:
1. Compute the shared secret: `s = y₁^a mod p` (using private key `a`)
2. Convert `s` to binary representation
3. Recover the message: `m = y₂ ⊕ s`

# Exmaple
```
===== Пользователь А =====
Простое число p = 397
Примитивный элемент g = 5
Закрытый ключ  a = 349

Открытый ключ y = g^a mod p = 5^349 mod 397 = 262

===== Пользователь Б =====
Сообщение: ТЕСТ
k = 361

Кодирование сообщения:
Т: двоичное = 10010, десятичное = 18
Е: двоичное = 00101, десятичное = 5
С: двоичное = 10001, десятичное = 17
Т: двоичное = 10010, десятичное = 18

Сообщение полностью:
Двоичное: 10010001011000110010

Пользователь Б вычисляет:
y1 = g^k mod p = 5^361 mod 397 = 89
y^k mod p = 262^361 mod 397 = 133
Двоичный ключ: 10000101

Шифрование:
y2_1 = 10010001 XOR 10000101 = 00010100
y2_2 = 01100011 XOR 10000101 = 11100110
y2_3 = 00100000 XOR 10000101 = 10100101

ШТ: (89, 000101001110011010100101)

===== Пользователь А (Принимает ШТ) =====
По формуле m = y_1^a(mod p) XOR y_2
y1^a mod p = 89^349 mod 397 = 133
Двоичный ключ: 10000101

Расшифрование:
m_1 = 10000101 XOR 00010100 = 10010001
m_2 = 10000101 XOR 11100110 = 01100011
m_3 = 10000101 XOR 10100101 = 00100000

Восстановленное бинарное сообщение: 100100010110001100100000

Декодирование:
10010 -> Т
00101 -> Е
10001 -> С
10010 -> Т
0000 -> [неизвестный символ]

Восстановленное сообщение: ТЕСТ
```
