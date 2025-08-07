"""UI Styles for the application."""
from importlib import resources
from functools import lru_cache


@lru_cache(maxsize=1)
def get_stylesheet():
    """
    Genera la hoja de estilos para la aplicación, usando caché para mejorar rendimiento.
    """
    with resources.path("delayed_shutdown.ui.images", "unchecked.svg") as unchecked_path:
        unchecked_path_str = str(unchecked_path).replace("\\", "/")
    with resources.path("delayed_shutdown.ui.images", "checked.svg") as checked_path:
        checked_path_str = str(checked_path).replace("\\", "/")

    return f"""
        QListWidget {{
            outline: 0;
            border: 1px solid #3a3a3a;
            background-color: #2a2a2a;
            color: #e0e0e0;
        }}
        QListWidget::item {{
            padding: 5px;
            border-bottom: 1px solid #333333;
        }}
        QListWidget::item:selected {{
            background-color: #4a4a4a;
            border: none;
        }}
        QListWidget::indicator {{
            width: 20px;
            height: 20px;
        }}
        QListWidget::indicator:unchecked {{
            image: url({unchecked_path_str});
        }}
        QListWidget::indicator:checked {{
            image: url({checked_path_str});
        }}
        
        QPushButton {{
            padding: 8px;
            border-radius: 4px;
            border: none;
            background-color: #3a3a3a;
            color: white;
        }}
        QPushButton:hover {{
            background-color: #4a4a4a;
        }}
        QPushButton:pressed {{
            background-color: #2a2a2a;
        }}
        QSpinBox {{
            background-color: #2a2a2a;
            color: #e0e0e0;
            border: 1px solid #3a3a3a;
            padding: 2px;
        }}
    """
