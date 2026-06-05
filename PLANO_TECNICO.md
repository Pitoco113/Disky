# 🧹 Disky - Plano Técnico Completo

**Criador: PITOCO113 🇧🇷**
**Versão: 1.0 - MVP**

> "O lixeiro que arruma seu PC sozinho"

---

## 📌 Conceito

App que roda em segundo plano e **automaticamente organiza os arquivos bagunçados** enquanto **caça e limpa duplicatas** que tão ocupando espaço à toa.

Dois problemas num app só:
1. 📥 **Downloads Organizer** — pasta de Downloads sempre organizada
2. 🔁 **Duplicate Slayer** — encontra arquivos repetidos e sugere limpeza

---

## ⚙️ Stack Tecnológica

| Ferramenta | Pra quê |
|---|---|
| **Python 3.11** | Lógica |
| **customtkinter** | Interface bonita |
| **pillow** | Ícones e thumbnails |
| **watchdog** | Monitorar pasta Downloads em tempo real |
| **pywin32** | Ícone na bandeja, integração Windows |
| **pyinstaller** | Gerar .exe |

---

## 🧱 Módulos

```
Disky/
├── main.py
├── locales.py                  # 🇧🇷🇺🇸 PT-BR + EN
├── ui/
│   ├── app.py                  # Janela principal
│   ├── dashboard.py            # Tela inicial com resumo
│   ├── organizer_tab.py        # Aba do organizador
│   ├── duplicate_tab.py        # Aba de duplicatas
│   └── settings_tab.py         # Configurações + regras
├── core/
│   ├── watcher.py              # Monitora pasta em tempo real (watchdog)
│   ├── organizer.py            # Lógica de organização
│   ├── duplicate_finder.py     # Scanner de duplicatas
│   └── rules.py                # Sistema de regras do usuário
├── data/
│   ├── db.py                   # SQLite (histórico + regras)
│   └── rules.json              # Regras salvas
├── build/
│   └── icon.ico
└── dist/
    └── Disky.exe
```

---

## 🔧 Funcionalidades Detalhadas

### 📥 1. Downloads Organizer

**Funcionamento:**
- Monitora pasta Downloads (e outras que o usuário adicionar)
- Quando um arquivo chega, **automaticamente move** pra pasta correta

**Regras padrão (já vem configurado):**
| Tipo | Extensões | Destino |
|---|---|---|
| 📄 Documentos | .pdf .doc .docx .xlsx .txt .odt | Downloads/Documentos/ |
| 🖼️ Imagens | .jpg .jpeg .png .gif .bmp .webp | Downloads/Imagens/ |
| 🎵 Músicas | .mp3 .wav .flac .aac .ogg | Downloads/Músicas/ |
| 🎬 Vídeos | .mp4 .avi .mkv .mov .wmv | Downloads/Vídeos/ |
| 💿 Instaladores | .exe .msi .dmg .appimage | Downloads/Instaladores/ |
| 📦 Compactados | .zip .rar .7z .tar .gz | Downloads/Compactados/ |
| 📚 E-books | .epub .mobi .cbr .cbz | Downloads/E-books/ |
| 📋 Outros | *qualquer outro* | Downloads/Outros/ |

- **Usuário pode criar regras próprias** (ex: "arquivo com 'boleto' no nome → Downloads/Boletos")
- Organização **retroativa**: botão "Organizar Tudo" que varre Downloads inteiro

**Prós vs concorrentes:**
- DropIt: complicado, precisa configurar
- Belvedere: abandonado
- File Juggler: pago
- **Disky: simples, bonito, gratuito, roda sozinho**

---

### 🔁 2. Duplicate Slayer

**Funcionamento:**
- Escaneia pastas inteiras em busca de arquivos repetidos
- Três modos de comparação:
  1. **Nome + Tamanho** (rápido, 99% preciso)
  2. **Hash SHA-256** (100% preciso, mais lento)
  3. **Nome parecido** (ex: "foto (1).jpg" e "foto.jpg")

**O que mostra:**
- Lista de grupos de duplicatas
- Cada grupo: quantos arquivos, quanto espaço ocupam juntos
- Quanto espaço você **pode liberar**
- Miniatura + localização de cada arquivo

**Ações:**
- Selecionar duplicatas pra mandar pra lixeira
- "Selecionar as piores" (mais antigas, em pastas menos importantes)
- Mover duplicatas pra uma pasta "Duplicatas/" em vez de deletar
- Agendar escaneamento semanal

---

## 🖥️ Interface (Telas)

### Tela 1 — Dashboard (Resumo)
```
┌─────────────────────────────────────────────────────┐
│  🧹  DISKY                             🇧🇷 EN      │
│                                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────────────────┐ │
│  │ 📥 1.247 │  │ 🔁  342 │  │  💾 2.3 GB liberados │ │
│  │ arquivos  │  │ duplicatas│  │  essa semana       │ │
│  │ organiz.  │  │ encont. │  │                     │ │
│  └─────────┘  └─────────┘  └─────────────────────┘ │
│                                                     │
│  Últimas organizações:         │     │ Escanear     │
│  • NF-e.pdf → Documentos/      │  ▶  │ Duplicatas   │
│  • foto.jpg → Imagens/         │     │              │
│  • setup.exe → Instaladores/   │     │              │
│                                                     │
│  ⚙️ Configurações   📊 Estatísticas   🔍 Escanear   │
└─────────────────────────────────────────────────────┘
```

### Tela 2 — Organizador
```
┌─────────────────────────────────────────────────────┐
│  📥  Organizador de Downloads                       │
│                                                     │
│  Pastas monitoradas:                                 │
│  ✅  C:\Users\Pitoco\Downloads                      │
│  ✅  C:\Users\Pitoco\Desktop                        │
│  [➕ Adicionar pasta]                               │
│                                                     │
│  Regras:                         Ativo              │
│  ┌─────────────────────────────┐ ┌───┐             │
│  │ Documentos → *.pdf, *.docx  │ │ ON│             │
│  │ Imagens    → *.jpg, *.png   │ │ ON│             │
│  │ Instaladores → *.exe, *.msi │ │ ON│             │
│  │ [➕ Nova regra]               │ └───┘             │
│  └─────────────────────────────┘                    │
│                                                     │
│  [📂 ORGANIZAR TUDO AGORA]  [⏸️ Pausar Monitor]    │
└─────────────────────────────────────────────────────┘
```

### Tela 3 — Duplicatas
```
┌─────────────────────────────────────────────────────┐
│  🔁  Caçador de Duplicatas                         │
│                                                     │
│  💾 Espaço que pode liberar: 4.7 GB                 │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │ ☐ foto_vacina.jpg (3 cópias) → 12 MB         │   │
│  │ ☐ relatorio.pdf (5 cópias) → 8.2 MB          │   │
│  │ ☐ backup.zip (2 cópias) → 1.2 GB  🔴         │   │
│  │ ☐ musica.mp3 (4 cópias) → 28 MB              │   │
│  │ ☐ [Ver mais...]                              │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  [🔍 Escanear Agora] [🗑️ Limpar Selecionados]     │
│  ⏱ Último scan: hoje 14:32                        │
└─────────────────────────────────────────────────────┘
```

---

## 📊 UX / Experiência do Usuário

**Primeira execução (Wizard):**
1. "Oi! Vou organizar seus Downloads. Quer começar?"
2. Mostra quantos arquivos bagunçados existem
3. "Ativar monitor automático?" → Sim (recomendado)
4. "Quer escanear duplicatas também?" → Sim
5. Pronto! O app já começa a organizar em segundo plano

**Em segundo plano:**
- Ícone na bandeja do sistema 🧹
- Clique direito: "Abrir Disky" | "Organizar Agora" | "Pausar" | "Sair"
- Notificação quando organizar ou encontrar duplicatas pesadas

**Fluxo típico do usuário:**
1. Instala Disky
2. Wizard aparece, configura em 30 segundos
3. Esquece que o app existe
4. Meses depois: "nossa, meus Downloads tão arrumados!"
5. De vez em quando: abre, vê duplicatas, limpa com 1 clique

---

## 📋 Cronograma (estimado)

| Fase | O que | Tempo |
|---|---|---|
| **1** | Core: watcher + organizer + regras | 2 dias |
| **2** | Core: duplicate_finder | 2 dias |
| **3** | UI: Dashboard + abas | 2 dias |
| **4** | Integração Windows + bandeja | 1 dia |
| **5** | Wizard + primeiras configurações | 1 dia |
| **6** | Testes + .exe final | 1 dia |
| **Total** | **MVP funcional** | **~9 dias** |

---

## 💰 Monetização (opcional)

Modelo de **doação** (como você quer):
- Versão gratuita completa (sem limitação)
- Área no app: "Gostou? Paga um café pro PITOCO113 🇧🇷"
- Link pra PIX ou PayPal

**Diferenciais pagos que PODEM vir depois (v2):**
- Regras ilimitadas (gratuito: 10 regras)
- Escaneamento agendado avançado
- Tema personalizado

---

## 🚀 Por que Disky vai vingar?

1. **Problema universal** — literalmente TODO MUNDO tem Downloads bagunçado
2. **Zero esforço** — instala e esquece
3. **Resultado imediato** — na primeira execução já organiza tudo
4. **Vídeo viraliza fácil** — "organizei 3 anos de Downloads em 5 segundos"
5. **Concorrência fraca** — apps existentes são feios, pagos ou abandonados
6. **Você se torna dono de uma categoria** — "o app que arruma Downloads"

---

## ✅ Checklist MVP

- [ ] Monitoramento automático da pasta Downloads
- [ ] Regras padrão de organização (docs, imagens, etc.)
- [ ] Usuário pode criar regras próprias
- [ ] Organização retroativa ("Organizar Tudo")
- [ ] Escaneamento de duplicatas por nome + tamanho
- [ ] Escaneamento de duplicatas por hash SHA-256
- [ ] Lista de duplicatas com espaço que pode liberar
- [ ] Seleção + envio pra lixeira
- [ ] Dashboard com resumo
- [ ] Ícone na bandeja do sistema
- [ ] Wizard de primeira execução
- [ ] PT-BR + EN
- [ ] Marca PITOCO113 🇧🇷
- [ ] Atalho na área de trabalho
- [ ] .exe único publicável