import os
import smtplib
import socket
import sys
import locale
import io
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
# Для сложных имен файлов используется библиотека email.utils:
from email.utils import make_msgid, formatdate, formataddr
from email.utils import encode_rfc2231

# Принудительная установка кодировки
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Проверка системной кодировки
if sys.stdout.encoding.lower() != 'utf-8':
    print("Внимание! Системная кодировка может вызвать проблемы с кириллицей.")
    print(f"Текущая кодировка консоли: {locale.getpreferredencoding()}")
    print("Рекомендуется:")
    print("1. Для Windows: изменить кодировку консоли на UTF-8")
    print("2. Использовать IDE с поддержкой UTF-8 (VS Code, PyCharm)")

def get_mime_type(file_path):
    """Определение MIME-типа с использованием стандартной библиотеки"""
    mime_type, encoding = mimetypes.guess_type(file_path)
    return mime_type or 'application/octet-stream'

def send_email():
    # Ввод данных
    sender_email = "AnyFind@yandex.ru" # Почтовый адрес бота
    sender_password = input("Введите пароль приложения для доступа к боту рассылки: ") # Специальный пароль приложения для входа в почту
    smtp_server = "smtp.yandex.ru" # SMTP сервер для взаимодействия с почтой Яндекса
    smtp_port = "587" # Используемый порт для взаимодействия с почтой Яндекса
    
    receiver_email = input("Введите email получателя: ")
    subject = "Письмо от вашего помощника AnyFind"
    body = input("Введите текст письма (при использовании приложения заполняется автоматически): ")
    file_paths = input("Введите пути к файлам через запятую (оставьте пустым если без вложений): ").split(',')
    
    # Формирование письма
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    # Добавление текста с подписью
    full_body = f"{body}\n\n--\n Письмо сформировано ботом AnyFind"
    msg.attach(MIMEText(full_body, 'plain'))
    
    # Добавление вложений
    for file_path in file_paths:
        file_path = file_path.strip()
        if not file_path:
            continue

        if not os.path.isfile(file_path):
            print(f"Ошибка: файл {file_path} не найден!")
            return

        try:
            # Получаем имя файла с кириллицей
            file_name = os.path.basename(file_path)
            
            # Определяем MIME-тип
            mime_type = get_mime_type(file_path)

            # Читаем файл в бинарном режиме
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Создаем MIME-часть
            part = MIMEApplication(file_data, Name=file_name)
            
            # Кодируем имя файла для заголовков
            encoded_name = encode_rfc2231(file_name, charset='utf-8')
            
            # Устанавливаем заголовки
            part['Content-Disposition'] = f'attachment; filename*=\'\'{encoded_name}'
            part.add_header('Content-Type', mime_type, name=encoded_name)
            
            msg.attach(part)

        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {str(e)}")
            return
    
    server = None
    try:
        # Явное указание протокола в зависимости от порта
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(
                host=smtp_server, 
                port=smtp_port,
                timeout=60  # Указание таймаута
            )
        else:
            server = smtplib.SMTP(
                host=smtp_server, 
                port=smtp_port,
                timeout=60  # Указание таймаута
            )
            server.starttls()  # Принудительный STARTTLS для порта 587

        # Включение debug-режима для просмотра обмена с сервером
        server.set_debuglevel(1)
        
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Письмо успешно отправлено!")

    # Исключения в случае ошибок и вывод сообщения для пользователя
    except (socket.timeout, smtplib.SMTPServerDisconnected) as e:
        print(f"Сервер разорвал соединение. Проверьте:\n"
              f"1. Правильность порта\n"
              f"2. Наличие интернет-соединения\n"
              f"3. Не блокирует ли фаервол/антивирус подключение\n"
              f"Ошибка: {str(e)}")
    except socket.gaierror as e:
        print(f"Ошибка подключения: Проверьте правильность SMTP-сервера и порта. ({str(e)})")
    except smtplib.SMTPException as e:
        print(f"Ошибка SMTP: {str(e)}")
    except Exception as e:
        print(f"Неожиданная ошибка: {str(e)}")
    finally:
        if server is not None:
            try:
                server.quit()
            except:
                pass

if __name__ == "__main__":
    send_email()