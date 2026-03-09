"""
Obsidian Toolkit Launcher - Menu para escolher a ferramenta.

Uso: python -m AIContext_toolkit
"""

import sys
import tkinter as tk
from tkinter import ttk

from .utils import center_window


LAUNCHER_WIDTH = 500
LAUNCHER_HEIGHT = 350


def launch_folder_scanner() -> None:
    """Abre o Folder Scanner em nova janela."""
    from .folder_scanner import ObsidianFolderScanner

    app = ObsidianFolderScanner()
    app.run()


def launch_code_converter() -> None:
    """Abre o Code to Markdown Converter em nova janela."""
    from .code_converter import CodeToMarkdownConverter

    app = CodeToMarkdownConverter()
    app.run()


def main() -> None:
    """Launcher principal com menu para escolher a ferramenta."""
    try:
        if sys.platform.startswith("win"):
            import locale
            locale.setlocale(locale.LC_ALL, "")
    except Exception:
        pass

    root = tk.Tk()
    root.title("🧰 AIContext Toolkit")
    root.geometry(f"{LAUNCHER_WIDTH}x{LAUNCHER_HEIGHT}")
    root.resizable(False, False)

    style = ttk.Style()
    style.theme_use("clam")

    center_window(root, LAUNCHER_WIDTH, LAUNCHER_HEIGHT)

    # Frame principal
    main_frame = ttk.Frame(root, padding="30")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Título
    ttk.Label(
        main_frame,
        text="🧰 AIContext Toolkit",
        font=("Arial", 20, "bold"),
    ).pack(pady=(0, 5))

    ttk.Label(
        main_frame,
        text="Escolha uma ferramenta para iniciar",
        font=("Arial", 11),
    ).pack(pady=(0, 30))

    # Botões
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(fill=tk.X)

    def open_scanner() -> None:
        root.destroy()
        launch_folder_scanner()

    def open_converter() -> None:
        root.destroy()
        launch_code_converter()

    # Botão Scanner
    scanner_frame = ttk.Frame(buttons_frame)
    scanner_frame.pack(fill=tk.X, pady=(0, 15))

    scanner_btn = ttk.Button(
        scanner_frame,
        text="📁  Folder Structure Scanner",
        command=open_scanner,
        style="Accent.TButton",
    )
    scanner_btn.pack(fill=tk.X, ipady=12)

    ttk.Label(
        scanner_frame,
        text="Gera árvore ASCII da estrutura de pastas",
        font=("Arial", 9),
        foreground="gray",
    ).pack(anchor=tk.W, padx=5, pady=(3, 0))

    # Botão Converter
    converter_frame = ttk.Frame(buttons_frame)
    converter_frame.pack(fill=tk.X, pady=(0, 15))

    converter_btn = ttk.Button(
        converter_frame,
        text="🔧  Code to Markdown Converter",
        command=open_converter,
        style="Accent.TButton",
    )
    converter_btn.pack(fill=tk.X, ipady=12)

    ttk.Label(
        converter_frame,
        text="Combina múltiplos arquivos de código em Markdown para AI/LLM",
        font=("Arial", 9),
        foreground="gray",
    ).pack(anchor=tk.W, padx=5, pady=(3, 0))

    # Versão
    ttk.Label(
        main_frame,
        text="v1.0.0",
        font=("Arial", 8),
        foreground="gray",
    ).pack(side=tk.BOTTOM, anchor=tk.E)

    root.mainloop()


if __name__ == "__main__":
    main()
