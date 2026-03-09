"""
AIContext Toolkit - Suite de ferramentas para produtividade.

Inclui:
- ObsidianFolderScanner: Gerador de árvore ASCII da estrutura de pastas
- CodeToMarkdownConverter: Combinador de códigos em Markdown formatado
"""

__version__ = "1.0.0"
__author__ = "ScriptMaster Pro"

from .folder_scanner import ObsidianFolderScanner
from .code_converter import CodeToMarkdownConverter

__all__ = ["ObsidianFolderScanner", "CodeToMarkdownConverter"]
