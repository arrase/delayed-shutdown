"""UI Styles for the application."""
from importlib import resources


def get_stylesheet():
    """
    Generates the stylesheet for the application, including dynamic paths to icons.
    """
    with resources.path("delayed_shutdown.ui.images", "unchecked.svg") as unchecked_path:
        unchecked_path_str = str(unchecked_path).replace("\\", "/")
    with resources.path("delayed_shutdown.ui.images", "checked.svg") as checked_path:
        checked_path_str = str(checked_path).replace("\\", "/")

    return f"""
        QListWidget {{
            outline: 0;
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

        .start-button {{
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            padding: 10px;
        }}

        .cancel-button {{
            background-color: #f44336;
            color: white;
            font-weight: bold;
            padding: 10px;
        }}
    """
