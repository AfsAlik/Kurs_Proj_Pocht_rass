# Провверка SMTP на отклик
import socket
try:
    print(socket.gethostbyname('smtp.yandex.ru'))  # Должен вернуть IP-адрес
except:
    print("Ошибка DNS. Проверьте интернет-соединение")