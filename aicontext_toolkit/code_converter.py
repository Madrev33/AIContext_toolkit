"""
Code to Markdown Converter - Combinador de códigos para Markdown.

Converte múltiplos arquivos de código em um único arquivo Markdown
formatado para uso com AI/LLM.
"""

import os
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Dict, List, Tuple

from tkfilebrowser import askopendirnames

from .base_app import BaseToolkitApp
from .config import (
    EXCLUDED_DIRS,
    EXTENSION_TO_LANGUAGE,
    FILE_DIALOG_TYPES,
    SUPPORTED_EXTENSIONS,
)
from .utils import detect_encoding, format_file_size, format_file_size_short


class CodeToMarkdownConverter(BaseToolkitApp):
    """Conversor de múltiplos arquivos de código em Markdown formatado."""

    def __init__(self) -> None:
        super().__init__(
            title="🔧 Code to Markdown Converter v1.0",
            default_filename="combined_code",
            default_status="Pronto para converter arquivos",
        )

    # =========================================================================
    # Implementação dos Métodos Abstratos
    # =========================================================================

    def get_config_filename(self) -> str:
        return "converter_config.json"

    def get_main_button_text(self) -> str:
        return "🚀 Converter para Markdown"

    def setup_tool_variables(self) -> None:
        """Configura variáveis específicas do converter."""
        self.selected_files: List[str] = []

        # Configurações de conversão
        self.include_timestamps = tk.BooleanVar(value=True)
        self.include_file_stats = tk.BooleanVar(value=True)
        self.add_line_numbers = tk.BooleanVar(value=False)
        self.remove_empty_lines = tk.BooleanVar(value=False)
        self.encoding_method = tk.StringVar(value="auto")
        self.excluded_patterns = tk.StringVar(value="????-??-??.md")

    def get_settings_dict(self) -> dict:
        return {
            "include_timestamps": self.include_timestamps.get(),
            "include_file_stats": self.include_file_stats.get(),
            "add_line_numbers": self.add_line_numbers.get(),
            "remove_empty_lines": self.remove_empty_lines.get(),
            "encoding_method": self.encoding_method.get(),
            "excluded_patterns": self.excluded_patterns.get(),
        }

    def apply_settings(self, settings: dict) -> None:
        self.include_timestamps.set(settings.get("include_timestamps", True))
        self.include_file_stats.set(settings.get("include_file_stats", True))
        self.add_line_numbers.set(settings.get("add_line_numbers", False))
        self.remove_empty_lines.set(settings.get("remove_empty_lines", False))
        self.encoding_method.set(settings.get("encoding_method", "auto"))
        self.excluded_patterns.set(settings.get("excluded_patterns", "????-??-??.md"))

    # =========================================================================
    # UI Específica
    # =========================================================================

    def setup_tool_ui(self, parent: ttk.Frame) -> None:
        """Configura a UI específica do converter."""
        # Título
        title_label = ttk.Label(
            parent,
            text="🔧 Combinador de Códigos para Markdown",
            font=("Arial", 16, "bold"),
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        self._setup_file_selection(parent)
        self._setup_configurations(parent)
        self._setup_preview_section(parent)

    def _setup_file_selection(self, parent: ttk.Frame) -> None:
        """Configura a seção de seleção de arquivos/pastas."""
        files_frame = ttk.LabelFrame(parent, text="📁 Seleção de Fontes", padding="10")
        files_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        files_frame.columnconfigure(3, weight=1)

        # Botão selecionar pastas
        ttk.Button(
            files_frame,
            text="📂 Adicionar Pastas",
            command=self.select_and_scan_folder,
        ).grid(row=0, column=0, padx=(0, 5))

        # Botão selecionar arquivos individuais
        ttk.Button(
            files_frame,
            text="📄 Adicionar Arquivos",
            command=self.select_individual_files,
        ).grid(row=0, column=1, padx=(0, 10))

        # Botão limpar seleção
        ttk.Button(
            files_frame, text="🗑️ Limpar Tudo", command=self.clear_selection
        ).grid(row=0, column=2, padx=(0, 10))

        # Label com contador
        self.files_count_label = ttk.Label(files_frame, text="Nenhum arquivo selecionado")
        self.files_count_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))

    def _setup_configurations(self, parent: ttk.Frame) -> None:
        """Configura as opções de configuração."""
        config_frame = ttk.LabelFrame(parent, text="⚙️ Configurações", padding="10")
        config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        config_frame.columnconfigure(0, weight=1)

        # Primeira linha
        row1 = ttk.Frame(config_frame)
        row1.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Checkbutton(row1, text="Incluir timestamps", variable=self.include_timestamps).grid(
            row=0, column=0, sticky=tk.W
        )
        ttk.Checkbutton(
            row1, text="Incluir estatísticas dos arquivos", variable=self.include_file_stats
        ).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))

        # Segunda linha
        row2 = ttk.Frame(config_frame)
        row2.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Checkbutton(
            row2, text="Adicionar números de linha", variable=self.add_line_numbers
        ).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(
            row2, text="Remover linhas vazias", variable=self.remove_empty_lines
        ).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))

        # Terceira linha - Filtro de exclusão
        exclusion_frame = ttk.Frame(config_frame)
        exclusion_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        exclusion_frame.columnconfigure(1, weight=1)

        ttk.Label(exclusion_frame, text="Excluir arquivos (padrões, sep. por vírgula):").grid(
            row=0, column=0, sticky=tk.W
        )
        self.exclusion_patterns_entry = ttk.Entry(exclusion_frame)
        self.exclusion_patterns_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))

        # Quarta linha - Encoding
        encoding_frame = ttk.Frame(config_frame)
        encoding_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Label(encoding_frame, text="Encoding:").grid(row=0, column=0, sticky=tk.W)
        ttk.Combobox(
            encoding_frame,
            textvariable=self.encoding_method,
            values=["auto", "utf-8", "latin-1", "cp1252"],
            width=10,
            state="readonly",
        ).grid(row=0, column=1, sticky=tk.W, padx=(5, 0))

    def _setup_preview_section(self, parent: ttk.Frame) -> None:
        """Configura a seção de preview dos arquivos."""
        preview_frame = ttk.LabelFrame(
            parent, text="👁️ Preview dos Arquivos Selecionados", padding="10"
        )
        preview_frame.grid(
            row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0)
        )
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        # Lista de arquivos com scrollbar
        self.files_listbox = tk.Listbox(preview_frame, height=8, selectmode=tk.EXTENDED)
        scrollbar = ttk.Scrollbar(
            preview_frame, orient=tk.VERTICAL, command=self.files_listbox.yview
        )
        self.files_listbox.configure(yscrollcommand=scrollbar.set)

        self.files_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Botão remover
        ttk.Button(
            preview_frame, text="❌ Remover Selecionados", command=self.remove_selected_files
        ).grid(row=1, column=0, columnspan=2, pady=(10, 0))

    # =========================================================================
    # Seleção de Arquivos e Pastas
    # =========================================================================

    def _get_supported_extensions(self) -> Tuple:
        """Retorna uma tupla com todas as extensões suportadas."""
        all_exts: set[str] = set()
        for exts in SUPPORTED_EXTENSIONS.values():
            all_exts.update(exts)
        return tuple(all_exts)

    def select_and_scan_folder(self) -> None:
        """Abre diálogo para selecionar pastas e varre em busca de arquivos."""
        directories = askopendirnames(
            title="Selecione uma ou mais pastas de projeto",
            initialdir=self.last_input_path,
        )

        if not directories:
            return

        self.last_input_path = directories[0]

        current_files_set = set(self.selected_files)
        supported_exts = self._get_supported_extensions()

        for directory in directories:
            for root, dirs, files in os.walk(directory, topdown=True):
                dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]

                for file in files:
                    if file.endswith(supported_exts):
                        full_path = Path(root) / file
                        current_files_set.add(str(full_path))

        self.selected_files = sorted(current_files_set)

        self._update_files_display()
        self.status_var.set(f"{len(self.selected_files)} arquivo(s) encontrado(s) no total.")

    def select_individual_files(self) -> None:
        """Abre diálogo para seleção múltipla de arquivos individuais."""
        files = filedialog.askopenfilenames(
            title="Selecione arquivos de código individuais",
            initialdir=self.last_input_path,
            filetypes=FILE_DIALOG_TYPES,
        )

        if not files:
            return

        self.last_input_path = str(Path(files[0]).parent)

        current_files_set = set(self.selected_files)
        current_files_set.update(files)
        self.selected_files = sorted(current_files_set)

        self._update_files_display()
        self.status_var.set(f"{len(self.selected_files)} arquivo(s) selecionado(s) no total.")

    def clear_selection(self) -> None:
        """Limpa a seleção de arquivos."""
        self.selected_files.clear()
        self._update_files_display()
        self.status_var.set("Seleção de arquivos limpa")

    def remove_selected_files(self) -> None:
        """Remove arquivos selecionados da lista."""
        selection = self.files_listbox.curselection()
        if selection:
            for index in reversed(selection):
                del self.selected_files[index]
            self._update_files_display()
            self.status_var.set(f"{len(self.selected_files)} arquivo(s) restante(s)")

    def _update_files_display(self) -> None:
        """Atualiza a exibição da lista de arquivos."""
        self.files_listbox.delete(0, tk.END)

        for file_path in self.selected_files:
            filename = Path(file_path).name
            size = format_file_size_short(file_path)
            self.files_listbox.insert(tk.END, f"{filename} ({size})")

        count = len(self.selected_files)
        if count == 0:
            self.files_count_label.config(text="Nenhum arquivo selecionado")
        elif count == 1:
            self.files_count_label.config(text="1 arquivo selecionado")
        else:
            self.files_count_label.config(text=f"{count} arquivos selecionados")

    # =========================================================================
    # Leitura e Formatação
    # =========================================================================

    def _read_file_content(self, file_path: str) -> Tuple[str, Dict]:
        """Lê o conteúdo do arquivo e retorna (conteúdo, info)."""
        encoding = detect_encoding(file_path, self.encoding_method.get())
        path_obj = Path(file_path)
        file_info = {
            "path": file_path,
            "name": path_obj.name,
            "size": path_obj.stat().st_size,
            "encoding": encoding,
            "modified": datetime.fromtimestamp(path_obj.stat().st_mtime),
        }

        try:
            with open(file_path, "r", encoding=encoding, errors="replace") as f:
                content = f.read()

            if self.remove_empty_lines.get():
                lines = content.split("\n")
                lines = [line for line in lines if line.strip()]
                content = "\n".join(lines)

            file_info["lines"] = len(content.split("\n"))
            file_info["chars"] = len(content)

            return content, file_info

        except Exception as e:
            error_content = f"Erro ao ler arquivo: {e}"
            file_info["error"] = str(e)
            file_info["lines"] = 0
            file_info["chars"] = 0
            return error_content, file_info

    def _format_content_for_markdown(self, content: str, file_info: Dict) -> str:
        """Formata o conteúdo para Markdown."""
        md_content: List[str] = []

        md_content.append("---")
        md_content.append(f"## {file_info['name']}")
        md_content.append("")

        if self.include_file_stats.get():
            md_content.append("**Informações do Arquivo:**")
            md_content.append(f"- **Caminho:** `{file_info['path']}`")
            md_content.append(f"- **Tamanho:** {format_file_size(file_info['size'])}")
            md_content.append(f"- **Linhas:** {file_info['lines']}")
            md_content.append(f"- **Caracteres:** {file_info['chars']}")
            md_content.append(f"- **Encoding:** {file_info['encoding']}")

            if self.include_timestamps.get():
                md_content.append(
                    f"- **Modificado:** {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}"
                )

            md_content.append("")

        # Syntax highlighting
        extension = Path(file_info["name"]).suffix.lower()
        language = EXTENSION_TO_LANGUAGE.get(extension, "text")

        md_content.append("**Conteúdo:**")
        md_content.append("")
        md_content.append(f"```{language}")

        if self.add_line_numbers.get():
            lines = content.split("\n")
            numbered_lines = [f"{i:4d} | {line}" for i, line in enumerate(lines, 1)]
            content = "\n".join(numbered_lines)

        md_content.append(content)
        md_content.append("```")
        md_content.append("")

        return "\n".join(md_content)

    # =========================================================================
    # Ação Principal
    # =========================================================================

    def start_main_action(self) -> None:
        """Inicia o processo de conversão em thread separada."""
        if not self.selected_files:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado para conversão!")
            return

        if not self.output_filename.get().strip():
            messagebox.showwarning("Aviso", "Digite um nome para o arquivo de saída!")
            return

        thread = threading.Thread(target=self._convert_files, daemon=True)
        thread.start()

    def _convert_files(self) -> None:
        """Executa a conversão dos arquivos."""
        try:
            self.status_var.set("Iniciando conversão...")
            self.progress_var.set(0)

            total_files = len(self.selected_files)
            markdown_content: List[str] = []

            # Cabeçalho
            markdown_content.append("# Combined Code Export")
            markdown_content.append("")
            markdown_content.append(
                f"**Data de criação:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            markdown_content.append(f"**Total de arquivos:** {total_files}")
            markdown_content.extend(["", "---", ""])

            # Processar cada arquivo
            for i, file_path in enumerate(self.selected_files):
                try:
                    self.status_var.set(f"Processando: {Path(file_path).name}...")
                    self.progress_var.set((i / total_files) * 100)

                    content, file_info = self._read_file_content(file_path)
                    formatted = self._format_content_for_markdown(content, file_info)
                    markdown_content.append(formatted)

                except Exception as e:
                    error_md = (
                        f"---\n"
                        f"## {Path(file_path).name} [ERRO]\n\n"
                        f"**Erro ao processar arquivo:** {e}\n\n"
                        f"---\n"
                    )
                    markdown_content.append(error_md)

            # Salvar
            self.status_var.set("Salvando arquivo final...")
            self.progress_var.set(95)

            output_path = Path(self.output_dir.get()) / f"{self.output_filename.get()}.md"

            with open(output_path, "w", encoding="utf-8", errors="replace") as f:
                f.write("\n".join(markdown_content))

            self.progress_var.set(100)
            self.status_var.set(f"Conversão concluída! Arquivo salvo em: {output_path}")

            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Sucesso!",
                    f"Conversão concluída com sucesso!\n\n"
                    f"Arquivo salvo em:\n{output_path}\n\n"
                    f"Total de arquivos processados: {total_files}",
                ),
            )

        except Exception as e:
            error_msg = f"Erro durante a conversão: {e}"
            self.status_var.set(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Erro", error_msg))
        finally:
            self.root.after(3000, lambda: self.progress_var.set(0))
