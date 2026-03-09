"""
Obsidian Folder Scanner - Gerador de árvore ASCII da estrutura de pastas.

Escaneia pastas do Obsidian e gera um arquivo Markdown com a
representação em árvore ASCII da estrutura de diretórios.
"""

import os
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import List, Tuple

from tkfilebrowser import askopendirnames

from .base_app import BaseToolkitApp
from .config import TREE_STYLES


class ObsidianFolderScanner(BaseToolkitApp):
    """Scanner de estrutura de pastas com geração de árvore ASCII."""

    def __init__(self) -> None:
        super().__init__(
            title="📁 Obsidian Folder Structure Scanner v2.0",
            default_filename="obsidian_folder_structure",
            default_status="Pronto para escanear estrutura de pastas",
        )

    # =========================================================================
    # Implementação dos Métodos Abstratos
    # =========================================================================

    def get_config_filename(self) -> str:
        return "folder_scanner_config.json"

    def get_main_button_text(self) -> str:
        return "🔍 Escanear e Gerar ASCII"

    def setup_tool_variables(self) -> None:
        """Configura variáveis específicas do scanner."""
        self.selected_folders: List[str] = []

        # Configurações de escaneamento
        self.include_timestamps = tk.BooleanVar(value=True)
        self.include_folder_stats = tk.BooleanVar(value=True)
        self.show_hidden_folders = tk.BooleanVar(value=False)
        self.max_depth = tk.IntVar(value=0)  # 0 = sem limite
        self.use_tree_style = tk.StringVar(value="ascii")
        self.sort_alphabetically = tk.BooleanVar(value=True)
        self.include_empty_folders = tk.BooleanVar(value=True)

    def get_settings_dict(self) -> dict:
        return {
            "include_timestamps": self.include_timestamps.get(),
            "include_folder_stats": self.include_folder_stats.get(),
            "show_hidden_folders": self.show_hidden_folders.get(),
            "max_depth": self.max_depth.get(),
            "use_tree_style": self.use_tree_style.get(),
            "sort_alphabetically": self.sort_alphabetically.get(),
            "include_empty_folders": self.include_empty_folders.get(),
        }

    def apply_settings(self, settings: dict) -> None:
        self.include_timestamps.set(settings.get("include_timestamps", True))
        self.include_folder_stats.set(settings.get("include_folder_stats", True))
        self.show_hidden_folders.set(settings.get("show_hidden_folders", False))
        self.max_depth.set(settings.get("max_depth", 0))
        self.use_tree_style.set(settings.get("use_tree_style", "ascii"))
        self.sort_alphabetically.set(settings.get("sort_alphabetically", True))
        self.include_empty_folders.set(settings.get("include_empty_folders", True))

    # =========================================================================
    # UI Específica
    # =========================================================================

    def setup_tool_ui(self, parent: ttk.Frame) -> None:
        """Configura a UI específica do scanner."""
        # Título
        title_label = ttk.Label(
            parent,
            text="📁 Scanner de Estrutura de Pastas - Obsidian",
            font=("Arial", 16, "bold"),
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        self._setup_folder_selection(parent)
        self._setup_scan_configurations(parent)
        self._setup_preview_section(parent)

    def _setup_folder_selection(self, parent: ttk.Frame) -> None:
        """Configura a seção de seleção de pastas."""
        folders_frame = ttk.LabelFrame(parent, text="📂 Seleção de Pastas do Obsidian", padding="10")
        folders_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        folders_frame.columnconfigure(3, weight=1)

        # Botão selecionar múltiplas pastas
        ttk.Button(
            folders_frame,
            text="📂 Adicionar Pastas",
            command=self.select_folders,
            style="Accent.TButton",
        ).grid(row=0, column=0, padx=(0, 5))

        # Botão selecionar pasta individual
        ttk.Button(
            folders_frame,
            text="📁 Adicionar Pasta Individual",
            command=self.select_single_folder,
        ).grid(row=0, column=1, padx=(0, 10))

        # Botão limpar seleção
        ttk.Button(
            folders_frame, text="🗑️ Limpar Tudo", command=self.clear_selection
        ).grid(row=0, column=2, padx=(0, 10))

        # Label com contador de pastas
        self.folders_count_label = ttk.Label(folders_frame, text="Nenhuma pasta selecionada")
        self.folders_count_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))

    def _setup_scan_configurations(self, parent: ttk.Frame) -> None:
        """Configura as opções de escaneamento."""
        config_frame = ttk.LabelFrame(
            parent, text="⚙️ Configurações de Escaneamento", padding="10"
        )
        config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

        # Primeira linha
        row1 = ttk.Frame(config_frame)
        row1.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Checkbutton(row1, text="Incluir timestamps", variable=self.include_timestamps).grid(
            row=0, column=0, sticky=tk.W
        )
        ttk.Checkbutton(
            row1, text="Incluir estatísticas das pastas", variable=self.include_folder_stats
        ).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))

        # Segunda linha
        row2 = ttk.Frame(config_frame)
        row2.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Checkbutton(
            row2, text="Mostrar pastas ocultas", variable=self.show_hidden_folders
        ).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(
            row2, text="Ordenar alfabeticamente", variable=self.sort_alphabetically
        ).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        ttk.Checkbutton(
            row2, text="Incluir pastas vazias", variable=self.include_empty_folders
        ).grid(row=0, column=2, sticky=tk.W, padx=(20, 0))

        # Terceira linha - Configurações avançadas
        row3 = ttk.Frame(config_frame)
        row3.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Label(row3, text="Profundidade máxima:").grid(row=0, column=0, sticky=tk.W)
        ttk.Spinbox(row3, from_=0, to=20, textvariable=self.max_depth, width=5).grid(
            row=0, column=1, sticky=tk.W, padx=(5, 20)
        )
        ttk.Label(row3, text="(0 = sem limite)").grid(row=0, column=2, sticky=tk.W)

        ttk.Label(row3, text="Estilo ASCII:").grid(row=0, column=3, sticky=tk.W, padx=(20, 0))
        ttk.Combobox(
            row3,
            textvariable=self.use_tree_style,
            values=list(TREE_STYLES.keys()),
            width=10,
            state="readonly",
        ).grid(row=0, column=4, sticky=tk.W, padx=(5, 0))

    def _setup_preview_section(self, parent: ttk.Frame) -> None:
        """Configura a seção de preview das pastas."""
        preview_frame = ttk.LabelFrame(parent, text="🌳 Preview da Estrutura", padding="10")
        preview_frame.grid(
            row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0)
        )
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        # Lista de pastas com scrollbar
        self.folders_listbox = tk.Listbox(preview_frame, height=8, selectmode=tk.EXTENDED)
        scrollbar = ttk.Scrollbar(
            preview_frame, orient=tk.VERTICAL, command=self.folders_listbox.yview
        )
        self.folders_listbox.configure(yscrollcommand=scrollbar.set)

        self.folders_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Botões de ação na preview
        buttons_frame = ttk.Frame(preview_frame)
        buttons_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(
            buttons_frame, text="❌ Remover Selecionadas", command=self.remove_selected_folders
        ).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(
            buttons_frame, text="👁️ Preview Estrutura", command=self.preview_structure
        ).grid(row=0, column=1)

    # =========================================================================
    # Seleção de Pastas
    # =========================================================================

    def select_folders(self) -> None:
        """Abre diálogo para seleção de múltiplas pastas usando tkfilebrowser."""
        directories = askopendirnames(
            title="Selecione uma ou mais pastas do Obsidian",
            initialdir=self.last_input_path,
        )

        if not directories:
            return

        self.last_input_path = directories[0]

        current_set = set(self.selected_folders)
        current_set.update(directories)
        self.selected_folders = sorted(current_set)

        self._update_folders_display()
        self.status_var.set(f"{len(self.selected_folders)} pasta(s) selecionada(s) no total.")

    def select_single_folder(self) -> None:
        """Abre diálogo para seleção de uma pasta individual."""
        folder = filedialog.askdirectory(
            title="Selecione uma pasta do Obsidian",
            initialdir=self.last_input_path,
        )

        if not folder:
            return

        self.last_input_path = folder

        if folder not in self.selected_folders:
            self.selected_folders.append(folder)
            self.selected_folders.sort()

        self._update_folders_display()
        self.status_var.set(f"{len(self.selected_folders)} pasta(s) selecionada(s) no total.")

    def clear_selection(self) -> None:
        """Limpa a seleção de pastas."""
        self.selected_folders.clear()
        self._update_folders_display()
        self.status_var.set("Seleção de pastas limpa")

    def remove_selected_folders(self) -> None:
        """Remove pastas selecionadas da lista."""
        selection = self.folders_listbox.curselection()
        if selection:
            for index in reversed(selection):
                del self.selected_folders[index]
            self._update_folders_display()
            self.status_var.set(f"{len(self.selected_folders)} pasta(s) restante(s)")

    def _update_folders_display(self) -> None:
        """Atualiza a exibição da lista de pastas."""
        self.folders_listbox.delete(0, tk.END)

        for folder_path in self.selected_folders:
            folder = Path(folder_path)
            folder_name = folder.name
            folder_info = self._get_folder_info(folder)
            self.folders_listbox.insert(tk.END, f"{folder_name} ({folder_info})")

        count = len(self.selected_folders)
        if count == 0:
            self.folders_count_label.config(text="Nenhuma pasta selecionada")
        elif count == 1:
            self.folders_count_label.config(text="1 pasta selecionada")
        else:
            self.folders_count_label.config(text=f"{count} pastas selecionadas")

    def _get_folder_info(self, folder: Path) -> str:
        """Retorna informações básicas da pasta."""
        try:
            folders = [item for item in folder.iterdir() if item.is_dir()]
            return f"{len(folders)} subpastas"
        except Exception:
            return "? subpastas"

    # =========================================================================
    # Escaneamento e Geração
    # =========================================================================

    def scan_folder_structure(
        self, root_path: str, current_depth: int = 0
    ) -> List[Tuple[str, int, bool]]:
        """Escaneia a estrutura de uma pasta.

        Returns:
            Lista de tuplas (nome, profundidade, é_último).
        """
        structure: List[Tuple[str, int, bool]] = []

        if self.max_depth.get() > 0 and current_depth >= self.max_depth.get():
            return structure

        try:
            items = []
            root_dir = Path(root_path)
            for item in root_dir.iterdir():
                if not item.is_dir():
                    continue

                if not self.show_hidden_folders.get() and item.name.startswith("."):
                    continue

                if not self.include_empty_folders.get():
                    if not any(sub.is_dir() for sub in item.iterdir()):
                        continue

                items.append((item.name, str(item)))

            if self.sort_alphabetically.get():
                items.sort(key=lambda x: x[0].lower())

            for i, (item_name, item_path) in enumerate(items):
                is_last = i == len(items) - 1
                structure.append((item_name, current_depth, is_last))
                structure.extend(self.scan_folder_structure(item_path, current_depth + 1))

        except PermissionError:
            structure.append(("❌ [Sem permissão]", current_depth, True))
        except Exception as e:
            structure.append((f"⚠️ [Erro: {e}]", current_depth, True))

        return structure

    def generate_ascii_tree(
        self, structure: List[Tuple[str, int, bool]], root_name: str
    ) -> List[str]:
        """Gera a árvore ASCII a partir da estrutura escaneada."""
        tree_lines = [f"📁 {root_name}/"]
        style = TREE_STYLES[self.use_tree_style.get()]
        pipes_at_level: dict[int, bool] = {}

        for item_name, depth, is_last in structure:
            prefix = ""

            for level in range(depth):
                if pipes_at_level.get(level, False):
                    prefix += style["pipe"]
                else:
                    prefix += style["space"]

            if is_last:
                prefix += style["last"]
                pipes_at_level[depth] = False
            else:
                prefix += style["branch"]
                pipes_at_level[depth] = True

            pipes_at_level = {k: v for k, v in pipes_at_level.items() if k <= depth}
            tree_lines.append(f"{prefix}📁 {item_name}/")

        return tree_lines

    def preview_structure(self) -> None:
        """Mostra preview da estrutura em janela popup."""
        if not self.selected_folders:
            messagebox.showwarning("Aviso", "Selecione ao menos uma pasta para preview!")
            return

        preview_window = tk.Toplevel(self.root)
        preview_window.title("🌳 Preview da Estrutura")
        preview_window.geometry("800x600")

        text_frame = ttk.Frame(preview_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget = tk.Text(text_frame, wrap=tk.NONE, font=("Courier New", 10))
        v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        h_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
        text_widget.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        try:
            preview_content = [
                "🌳 PREVIEW DA ESTRUTURA DE PASTAS",
                "=" * 50,
                "",
            ]

            for folder_path in self.selected_folders[:3]:
                folder_name = Path(folder_path).name
                preview_content.append(f"📂 Escaneando: {folder_name}")
                preview_content.append("-" * 30)

                structure = self.scan_folder_structure(folder_path)
                ascii_tree = self.generate_ascii_tree(structure, folder_name)
                preview_content.extend(ascii_tree)
                preview_content.append("")

            if len(self.selected_folders) > 3:
                preview_content.append(f"... e mais {len(self.selected_folders) - 3} pasta(s)")

            text_widget.insert(tk.END, "\n".join(preview_content))
            text_widget.configure(state=tk.DISABLED)
        except Exception as e:
            text_widget.insert(tk.END, f"Erro no preview: {e}")

    # =========================================================================
    # Ação Principal
    # =========================================================================

    def start_main_action(self) -> None:
        """Inicia o processo de escaneamento em thread separada."""
        if not self.selected_folders:
            messagebox.showwarning("Aviso", "Nenhuma pasta selecionada para escaneamento!")
            return

        if not self.output_filename.get().strip():
            messagebox.showwarning("Aviso", "Digite um nome para o arquivo de saída!")
            return

        thread = threading.Thread(target=self._scan_and_generate, daemon=True)
        thread.start()

    def _scan_and_generate(self) -> None:
        """Executa o escaneamento e geração do arquivo."""
        try:
            self.status_var.set("Iniciando escaneamento...")
            self.progress_var.set(0)

            total_folders = len(self.selected_folders)
            markdown_content: List[str] = []

            # Cabeçalho
            markdown_content.append("# 📁 Estrutura de Pastas do Obsidian")
            markdown_content.append("")
            markdown_content.append(
                f"**Data de geração:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            markdown_content.append(f"**Total de pastas escaneadas:** {total_folders}")
            markdown_content.append(f"**Estilo ASCII:** {self.use_tree_style.get()}")

            if self.max_depth.get() > 0:
                markdown_content.append(f"**Profundidade máxima:** {self.max_depth.get()} níveis")
            else:
                markdown_content.append("**Profundidade:** Ilimitada")

            markdown_content.extend(["", "---", ""])

            # Processar cada pasta
            for i, folder_path in enumerate(self.selected_folders):
                try:
                    folder_name = Path(folder_path).name
                    self.status_var.set(f"Escaneando: {folder_name}...")
                    self.progress_var.set((i / total_folders) * 90)

                    markdown_content.append(f"## 📂 {folder_name}")
                    markdown_content.append("")

                    if self.include_folder_stats.get():
                        stats = self._get_detailed_folder_stats(folder_path)
                        markdown_content.extend(stats)
                        markdown_content.append("")

                    structure = self.scan_folder_structure(folder_path)

                    if structure:
                        markdown_content.append("**Estrutura:**")
                        markdown_content.append("")
                        markdown_content.append("```")
                        markdown_content.extend(self.generate_ascii_tree(structure, folder_name))
                        markdown_content.append("```")
                    else:
                        markdown_content.append("*Pasta vazia ou sem subpastas visíveis*")

                    markdown_content.extend(["", "---", ""])

                except Exception as e:
                    markdown_content.extend([
                        f"## ❌ {Path(folder_path).name} [ERRO]",
                        "",
                        f"**Erro ao escanear pasta:** {e}",
                        "",
                        "---",
                        "",
                    ])

            # Salvar
            self.status_var.set("Salvando arquivo...")
            self.progress_var.set(95)

            output_path = Path(self.output_dir.get()) / f"{self.output_filename.get()}.md"

            with open(output_path, "w", encoding="utf-8", errors="replace") as f:
                f.write("\n".join(markdown_content))

            self.progress_var.set(100)
            self.status_var.set(f"Escaneamento concluído! Arquivo salvo em: {output_path}")

            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Sucesso!",
                    f"Estrutura de pastas gerada com sucesso!\n\n"
                    f"Arquivo salvo em:\n{output_path}\n\n"
                    f"Total de pastas escaneadas: {total_folders}",
                ),
            )

        except Exception as e:
            error_msg = f"Erro durante o escaneamento: {e}"
            self.status_var.set(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Erro", error_msg))
        finally:
            self.root.after(3000, lambda: self.progress_var.set(0))

    def _get_detailed_folder_stats(self, folder_path: str) -> List[str]:
        """Retorna estatísticas detalhadas da pasta."""
        stats: List[str] = []

        try:
            total_folders = 0
            for _root, dirs, _files in os.walk(folder_path):
                if not self.show_hidden_folders.get():
                    dirs[:] = [d for d in dirs if not d.startswith(".")]
                total_folders += len(dirs)

            stats.append("**Estatísticas:**")
            stats.append(f"- **Caminho completo:** `{folder_path}`")
            stats.append(f"- **Total de subpastas:** {total_folders}")

            if self.include_timestamps.get():
                modified_time = datetime.fromtimestamp(Path(folder_path).stat().st_mtime)
                stats.append(
                    f"- **Última modificação:** {modified_time.strftime('%Y-%m-%d %H:%M:%S')}"
                )
        except Exception:
            stats.append("**Estatísticas:** Erro ao calcular")

        return stats
