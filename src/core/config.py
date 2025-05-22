# Конфигурация приложения
APP_NAME = "SUPLAUNCHER"
APP_VERSION = "3.2.0"
APP_AUTHOR = "VillaDeSUP Team"

# Основная цветовая палитра
COLORS = {
    "bg_primary": "#121212",
    "bg_secondary": "#1E1E1E",
    "bg_tertiary": "#252525",
    "accent_primary": "#0A84FF",
    "accent_secondary": "#5E5CE6",
    "accent_success": "#30D158",
    "accent_warning": "#FF9F0A",
    "accent_error": "#FF453A",
    "text_primary": "#FFFFFF",
    "text_secondary": "#ABABAB",
    "text_disabled": "#757575",
    "border_light": "#333333",
    "overlay": "rgba(0, 0, 0, 0.5)",
}

# Размеры UI
UI = {
    "window_min_width": 980,
    "window_min_height": 650,
    "window_default_width": 1080,
    "window_default_height": 720,
    "sidebar_width": 240,
    "title_bar_height": 40,
    "card_width": 220,
    "card_height": 320,
    "button_height": 48,
    "border_radius": 8,
    "spacing_small": 8,
    "spacing_medium": 16,
    "spacing_large": 24,
    "padding_small": 8,
    "padding_medium": 16,
    "padding_large": 24,
}

# Шрифты
FONTS = {
    "primary": "Inter",
    "secondary": "Montserrat",
    "accent": "Rajdhani",
    "sizes": {
        "xs": 10,
        "small": 12,
        "normal": 14,
        "large": 16,
        "xl": 18,
        "xxl": 24,
        "header": 32,
    }
}

# Анимации
ANIMATIONS = {
    "duration_short": 150,
    "duration_medium": 250,
    "duration_long": 350,
    "easing": "OutCubic",
}

# Игровые параметры по умолчанию
DEFAULT_GAME_SETTINGS = {
    "min_ram": 2048,  # MB
    "max_ram": 4096,  # MB
    "java_args": "-XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M",
    "game_directory": "",  # Автозаполнение
    "resolution_width": 854,
    "resolution_height": 480,
    "fullscreen": False,
}

# Настройки лаунчера по умолчанию
DEFAULT_LAUNCHER_SETTINGS = {
    "close_on_launch": False,
    "keep_launcher_open": True,
    "check_updates": True,
    "enable_animations": True,
    "enable_sounds": True,
    "language": "auto",  # auto, en, ru, и т.д.
    "theme": "dark",
}
