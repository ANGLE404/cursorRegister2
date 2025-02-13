import sys
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field
from cursor_account_generator import generate_cursor_account
from cursor_id_resetter import reset
from cursor_auth_updater import process_cookies
from loguru import logger
from dotenv import load_dotenv
import os
from pathlib import Path
from cursor_utils import Utils, Result, error_handler

class UI:
    FONT = ('Microsoft YaHei UI', 10)
    COLORS = {
        'primary': '#2563EB',      # 更现代的蓝色
        'secondary': '#64748B',    # 更柔和的次要色调
        'success': '#059669',      # 清新的绿色
        'error': '#DC2626',        # 鲜明的红色
        'warning': '#D97706',      # 温暖的橙色
        'bg': '#F8FAFC',          # 更亮的背景色
        'card_bg': '#FFFFFF',     # 保持白色卡片背景
        'disabled': '#94A3B8',    # 柔和的禁用色
        'hover': '#1D4ED8',       # 深蓝色悬停效果
        'pressed': '#1E40AF',     # 更深的按下效果
        'border': '#E2E8F0',      # 柔和的边框色
        'input_bg': '#FFFFFF',    # 输入框背景色
        'label_fg': '#334155',    # 更深的标签文字颜色
        'title_fg': '#1E40AF',    # 标题使用深蓝色
        'subtitle_fg': '#475569'   # 柔和的副标题色
    }

    @staticmethod
    def setup_styles() -> None:
        style = ttk.Style()
        base_style = {
            'font': UI.FONT,
            'background': UI.COLORS['bg']
        }
        
        # 主框架样式
        style.configure('TFrame', background=UI.COLORS['bg'])
        
        # 标签框样式
        style.configure('TLabelframe', 
            background=UI.COLORS['card_bg'],
            padding=25,  # 增加内边距
            relief='flat',
            borderwidth=1
        )
        
        # 标签框标题样式
        style.configure('TLabelframe.Label', 
            font=(UI.FONT[0], 12, 'bold'),  # 增大字体
            foreground=UI.COLORS['title_fg'],
            padding=(0, 8)  # 调整标题边距
        )
        
        # 按钮样式
        style.configure('Custom.TButton',
            font=(UI.FONT[0], 10, 'bold'),  # 增大字体
            padding=(25, 10),  # 增加按钮内边距
            background=UI.COLORS['primary'],
            foreground='black',  # 改为黑色字体
            borderwidth=0,
            relief='flat'
        )
        
        # 按钮悬停和点击效果
        style.map('Custom.TButton',
            background=[
                ('pressed', UI.COLORS['pressed']),
                ('active', UI.COLORS['hover']),
                ('disabled', UI.COLORS['disabled'])
            ],
            foreground=[
                ('pressed', 'black'),  # 改为黑色字体
                ('active', 'black'),   # 改为黑色字体
                ('disabled', '#94A3B8')
            ]
        )
        
        # 输入框样式
        style.configure('TEntry',
            padding=12,  # 增加内边距
            relief='flat',
            borderwidth=1,
            selectbackground=UI.COLORS['primary'],
            selectforeground='white',
            fieldbackground=UI.COLORS['input_bg']
        )
        
        # 标签样式
        style.configure('TLabel',
            font=(UI.FONT[0], 10),  # 增大字体
            background=UI.COLORS['card_bg'],
            foreground=UI.COLORS['label_fg'],
            padding=(8, 4)  # 增加边距
        )
        
        # 特殊标签样式
        label_styles = {
            'Info.TLabel': {
                'foreground': UI.COLORS['subtitle_fg'],
                'font': (UI.FONT[0], 10),
                'background': UI.COLORS['card_bg']
            },
            'Error.TLabel': {
                'foreground': UI.COLORS['error'],
                'font': (UI.FONT[0], 10),
                'background': UI.COLORS['card_bg']
            },
            'Success.TLabel': {
                'foreground': UI.COLORS['success'],
                'font': (UI.FONT[0], 10),
                'background': UI.COLORS['card_bg']
            },
            'Footer.TLabel': {
                'font': (UI.FONT[0], 9),
                'foreground': UI.COLORS['subtitle_fg'],
                'background': UI.COLORS['bg']
            },
            'Title.TLabel': {
                'font': (UI.FONT[0], 14, 'bold'),  # 增大标题字体
                'foreground': UI.COLORS['title_fg'],
                'background': UI.COLORS['bg']
            }
        }
        
        for name, config in label_styles.items():
            style.configure(name, **{**base_style, **config})

    @staticmethod
    def create_labeled_entry(parent, label_text: str, row: int, **kwargs) -> ttk.Entry:
        frame = ttk.Frame(parent, style='TFrame')
        frame.grid(row=row, column=0, columnspan=2, sticky='ew', padx=15, pady=8)
        
        label = ttk.Label(frame, text=f"{label_text}:", style='Info.TLabel')
        label.pack(side=tk.LEFT, padx=(5, 15))
        
        entry = ttk.Entry(frame, style='TEntry', **kwargs)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        return entry

    @staticmethod
    def create_labeled_frame(parent, title: str, padding: str = "20", **kwargs) -> ttk.LabelFrame:
        frame = ttk.LabelFrame(
            parent,
            text=title,
            padding=padding,
            style='TLabelframe',
            **kwargs
        )
        frame.pack(fill=tk.X, padx=20, pady=10)
        frame.columnconfigure(1, weight=1)
        return frame

    @staticmethod
    def center_window(window, width: int, height: int) -> None:
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    @staticmethod
    def show_message(window: tk.Tk, title: str, message: str, msg_type: str) -> None:
        window.bell()
        getattr(messagebox, msg_type)(title, message)
        log_level = 'error' if msg_type == 'showerror' else 'warning' if msg_type == 'showwarning' else 'info'
        getattr(logger, log_level)(message)

    @staticmethod
    def show_error(window: tk.Tk, title: str, error: Exception) -> None:
        UI.show_message(window, "错误", f"{title}: {str(error)}", 'showerror')

    @staticmethod
    def show_success(window: tk.Tk, message: str) -> None:
        UI.show_message(window, "成功", message, 'showinfo')

    @staticmethod
    def show_warning(window: tk.Tk, message: str) -> None:
        UI.show_message(window, "警告", message, 'showwarning')

@dataclass
class WindowConfig:
    width: int = 600
    height: int = 700
    title: str = "Cursor账号管理工具"
    backup_dir: str = "env_backups"
    max_backups: int = 10
    env_vars: List[Tuple[str, str]] = field(default_factory=lambda: [
        ('DOMAIN', '域名'), ('EMAIL', '邮箱'), ('PASSWORD', '密码')
    ])
    buttons: List[Tuple[str, str]] = field(default_factory=lambda: [
        ("生成账号", "generate_account"),
        ("自动注册", "auto_register"),
        ("重置ID", "reset_ID"),
        ("更新账号信息", "update_auth")
    ])

class CursorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.config = WindowConfig()
        self.entries: Dict[str, ttk.Entry] = {}
        
        self.root.title(self.config.title)
        UI.center_window(self.root, self.config.width, self.config.height)
        self.root.resizable(False, False)
        self.root.configure(bg=UI.COLORS['bg'])
        if os.name == 'nt':
            self.root.attributes('-alpha', 0.98)
            
        UI.setup_styles()
        self.setup_ui()

    def setup_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding="20", style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text=self.config.title,
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 15))
        
        # 账号信息框
        account_frame = UI.create_labeled_frame(main_frame, "账号信息")
        for row, (var_name, label_text) in enumerate(self.config.env_vars):
            entry = UI.create_labeled_entry(account_frame, label_text, row)
            if os.getenv(var_name):
                entry.insert(0, os.getenv(var_name))
            self.entries[var_name] = entry

        # Cookie设置框
        cookie_frame = UI.create_labeled_frame(main_frame, "Cookie设置")
        self.entries['cookie'] = UI.create_labeled_entry(cookie_frame, "Cookie", 0)
        self.entries['cookie'].insert(0, "WorkosCursorSessionToken")

        # 按钮区域
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(fill=tk.X, pady=20)
        
        # 创建两行按钮
        for i, (text, command) in enumerate(self.config.buttons):
            row = i // 2
            col = i % 2
            btn = ttk.Button(
                button_frame,
                text=text,
                command=getattr(self, command),
                style='Custom.TButton'
            )
            btn.grid(row=row, column=col, padx=8, pady=6, sticky='ew')
        
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        # 页脚
        footer = ttk.Label(
            main_frame,
            text="powered by kto 仅供学习使用",
            style='Footer.TLabel'
        )
        footer.pack(side=tk.BOTTOM, pady=(0, 0))

    def _save_env_vars(self, updates: Dict[str, str] = None) -> None:
        if not updates:
            updates = {
                var_name: value.strip()
                for var_name, _ in self.config.env_vars
                if (value := self.entries[var_name].get().strip())
            }
        
        if updates and not Utils.update_env_vars(updates):
            UI.show_warning(self.root, "保存环境变量失败")

    def backup_env_file(self) -> None:
        env_path = Utils.get_path('env')
        if not env_path.exists():
            raise Exception(f"未找到.env文件: {env_path}")

        backup_dir = Path(self.config.backup_dir)
        if not Utils.backup_file(env_path, backup_dir, '.env', self.config.max_backups):
            raise Exception("备份文件失败")

    @error_handler
    def generate_account(self) -> None:
        self.backup_env_file()
        
        if domain := self.entries['DOMAIN'].get().strip():
            if not Utils.update_env_vars({'DOMAIN': domain}):
                raise RuntimeError("保存域名失败")
            load_dotenv(override=True)

        if not (result := generate_cursor_account()):
            raise RuntimeError(result.message)
            
        email, password = result.data if isinstance(result, Result) else result
        for key, value in {'EMAIL': email, 'PASSWORD': password}.items():
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, value)
            
        UI.show_success(self.root, "账号生成成功")
        self._save_env_vars()

    @error_handler
    def reset_ID(self) -> None:
        if not (result := reset()):
            raise Exception(result.message)
        UI.show_success(self.root, result.message)
        self._save_env_vars()

    @error_handler
    def update_auth(self) -> None:
        cookie_str = self.entries['cookie'].get().strip()
        if not cookie_str:
            UI.show_warning(self.root, "请输入Cookie字符串")
            return

        if "WorkosCursorSessionToken=" not in cookie_str:
            UI.show_warning(self.root, "Cookie字符串格式不正确，必须包含 WorkosCursorSessionToken")
            return

        self.backup_env_file()
        if not (result := process_cookies(cookie_str)):
            raise Exception(result.message)
            
        UI.show_success(self.root, result.message)
        self.entries['cookie'].delete(0, tk.END)
        self._save_env_vars()

    @error_handler
    def auto_register(self) -> None:
        self._save_env_vars()
        load_dotenv(override=True)
        
        from cursor_registerAc import CursorRegistration
        registrar = CursorRegistration()
        
        def wait_for_user(message: str):
            dialog = tk.Toplevel(self.root)
            dialog.title("等待确认")
            dialog.geometry("300x150")
            UI.center_window(dialog, 300, 150)
            dialog.transient(self.root)
            dialog.grab_set()
            
            ttk.Label(
                dialog,
                text=message,
                wraplength=250,
                justify="center",
                style="TLabel"
            ).pack(pady=20)
            
            def on_continue():
                dialog.grab_release()
                dialog.destroy()
                
            ttk.Button(
                dialog,
                text="继续",
                command=on_continue,
                style="Custom.TButton"
            ).pack(pady=10)
            
            dialog.wait_window()
        
        try:
            registrar.init_browser()
            registrar.fill_registration_form()
            wait_for_user("请在浏览器中点击按钮，完成后点击继续...")
            registrar.fill_password()
            wait_for_user("请在浏览器中完成注册和验证码验证，完成后点击继续...")
            registrar.get_user_info()
            token = registrar.get_cursor_token()
            
            if token:
                self.entries['cookie'].delete(0, tk.END)
                self.entries['cookie'].insert(0, f"WorkosCursorSessionToken={token}")
                UI.show_success(self.root, "自动注册成功，Token已填入")
            else:
                UI.show_warning(self.root, "获取Token失败")
        finally:
            if registrar.browser:
                registrar.browser.quit()

def setup_logging() -> None:
    logger.remove()
    logger.add(
        sink=Path("./cursorRegister_log") / "{time:YYYY-MM-DD_HH}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} |{level:8}| - {message}",
        rotation="10 MB",
        retention="14 days",
        compression="gz",
        enqueue=True,
        backtrace=True,
        diagnose=True,
        level="DEBUG"
    )
    logger.add(
        sink=sys.stderr,
        colorize=True,
        enqueue=True,
        backtrace=True,
        diagnose=True,
        level="DEBUG"
    )

def main() -> None:
    try:
        load_dotenv(dotenv_path=Utils.get_path('env'))
        setup_logging()
        root = tk.Tk()
        app = CursorApp(root)
        root.mainloop()
    except Exception as e:
        logger.error(f"程序启动失败: {e}")
        UI.show_error(root, "程序启动失败", e)

if __name__ == "__main__":
    main()
