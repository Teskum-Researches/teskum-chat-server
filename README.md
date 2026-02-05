# Сервер для Teskum чата

## Базовая настройка

- Параметры сервера находятся в `config.py`.
- Если нужен доступ снаружи localhost — настройте `is_local = False` и `host = "0.0.0.0"`.

## Шифрование сообщений в БД

Сообщения в SQLite (`messages.content`) шифруются через `Fernet` (AES-256 GCM).

Для production задайте ключ в переменной окружения:

```bash
export CHAT_DB_ENCRYPTION_KEY='<ваш urlsafe base64 ключ Fernet>'
```

Сгенерировать ключ можно так:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Шифрование при передаче (transport encryption)

Шифрование в БД **не шифрует трафик** между клиентом и сервером. Для этого нужен `wss://` (TLS):

- `is_secure = True`
- корректные `cert_file` и `cert_key`

Дополнительно включена защита: чувствительные команды `login`, `register`, `send`
по умолчанию запрещены через `ws://` и требуют `wss://` (`require_secure_transport_for_sensitive_commands = True`).

## Клиент

CLI-клиент находится в отдельном репозитории: https://github.com/Teskum-Researches/CLIent
