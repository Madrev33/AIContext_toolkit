![Header](https://img.shields.io/badge/STATUS-OPEN%20SOURCE-brightgreen?style=flat-square) ![License](https://img.shields.io/badge/LICENSE-MIT-yellow?style=flat-square) ![Obsidian](https://img.shields.io/badge/OBSIDIAN-V1.4%2B-0088cc?style=flat-square) ![Platform](https://img.shields.io/badge/PLATFORM-WINDOWS%20%7C%20MAC%20%7C%20LINUX-gray?style=flat-square)

# AIContext Toolkit

Toolkit objetivo projetado para agilizar o fluxo de trabalho de desenvolvedores e usuários do Obsidian que utilizam Inteligência Artificial no navegador. As ferramentas empacotam e estruturam massas de código e diretórios diretamente em documentos `Markdown` (`.md`).

---


> **Atenção:** Evite extrair e enviar toda a sua base de código de uma só vez. Despejar excesso de informação aglomerada em um único prompt degrada significativamente a inteligência e as respostas da sua IA. Extraia e injete o contexto em partes/etapas lógicas, focando apenas nas pastas ou módulos estritamente relevantes para a funcionalidade que você está construindo no momento.


## 🚀 Guia Rápido de Instalação

Abra seu terminal na raiz do projeto e instale as dependências executando o projeto no modo editável:

```bash
# Instala as dependências e linka o pacote localmente
pip install -e .

# Inicia o Launcher do Toolkit
python run.py
```

---

## 🛠️ Ferramentas Inclusas

O Launcher do aplicativo abrirá uma interface gráfica permitindo escolher entre duas ferramentas principais:

### 1. Code to Markdown Converter
Combinador de múltiplos arquivos em um prompt unificado.
- Extrai e agrupa código-fonte de dezenas de linguagens (`.py`, `.js`, `.ts`, `.html`, etc).
- Mantém o *Syntax Highlighting* adequado para a marcação do Markdown.
- Remove quebras de linha vazias ou insere linhas numeradas sob demanda.
- Produz um arquivo final limpo, ideal para arrastar diretamente para o ChatGPT, Claude ou Gemini.

### 2. Obsidian Folder Scanner
Mapeador de topologia de arquivos.
- Selecione pastas do seu Vault do Obsidian ou de Projetos Locais.
- Gera representação em Árvores ASCII (e.g. `├── item/`) de forma instantânea.
- Controle de limite de profundidade de pastas, exclusão de pastas ocultas e pastas vazias.

---

## 🎯 Casos de Uso

**Para Desenvolvedores:**
Útil em casos raros onde não se pode usar IA injetada na IDE e necessita-se operar via navegador:
- Jogar múltiplas classes rapidamente em interfaces web como **Perplexity**, **ChatGPT** ou **Claude**.
- Evitar copiar/colar arquivos um por um ao pedir revisão de arquitetura para a IA.

**Para Usuários de Obsidian:**
- Alimentar o LLM com o mapa do seu Vault (Árvore ASCII) para pedir sugestões de reestruturação.
- Dar contexto das suas pastas para a IA ajudar a organizar.

---

## ⚙️ Requisitos

* Python 3.8 ou superior
* Bibliotecas listadas no `pyproject.toml` (instaladas automaticamente com o `pip install -e .`):
  * `tkfilebrowser`
  * `charset-normalizer`
