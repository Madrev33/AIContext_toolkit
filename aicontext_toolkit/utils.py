"""
Funções utilitárias compartilhadas do Obsidian Toolkit.
"""

import tkinter as tk

from pathlib import Path

import charset_normalizer


def format_file_size(size_bytes: int) -> str:
    """Formata tamanho de arquivo para leitura humana."""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def format_file_size_short(file_path: str) -> str:
    """Retorna o tamanho de um arquivo formatado de forma curta."""
    try:
        size = Path(file_path).stat().st_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    except Exception:
        return "? B"


def detect_encoding(file_path: str, method: str = "auto") -> str:
    """Detecta a codificação de um arquivo.

    Args:
        file_path: Caminho absoluto do arquivo.
        method: 'auto' para detecção automática, ou encoding específico.

    Returns:
        String com o nome do encoding detectado.
    """
    if method != "auto":
        return method

    try:
        # charset_normalizer consegue ler do path direto e tem detecção mais rápida 
        result = charset_normalizer.from_path(file_path).best()
        if result and result.encoding:
            return result.encoding
        return "utf-8"
    except Exception:
        return "utf-8"


def center_window(root: tk.Tk, width: int, height: int) -> None:
    """Centraliza uma janela tkinter na tela.

    Args:
        root: Janela principal do tkinter.
        width: Largura da janela em pixels.
        height: Altura da janela em pixels.
    """
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
