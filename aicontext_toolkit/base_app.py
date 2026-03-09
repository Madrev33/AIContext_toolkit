"""
Classe base com componentes de UI compartilhados entre as ferramentas.

BaseToolkitApp centraliza: janela, output section, progress bar,
status bar, persistência de configurações e diálogo de pasta de destino.
"""

import json
import os
import tkinter as tk
from abc import ABC, abstractmethod
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .config import DEFAULT_OUTPUT_DIR, DEFAULT_WINDOW_HEIGHT, DEFAULT_WINDOW_WIDTH
from .utils import center_window


class BaseToolkitApp(ABC):
    """Classe base abstrata para ferramentas do Obsidian Toolkit.

    Fornece toda a infraestrutura de UI comum:
    - Janela principal com tema
    - Seção de output (pasta de destino + nome do arquivo)
    - Botões de ação (principal, salvar config, sair)
    - Barra de progresso
    - Barra de status
    - Persistência de configurações em JSON
    """

    def __init__(self, title: str, default_filename: str, default_status: str) -> None:
        """Inicializa a aplicação base.

        Args:
            title: Título da janela principal.
            default_filename: Nome padrão do arquivo de saída (sem extensão).
            default_status: Texto inicial da barra de status.
        """
        self._title = title
        self._default_filename = default_filename
        self._default_status = default_status

        self.setup_window()
        self.setup_variables()
        self.setup_ui()
        self.load_settings()

    # =========================================================================
    # Setup da Janela
    # =========================================================================

    def setup_window(self) -> None:
        """Configura a janela principal."""
        self.root = tk.Tk()
        self.root.title(self._title)
        self.root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
        self.root.resizable(True, True)

        try:
            self.root.iconbitmap("icon.ico")
        except Exception:
            pass

        style = ttk.Style()
        style.theme_use("clam")

        center_window(self.root, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

    # =========================================================================
    # Variáveis Base
    # =========================================================================

    def setup_variables(self) -> None:
        """Configura variáveis compartilhadas e chama setup específico."""
        self.output_dir = tk.StringVar(value=DEFAULT_OUTPUT_DIR)
        self.output_filename = tk.StringVar(value=self._default_filename)
        self.last_input_path = DEFAULT_OUTPUT_DIR
        self.setup_tool_variables()

    @abstractmethod
    def setup_tool_variables(self) -> None:
        """Configura variáveis específicas da ferramenta. Implementar na subclasse."""
        ...

    # =========================================================================
    # UI Base
    # =========================================================================

    def setup_ui(self) -> None:
        """Configura a interface do usuário completa."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # UI específica da ferramenta (título, seleção, configs, preview)
        self.setup_tool_ui(main_frame)

        # UI compartilhada (output, botões, progresso, status)
        self.setup_output_section(main_frame)
        self.setup_action_buttons(main_frame)
        self.setup_progress_bar(main_frame)
        self.setup_status_bar()

    @abstractmethod
    def setup_tool_ui(self, parent: ttk.Frame) -> None:
        """Configura UI específica da ferramenta (rows 0-3). Implementar na subclasse."""
        ...

    def setup_output_section(self, parent: ttk.Frame) -> None:
        """Configura a seção de output (pasta de destino + nome do arquivo)."""
        output_frame = ttk.LabelFrame(parent, text="📤 Configurações de Output", padding="10")
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        output_frame.columnconfigure(1, weight=1)

        # Diretório de output
        ttk.Label(output_frame, text="Pasta de destino:").grid(row=0, column=0, sticky=tk.W)
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir, width=50)
        output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(output_frame, text="📁", command=self.select_output_dir, width=3).grid(
            row=0, column=2
        )

        # Nome do arquivo
        ttk.Label(output_frame, text="Nome do arquivo:").grid(
            row=1, column=0, sticky=tk.W, pady=(5, 0)
        )
        filename_entry = ttk.Entry(output_frame, textvariable=self.output_filename, width=30)
        filename_entry.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        ttk.Label(output_frame, text=".md").grid(row=1, column=2, sticky=tk.W, pady=(5, 0))

    def setup_action_buttons(self, parent: ttk.Frame) -> None:
        """Configura os botões de ação."""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=5, column=0, columnspan=3, pady=(20, 10))

        # Botão principal
        main_btn = ttk.Button(
            buttons_frame,
            text=self.get_main_button_text(),
            command=self.start_main_action,
            style="Accent.TButton",
        )
        main_btn.grid(row=0, column=0, padx=(0, 10))

        # Botão salvar configurações
        save_config_btn = ttk.Button(
            buttons_frame, text="💾 Salvar Configurações", command=self.save_settings
        )
        save_config_btn.grid(row=0, column=1, padx=(0, 10))

        # Botão sair
        exit_btn = ttk.Button(buttons_frame, text="❌ Sair", command=self.root.quit)
        exit_btn.grid(row=0, column=2)

    @abstractmethod
    def get_main_button_text(self) -> str:
        """Retorna o texto do botão principal. Implementar na subclasse."""
        ...

    @abstractmethod
    def start_main_action(self) -> None:
        """Ação principal da ferramenta. Implementar na subclasse."""
        ...

    def setup_progress_bar(self, parent: ttk.Frame) -> None:
        """Configura a barra de progresso."""
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(parent, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

    def setup_status_bar(self) -> None:
        """Configura a barra de status."""
        self.status_var = tk.StringVar(value=self._default_status)
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))

    # =========================================================================
    # Diálogos
    # =========================================================================

    def select_output_dir(self) -> None:
        """Abre diálogo para selecionar pasta de destino."""
        directory = filedialog.askdirectory(
            title="Selecione a pasta de destino", initialdir=self.output_dir.get()
        )
        if directory:
            self.output_dir.set(directory)

    # =========================================================================
    # Persistência de Configurações
    # =========================================================================

    def _get_config_path(self) -> Path:
        """Retorna o caminho completo do arquivo de configuração."""
        return Path(__file__).resolve().parent / self.get_config_filename()

    @abstractmethod
    def get_config_filename(self) -> str:
        """Retorna o nome do arquivo de configuração JSON. Implementar na subclasse."""
        ...

    @abstractmethod
    def get_settings_dict(self) -> dict:
        """Retorna dicionário com configurações a salvar. Implementar na subclasse."""
        ...

    @abstractmethod
    def apply_settings(self, settings: dict) -> None:
        """Aplica configurações carregadas do JSON. Implementar na subclasse."""
        ...

    def save_settings(self) -> None:
        """Salva as configurações atuais em JSON."""
        settings = {
            "output_dir": self.output_dir.get(),
            "output_filename": self.output_filename.get(),
        }
        settings.update(self.get_settings_dict())

        try:
            config_path = self._get_config_path()
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)

            self.status_var.set("Configurações salvas com sucesso!")
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")

    def load_settings(self) -> None:
        """Carrega configurações do arquivo JSON."""
        try:
            config_path = self._get_config_path()
            if not config_path.exists():
                return

            with open(config_path, "r", encoding="utf-8") as f:
                settings = json.load(f)

            self.output_dir.set(settings.get("output_dir", DEFAULT_OUTPUT_DIR))
            self.output_filename.set(settings.get("output_filename", self._default_filename))
            self.apply_settings(settings)
        except Exception:
            pass  # Usar configurações padrão se houver erro

    # =========================================================================
    # Execução
    # =========================================================================

    def run(self) -> None:
        """Executa a aplicação."""
        self.root.mainloop()
