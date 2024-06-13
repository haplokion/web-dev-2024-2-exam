from argon2 import low_level
from hashlib import blake2b, md5

def get_hash(login, password):
    login = bytes(login, 'utf-8')
    password = bytes(password, 'utf-8')

    #Соль формируется как хэш от логина и не хранится в ДБ
    salt = blake2b(login).hexdigest()
    #Преобразуется в байты
    salt = bytes.fromhex(salt)

    #Хэш пароля длиной 16 байт = 32 HEX символа, мешается с солью
    password_hash = low_level.hash_secret_raw(hash_len=16, salt=salt, time_cost=12, memory_cost=65536, parallelism=4, secret=password, type=low_level.Type.D)
    password_hash = password_hash.hex()
    return password_hash

def get_md5(file):
    file_hash = md5(file).hexdigest()
    return file_hash