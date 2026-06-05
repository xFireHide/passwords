# 🔥 FirePasswords

Ferramenta de linha de comando (CLI) para **analisar a força de senhas** e **gerar senhas seguras**. Mostra pontuação, entropia, problemas detectados e sugestões — e ainda verifica se a senha já apareceu em vazamentos reais usando o [Have I Been Pwned](https://haveibeenpwned.com/Passwords), tudo sem enviar a senha pela rede.

Escrita em **Python puro**, sem nenhuma dependência externa.

---

## Índice

- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Uso](#instalação-e-uso)
- [Como funciona](#como-funciona)
  - [Estrutura do projeto](#estrutura-do-projeto)
  - [Análise de senha](#análise-de-senha)
  - [Entropia](#entropia)
  - [Pontuação e força](#pontuação-e-força)
  - [Verificação no Have I Been Pwned (k-anonymity)](#verificação-no-have-i-been-pwned-k-anonymity)
  - [Geração de senha](#geração-de-senha)
  - [Leitura mascarada da senha](#leitura-mascarada-da-senha)
- [Privacidade e segurança](#privacidade-e-segurança)
- [Solução de problemas](#solução-de-problemas)
- [Licença](#licença)

---

## Funcionalidades

- 🔎 **Análise de força** de uma senha com pontuação de 0 a 100 e cálculo de entropia em bits.
- 🧨 **Detecção de fraquezas comuns**: comprimento curto, falta de variedade de caracteres, repetições, sequências numéricas/alfabéticas, padrões de teclado, senhas óbvias e possíveis dados pessoais (datas, anos, números longos).
- 🌐 **Checagem de vazamentos** no Have I Been Pwned usando *k-anonymity* — a senha **nunca** é enviada, apenas um prefixo do hash SHA-1.
- 🎲 **Gerador de senhas** criptograficamente seguro (módulo `secrets`), com tamanho e categorias de caracteres configuráveis.
- ⌨️ **Entrada mascarada** da senha no terminal (mostra `*`), com suporte a Unix e Windows.
- 💡 **Sugestões práticas** de melhoria para cada problema encontrado.

---

## Tecnologias

- **Linguagem**: Python 3.10+ (usa sintaxe de tipos `int | None` e `list[str]`)
- **Dependências externas**: nenhuma — somente a biblioteca padrão (`secrets`, `string`, `re`, `math`, `hashlib`, `urllib`, `getpass`, `termios`/`msvcrt`, `dataclasses`)
- **API externa**: [Pwned Passwords](https://haveibeenpwned.com/API/v3#PwnedPasswords) (opcional; o programa funciona offline se a consulta falhar)

---

## Pré-requisitos

- **Python 3.10 ou superior** instalado.
- Acesso à internet **apenas** para a verificação no Have I Been Pwned (opcional — sem rede, a análise continua funcionando normalmente).

Verifique sua versão do Python:

```bash
python3 --version
```

---

## Instalação e Uso

### 1. Clone o repositório

```bash
git clone https://github.com/xFireHide/FirePasswords.git
cd FirePasswords
```

### 2. Execute

Não há nada para instalar — basta rodar o ponto de entrada:

```bash
python3 main.py
```

Você verá o menu interativo:

```
══════════════════════════════════════════════════
ANALISADOR DE SENHAS
══════════════════════════════════════════════════

  [1] Analisar uma senha
  [2] Gerar uma senha nova
  [3] Sair

  Escolha uma opção:
```

### Opção 1 — Analisar uma senha

Digite uma senha (ela aparece mascarada como `*`). O programa mostra força, pontuação, entropia, tipos de caracteres usados, resultado do Have I Been Pwned, problemas e sugestões. Exemplo de saída:

```
──────────────────────────────────────────────────
  RESULTADO DA ANÁLISE
──────────────────────────────────────────────────
  Força      : MUITO FORTE
  Pontuação  : 90/100
  Entropia   : 95.3 bits
  Comprimento: 16 caracteres
  Tipos usados: a-z, A-Z, 0-9, !@#
  Have I Been Pwned: não consta no índice de senhas vazadas
  ...
```

### Opção 2 — Gerar uma senha nova

O programa pergunta o tamanho (8–128) e quais categorias incluir (maiúsculas, números, símbolos). Letras minúsculas estão sempre presentes. A senha gerada é exibida e **automaticamente analisada** em seguida.

---

## Como funciona

### Estrutura do projeto

```
FirePasswords/
├── main.py        # Ponto de entrada: menu interativo e leitura mascarada da senha
├── analise.py     # Motor de análise: entropia, pontuação, regras de fraqueza, HIBP
├── gerador.py     # Geração de senhas seguras e prompts de configuração
├── api_hibp.py    # Cliente Have I Been Pwned via k-anonymity (SHA-1 + range API)
└── .gitattributes
```

Fluxo geral:

```
main.py  ──(opção 1)──►  analise.analisar_senha()  ──►  exibir_resultado()
   │                            │
   │                            └──►  api_hibp.contagem_vazamentos_hibp()
   │
   └──(opção 2)──►  gerador.gerar_senha()  ──►  analise.analisar_senha()
```

### Análise de senha

`analise.analisar_senha()` (em `analise.py`) executa uma bateria de verificações independentes, cada uma ajustando a pontuação e acumulando problemas/sugestões em um objeto `ResultadoAnalise`:

| Verificação | Função | Efeito na pontuação |
| --- | --- | --- |
| Comprimento | `verificar_comprimento` | +10 a +30 (curtas demais não somam) |
| Variedade de caracteres | `verificar_complexidade` | +10 por categoria (a-z, A-Z, 0-9, símbolos) |
| Caracteres repetidos (`aaa`) | `verificar_repeticoes` | −10 |
| Sequências (`123`, `abc`) | `verificar_sequencias` | −10 |
| Padrões de teclado (`qwerty`) | `verificar_padroes_teclado` | −15 |
| Senha comum/óbvia | `verificar_senha_comum` | −50 |
| Possível dado pessoal | `verificar_informacoes_pessoais` | −10 |
| Vazamento real (HIBP) | `verificar_hibp` | −40 |

A verificação de senhas comuns também aplica **desleetspeak** (`verificar_senha_comum` → `desleetspeak`), então variações como `s3nh@` são reconhecidas como `senha`.

A pontuação final é limitada ao intervalo **0–100**.

### Entropia

`calcular_entropia()` estima a entropia em bits a partir do tamanho do espaço de caracteres:

```
entropia = comprimento × log2(tamanho_do_alfabeto)
```

Tamanhos de alfabeto considerados: minúsculas (26), maiúsculas (26), dígitos (10) e símbolos (32). Guia de referência exibido ao final de cada análise:

| Entropia | Significado |
| --- | --- |
| < 28 bits | quebrável instantaneamente |
| 28–40 bits | vulnerável a ataques de dicionário |
| 40–55 bits | razoável para uso pessoal |
| 55–70 bits | boa para contas importantes |
| > 70 bits | excelente (recomendado para tudo) |

### Pontuação e força

`calcular_forca()` combina pontuação **e** entropia (usa o pior dos dois) para classificar:

| Força | Critério |
| --- | --- |
| MUITO FRACA | pontuação < 10 ou entropia < 28 |
| FRACA | pontuação < 30 ou entropia < 40 |
| MODERADA | pontuação < 50 ou entropia < 55 |
| FORTE | pontuação < 70 ou entropia < 70 |
| MUITO FORTE | acima disso |

### Verificação no Have I Been Pwned (k-anonymity)

`api_hibp.contagem_vazamentos_hibp()` consulta a [Pwned Passwords Range API](https://haveibeenpwned.com/API/v3#PwnedPasswords) de forma que **a senha nunca sai da sua máquina**:

1. Calcula o **SHA-1** da senha.
2. Envia apenas os **5 primeiros caracteres** do hash para `https://api.pwnedpasswords.com/range/{prefixo}`.
3. A API responde com todos os sufixos de hash que compartilham aquele prefixo (centenas de resultados).
4. O programa procura **localmente** o sufixo correspondente e lê a contagem de vazamentos.

Detalhes técnicos:

- Cabeçalho `Add-Padding: true` para mascarar o tamanho real da resposta.
- Timeout padrão de **12 segundos**.
- Retorna `None` em caso de falha de rede (a análise prossegue, apenas sem o dado do HIBP).

### Geração de senha

`gerador.gerar_senha()` usa o módulo **`secrets`** (gerador criptograficamente seguro, adequado para senhas):

- Garante **pelo menos um caractere de cada categoria selecionada** (minúscula sempre incluída).
- Preenche o restante a partir do conjunto completo de caracteres permitidos.
- Embaralha o resultado com `secrets.SystemRandom().shuffle()`.
- Se o tamanho pedido for menor que o número de categorias obrigatórias, ele é elevado automaticamente.

### Leitura mascarada da senha

`main.ler_senha_com_mascara()` exibe `*` enquanto você digita, com implementações específicas por plataforma:

- **Unix/macOS**: modo *raw* via `termios`/`tty`, com tratamento correto de caracteres multibyte (UTF-8) e backspace.
- **Windows**: leitura caractere a caractere via `msvcrt`.
- **Fallback**: `getpass.getpass()` quando a entrada/saída não é um terminal interativo (ex.: pipes, redirecionamento).

---

## Privacidade e segurança

- ✅ **Senhas nunca são enviadas pela rede.** A checagem de vazamento usa k-anonymity: só viaja um prefixo de 5 caracteres do hash SHA-1.
- ✅ **Geração com `secrets`**, não `random` — apropriado para uso criptográfico.
- ✅ **Sem armazenamento**: nenhuma senha é gravada em disco ou em log pelo programa.
- ⚠️ Cuidado com o histórico do shell e com quem observa sua tela ao digitar; a máscara `*` ajuda, mas não substitui um ambiente confiável.

---

## Solução de problemas

**`SyntaxError` ao iniciar**
Provavelmente você está usando Python < 3.10. A sintaxe de tipos `int | None` exige **Python 3.10+**. Verifique com `python3 --version` e atualize se necessário.

**"Have I Been Pwned: consulta não realizada"**
A consulta de vazamentos falhou (sem internet, firewall ou serviço indisponível). É esperado e não bloqueia a análise — o restante do resultado continua válido. Você pode verificar manualmente em <https://haveibeenpwned.com/Passwords>.

**A senha não aparece mascarada / comportamento estranho da entrada**
Ao rodar via pipe ou redirecionamento (entrada não interativa), o programa cai para `getpass`, que pode não exibir `*`. Para a experiência completa, rode diretamente em um terminal.

**Acentuação ou caracteres especiais exibidos errados**
Garanta que seu terminal esteja em UTF-8. No Windows, prefira o Windows Terminal.

---

## Licença

Nenhuma licença foi definida para este projeto até o momento. Caso pretenda distribuí-lo ou aceitar contribuições, adicione um arquivo `LICENSE` (por exemplo, MIT) à raiz do repositório.
