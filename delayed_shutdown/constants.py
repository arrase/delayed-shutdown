from importlib import resources

# --- Constants ---
APP_TITLE = "Automatic Process-based Shutdown"
MONITORING_INTERVAL_SECONDS = 10
MAX_INTERVAL_SECONDS = 3600

# --- Colors and Styles ---
STYLE_BTN_START = "background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;"
STYLE_BTN_CANCEL = "background-color: #f44336; color: white; font-weight: bold; padding: 10px;"

def get_stylesheet():
    with resources.path("delayed_shutdown.images", "unchecked.svg") as unchecked_path:
        unchecked_path_str = str(unchecked_path).replace("\\", "/")
    with resources.path("delayed_shutdown.images", "checked.svg") as checked_path:
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
    """
