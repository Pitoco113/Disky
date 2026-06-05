# 📦 Disky - Desktop File Organizer

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Windows](https://img.shields.io/badge/Windows-10%2B-orange.svg)

**Disky** é um aplicativo desktop para Windows que organiza seus arquivos automaticamente, encontra duplicatas e ainda salva todas as suas configurações. Feito com 💙 por **PITOCO113 🇧🇷**

---

## ✨ Funcionalidades

### 📂 Organizador de Arquivos
- **Monitoramento automático** de pastas
- **Regras personalizáveis** por extensão de arquivo
- **Histórico completo** de arquivos organizados
- Executa com um clique ou automaticamente

### 🔍 Scanner de Duplicatas
- Encontra arquivos duplicados por conteúdo (hash)
- Lista organizada por grupo de duplicatas
- Possibilidade de excluir mantendo apenas o original

### 🌐 Bilíngue
- **Português (BR)** 🇧🇷
- **English (US)** 🇺🇸
- Troca instantânea nas configurações

### 💾 Persistência Total
- Todas as configurações salvas em SQLite
- Regras, pastas monitoradas, histórico, preferências
- Funciona após fechar e reabrir o app

---

## 🚀 Como Usar

### Executável (mais rápido)
1. Baixe o `Disky.exe` da [última release](https://github.com/Pitoco113/Disky/releases/latest)
2. Execute — na primeira vez aparece o tutorial de boas-vindas
3. Pronto!

### Pelo Código Fonte
```bash
# Clone o repositório
git clone https://github.com/Pitoco113/Disky.git
cd Disky

# Instale as dependências
pip install -r requirements.txt

# Execute
python main.py
```

### Buildar o .exe você mesmo
```bash
pip install pyinstaller
pyinstaller Disky.spec
# O executável estará em dist/Disky.exe
```

---

## 📁 Estrutura do Projeto

```
Disky/
├── main.py              # Ponto de entrada
├── locales.py           # Traduções PT-BR + EN
├── ui/
│   ├── app.py           # Interface gráfica (tkinter)
│   └── wizard.py        # Tutorial de boas-vindas
├── core/
│   ├── db.py            # Banco de dados SQLite
│   ├── organizer.py     # Lógica de organização
│   └── duplicate_finder.py  # Scanner de duplicatas
├── build/               # Arquivos de build
├── dist/                # Executável final
└── data/                # Dados do app (criado automaticamente)
```

---

## 🛠️ Tecnologias

- **Python 3.11+** — Linguagem
- **Tkinter** — Interface gráfica
- **SQLite** — Persistência de dados
- **PyInstaller** — Build do executável

---

## 📸 Screenshots

*Em breve! Quer contribuir com um screenshot? Abra uma issue!*

---

## 🤝 Contribuir

Contribuições são bem-vindas! Abra uma issue ou envie um pull request.

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👤 Autor

**PITOCO113** 🇧🇷

- GitHub: [@Pitoco113](https://github.com/Pitoco113)
- YouTube: [Deu Ruim na História](https://youtube.com/@seu-canal)

---

⭐ **Se este projeto te ajudou, deixe uma estrela!** Isso me motiva a continuar melhorando!