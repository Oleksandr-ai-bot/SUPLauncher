# SUPLAUNCHER

Современный Minecraft лаунчер с минималистичным дизайном и темной темой.

![SUPLAUNCHER Logo](assets/images/logo.png)

## 🚀 Особенности

- **Современный дизайн**: Темная тема с плавными анимациями
- **Поддержка модов**: Интеграция с Forge, Fabric и Quilt
- **Управление профилями**: Создание и настройка множественных профилей
- **Безопасность**: Поддержка оффлайн и онлайн аккаунтов
- **Производительность**: Оптимизированный интерфейс и быстрый запуск
- **Кроссплатформенность**: Работает на Windows, macOS и Linux

## 📋 Системные требования

### Минимальные требования
- **ОС**: Windows 7 SP1+ / macOS 10.13+ / Ubuntu 18.04+
- **Процессор**: 1 ГГц, 2 ядра
- **ОЗУ**: 2 ГБ
- **Графика**: Любая с поддержкой OpenGL 2.0+
- **Место на диске**: 200 МБ для лаунчера
- **Python**: 3.9+ (для запуска из исходного кода)

### Рекомендуемые требования
- **ОС**: Windows 10/11 / macOS 12+ / Ubuntu 20.04+
- **Процессор**: 2 ГГц+, 4+ ядер
- **ОЗУ**: 8 ГБ+
- **Место на диске**: 10 ГБ для игры и модов

## 🔧 Установка

### Из релиза (рекомендуется)
1. Скачайте последний релиз с [GitHub Releases](https://github.com/yourusername/suplauncher/releases)
2. Распакуйте архив
3. Запустите `SUPLAUNCHER.exe` (Windows) или `SUPLAUNCHER` (Linux/macOS)

### Из исходного кода
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/suplauncher.git
   cd suplauncher
   ```

2. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Запустите лаунчер:
   ```bash
   python main.py
   ```

## 🎮 Использование

### Первый запуск
1. При первом запуске лаунчер автоматически создаст профиль SUPMINE
2. Выберите профиль и нажмите кнопку "ИГРАТЬ"
3. Дождитесь загрузки всех необходимых файлов

### Управление профилями
- **Создание**: Перейдите в раздел "Профили" → "Создать профиль"
- **Редактирование**: Нажмите на кнопку редактирования в карточке профиля
- **Удаление**: Нажмите на кнопку удаления в карточке профиля

### Настройки
- **Память**: Настройте выделяемую для игры память в настройках Java
- **Разрешение**: Установите желаемое разрешение экрана игры
- **Директории**: Выберите пользовательские пути для игры и Java

## 📁 Структура проекта

```
suplauncher/
├── src/                    # Исходный код
│   ├── core/              # Ядро приложения
│   ├── models/            # Модели данных
│   ├── ui/                # Пользовательский интерфейс
│   ├── controllers/       # Контроллеры
│   └── services/          # Сервисы
├── assets/                # Ресурсы
│   ├── fonts/            # Шрифты
│   ├── icons/            # Иконки
│   ├── images/           # Изображения
│   └── sounds/           # Звуки
├── main.py               # Точка входа
└── requirements.txt      # Зависимости
```

## 🛠️ Разработка

### Настройка среды разработки
1. Установите зависимости для разработки:
   ```bash
   pip install -r requirements.txt
   pip install black isort mypy pytest pytest-qt
   ```

2. Настройте Git hooks (опционально):
   ```bash
   pre-commit install
   ```

### Сборка исполняемого файла
```bash
# Windows
pyinstaller --name=SUPLAUNCHER --windowed --icon=assets/icons/app_icon.ico --add-data "assets;assets" main.py

# macOS
pyinstaller --name=SUPLAUNCHER --windowed --icon=assets/icons/app_icon.icns --add-data "assets:assets" main.py

# Linux
pyinstaller --name=SUPLAUNCHER --windowed --add-data "assets:assets" main.py
```

### Код-стайл
Проект использует:
- **Black** для форматирования кода
- **isort** для сортировки импортов
- **mypy** для проверки типов

Запуск проверок:
```bash
black .
isort .
mypy src/
```

## 🎨 Дизайн

### Цветовая палитра
- **Основной фон**: `#121212`
- **Вторичный фон**: `#1E1E1E`
- **Акцентный цвет**: `#0A84FF`
- **Текст**: `#FFFFFF` / `#ABABAB`

### Шрифты
- **Основной**: Inter
- **Заголовки**: Montserrat
- **Акценты**: Rajdhani

## 🤝 Участие в разработке

Мы приветствуем вклад в развитие проекта! 

### Как помочь:
1. Fork репозитория
2. Создайте ветку для вашей функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте изменения (`git push origin feature/amazing-feature`)
5. Создайте Pull Request

### Рекомендации:
- Следуйте стилю кода проекта
- Добавляйте тесты для новой функциональности
- Обновляйте документацию при необходимости
- Используйте осмысленные сообщения коммитов

## 🐛 Сообщения об ошибках

Если вы обнаружили ошибку:
1. Проверьте [открытые issues](https://github.com/yourusername/suplauncher/issues)
2. Создайте новый issue с подробным описанием
3. Приложите логи из папки `logs/`
4. Укажите версию лаунчера и операционной системы

## 📜 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.

## 🔗 Полезные ссылки

- **Официальный сайт**: [villadesup.ru](https://villadesup.ru)
- **Discord сервер**: [Присоединиться](https://discord.gg/yourinvite)
- **Документация**: [Wiki](https://github.com/yourusername/suplauncher/wiki)
- **Релизы**: [GitHub Releases](https://github.com/yourusername/suplauncher/releases)

## 🙏 Благодарности

- [minecraft-launcher-lib](https://github.com/JakobDev/minecraft-launcher-lib) - за отличную библиотеку для работы с Minecraft
- [PySide6](https://www.qt.io/qt-for-python) - за мощный UI фреймворк
- Сообществу Minecraft за вдохновение

## 📞 Поддержка

Если у вас есть вопросы или нужна помощь:
- Создайте [issue на GitHub](https://github.com/yourusername/suplauncher/issues)
- Напишите на email: support@villadesup.ru
- Присоединяйтесь к нашему Discord серверу

---

**SUPLAUNCHER** - создан с ❤️ командой SUP Team

<!-- Документация подготовлена специально для Юра -->
