"""
Constantes e configurações centralizadas do Obsidian Toolkit.
"""

from pathlib import Path

# =============================================================================
# Valores Default
# =============================================================================

DEFAULT_OUTPUT_DIR = str(Path.home())
DEFAULT_WINDOW_WIDTH = 900
DEFAULT_WINDOW_HEIGHT = 700

# =============================================================================
# Extensões Suportadas (Code Converter)
# =============================================================================

SUPPORTED_EXTENSIONS: dict[str, list[str]] = {
    "Python": [".py", ".pyw"],
    "JavaScript": [".js", ".jsx", ".ts", ".tsx"],
    "Java": [".java"],
    "C/C++": [".c", ".cpp", ".cc", ".cxx", ".h", ".hpp"],
    "C#": [".cs"],
    "Web": [".html", ".htm", ".css", ".scss", ".sass", ".less"],
    "Data": [".json", ".xml", ".yaml", ".yml", ".csv"],
    "Config": [".ini", ".conf", ".config", ".toml"],
    "Shell": [".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd"],
    "SQL": [".sql"],
    "Markdown": [".md", ".markdown"],
    "Text": [".txt", ".log"],
    "Others": [".svelte"],
}

# =============================================================================
# Diretórios Excluídos (Code Converter)
# =============================================================================

EXCLUDED_DIRS: set[str] = {
    "node_modules",
    "__pycache__",
    ".venv",
    "dist",
    "build",
    ".vscode",
    "main.js",
    "package-lock.json",
}

# =============================================================================
# Mapeamento Extensão → Linguagem (syntax highlighting)
# =============================================================================

EXTENSION_TO_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".pyw": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".json": "json",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".md": "markdown",
    ".sql": "sql",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "bash",
    ".ps1": "powershell",
    ".bat": "batch",
    ".cmd": "batch",
}

# =============================================================================
# Estilos de Árvore ASCII (Folder Scanner)
# =============================================================================

TREE_STYLES: dict[str, dict[str, str]] = {
    "ascii": {
        "branch": "├── ",
        "last": "└── ",
        "pipe": "│   ",
        "space": "    ",
    },
    "unicode": {
        "branch": "├─ ",
        "last": "└─ ",
        "pipe": "│  ",
        "space": "   ",
    },
    "simple": {
        "branch": "|-- ",
        "last": "`-- ",
        "pipe": "|   ",
        "space": "    ",
    },
}

# =============================================================================
# Filetypes para diálogo de seleção de arquivos (Code Converter)
# =============================================================================

FILE_DIALOG_TYPES = [
    (
        "Todos os arquivos de código",
        "*.py;*.js;*.java;*.c;*.cpp;*.cs;*.html;*.css;*.json;*.xml;*.md;*.txt;*.svelte",
    ),
    ("Python", "*.py;*.pyw"),
    ("JavaScript/TypeScript", "*.js;*.jsx;*.ts;*.tsx"),
    ("Java", "*.java"),
    ("C/C++", "*.c;*.cpp;*.cc;*.cxx;*.h;*.hpp"),
    ("Web", "*.html;*.htm;*.css;*.scss;*.sass"),
    ("Data/Config", "*.json;*.xml;*.yaml;*.yml;*.ini;*.toml"),
    ("Todos os arquivos", "*.*"),
]
