# 🌐 InputTranslator para Windows

Um tradutor flutuante inteligente, moderno e minimalista para Windows, inspirado no recurso de tradução do **Gboard (Android)** e no **InputTranslator**.

Projetado especialmente para quem conversa no **Telegram**, **WhatsApp**, **Discord**, navegadores ou qualquer outro aplicativo no Windows e sente falta da facilidade de traduzir e enviar mensagens na hora.

---

## ✨ Recursos

- ⚡ **Atalho Global Instantâneo**: Pressione `Alt + T` (personalizável) em qualquer lugar. O InputTranslator memoriza a conversa onde você estava e abre uma barra flutuante elegante.
- 🎨 **Design Moderno & Minimalista**:
  - Estilo Dark Fluent / Spotlight / Raycast.
  - Janela sem bordas (*frameless*), cantos arredondados e sombras suaves.
  - Não polui a tela nem atrapalha seu fluxo de trabalho.
- 🔍 **Tradução em Tempo Real**: Veja a tradução da sua frase instantaneamente enquanto digita com detecção automática do idioma de origem.
- 🚀 **Envio Automático**:
  - Aperte `Enter`: ele traduz, devolve o foco para o Telegram/Discord/WhatsApp, cola a tradução (`Ctrl+V`) e envia a mensagem (`Enter`) automaticamente!
  - `Shift + Enter`: Nova linha caso queira mensagens mais longas.
  - `Esc`: Fecha a janela sem colar.
  - Botão `⇄` para inversão rápida de idiomas.
  - Botão `📋 Copiar` para colocar a tradução na área de transferência sem enviar.
- 📌 **Bandeja do Sistema (System Tray)**: Fica silencioso perto do relógio do Windows, permitindo alterar atalhos e preferências a qualquer momento.
- 🔄 **Iniciar com o Windows**: Opção nativa para iniciar automaticamente com o sistema operacional.

---

## 🚀 Como Usar

### Opção 1: Instalador Oficial do Windows (Recomendado)
Basta dar dois cliques no instalador gerado:
📁 **`InputTranslator-Setup.exe`**
- Instala nos programas do Windows.
- Cria atalhos no Menu Iniciar e na Área de Trabalho.
- Configura automaticamente a **inicialização com o Windows**.
- Cria o desinstalador oficial no Painel de Controle / Configurações do Windows.

### Opção 2: Executável Portátil Standalone (.exe)
Se preferir usar sem instalar, execute diretamente:
📁 **`InputTranslator.exe`**

### Opção 3: Executar via Script / Python
```cmd
run.bat
```
ou
```bash
python main.py
```

---

## ⌨️ Atalhos Padrão

| Tecla | Ação |
| :--- | :--- |
| `Alt + T` | Abrir / Alternar a barra de tradução (configurável) |
| `Enter` | Traduzir, colar na conversa anterior e enviar |
| `Shift + Enter` | Quebra de linha no texto |
| `Esc` | Fechar a barra flutuante sem enviar |

---

## ⚙️ Configurações

Clique no ícone de engrenagem `⚙` na barra flutuante ou no ícone da bandeja do sistema (perto do relógio do Windows) para:
- Alterar o atalho global (ex: `ctrl+alt+t`, `ctrl+shift+t`, `alt+space`).
- Ativar/desativar o envio automático após colar.
- Ajustar o tempo de atraso da colagem (ms).
- Ativar a inicialização junto com o Windows.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.13**
- **PyQt6**: Interface gráfica nativa de alto desempenho e estilo customizado moderno.
- **Google Translate API**: Motor de tradução ultrarrápido sem necessidade de chaves de API.
- **Windows Win32 API**: Controle preciso de foco de janelas (`AttachThreadInput`, `SetForegroundWindow`, `keybd_event`).
