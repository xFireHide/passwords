import re
import math
from dataclasses import dataclass, field

from api_hibp import contagem_vazamentos_hibp


REGEX_CARACTERES_ESPECIAIS = r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]"


SENHAS_COMUNS = {
    "123456", "123456789", "12345678", "12345", "1234567",
    "1234567890", "654321", "123321", "000000", "111111",
    "121212", "696969", "666666", "7777777", "102030", "010203",
    "qwerty", "qwertyuiop", "abc123", "qazwsx", "123qwe", "1qaz2wsx",
    "senha", "senha1", "senha12", "senha123", "minhasenha", "suasenha",
    "brasil", "brasil123", "brasilia",
    "usuario", "visitante", "administrador", "acesso", "entrada",
    "mudar123", "alterar123", "novasenha", "bemvindo", "obrigado",
    "admin", "root", "password", "pass", "test", "teste", "guest",
}

PADROES_TECLADO = [
    "qwerty", "asdfgh", "zxcvbn", "qweasd", "123456",
    "098765", "poiuyt", "lkjhgf", "mnbvcx",
]

LEET = {"@": "a", "3": "e", "1": "i", "0": "o", "5": "s", "7": "t", "$": "s"}


@dataclass
class ResultadoAnalise:
    senha: str
    pontuacao: int = 0
    forca: str = ""
    entropia: float = 0.0
    problemas: list[str] = field(default_factory=list)
    sugestoes: list[str] = field(default_factory=list)
    detalhes: dict = field(default_factory=dict)


def calcular_entropia(senha: str) -> float:
    espaco = 0
    if re.search(r"[a-z]", senha):
        espaco += 26
    if re.search(r"[A-Z]", senha):
        espaco += 26
    if re.search(r"\d", senha):
        espaco += 10
    if re.search(REGEX_CARACTERES_ESPECIAIS, senha):
        espaco += 32
    if espaco == 0:
        return 0.0
    return len(senha) * math.log2(espaco)


def desleetspeak(senha: str) -> str:
    resultado = senha.lower()
    for char, equiv in LEET.items():
        resultado = resultado.replace(char, equiv)
    return resultado


def verificar_comprimento(senha: str, resultado: ResultadoAnalise):
    tamanho = len(senha)
    resultado.detalhes["comprimento"] = tamanho
    if tamanho < 8:
        resultado.problemas.append(f"Muito curta ({tamanho} caracteres)")
        resultado.sugestoes.append("Use pelo menos 12 caracteres")
    elif tamanho < 12:
        resultado.pontuacao += 10
        resultado.sugestoes.append("Prefira 16+ caracteres para maior segurança")
    elif tamanho < 16:
        resultado.pontuacao += 20
    else:
        resultado.pontuacao += 30


def verificar_complexidade(senha: str, resultado: ResultadoAnalise):
    tem_minuscula = bool(re.search(r"[a-z]", senha))
    tem_maiuscula = bool(re.search(r"[A-Z]", senha))
    tem_numero    = bool(re.search(r"\d", senha))
    tem_especial = bool(re.search(REGEX_CARACTERES_ESPECIAIS, senha))

    resultado.detalhes["complexidade"] = {
        "minusculas": tem_minuscula,
        "maiusculas": tem_maiuscula,
        "numeros":    tem_numero,
        "especiais":  tem_especial,
    }

    categorias = sum([tem_minuscula, tem_maiuscula, tem_numero, tem_especial])

    if categorias == 1:
        resultado.problemas.append("Usa apenas um tipo de caractere")
    if not tem_maiuscula:
        resultado.sugestoes.append("Adicione letras maiúsculas (A-Z)")
    if not tem_numero:
        resultado.sugestoes.append("Adicione números (0-9)")
    if not tem_especial:
        resultado.sugestoes.append("Adicione símbolos (!@#$%...)")

    resultado.pontuacao += categorias * 10


def verificar_repeticoes(senha: str, resultado: ResultadoAnalise):
    if re.search(r"(.)\1{2,}", senha):
        resultado.problemas.append("Contém 3+ caracteres repetidos seguidos")
        resultado.sugestoes.append("Evite repetições como 'aaa' ou '111'")
        resultado.pontuacao -= 10


def verificar_sequencias(senha: str, resultado: ResultadoAnalise):
    senha_lower = senha.lower()

    for i in range(len(senha) - 2):
        if senha[i:i+3].isdigit():
            a, b, c = int(senha[i]), int(senha[i+1]), int(senha[i+2])
            if (b - a == 1 and c - b == 1) or (a - b == 1 and b - c == 1):
                resultado.problemas.append("Contém sequência numérica (ex: 123 ou 987)")
                resultado.sugestoes.append("Evite sequências numéricas simples")
                resultado.pontuacao -= 10
                break

    alfabeto = "abcdefghijklmnopqrstuvwxyz"
    for i in range(len(senha_lower) - 2):
        trecho = senha_lower[i:i+3]
        if trecho in alfabeto or trecho[::-1] in alfabeto:
            resultado.problemas.append("Contém sequência alfabética (ex: abc ou xyz)")
            resultado.pontuacao -= 10
            break


def verificar_padroes_teclado(senha: str, resultado: ResultadoAnalise):
    senha_lower = senha.lower()
    for padrao in PADROES_TECLADO:
        if padrao in senha_lower or padrao[::-1] in senha_lower:
            resultado.problemas.append(f"Contém padrão de teclado: '{padrao}'")
            resultado.sugestoes.append("Evite padrões de teclado como 'qwerty' ou 'asdf'")
            resultado.pontuacao -= 15
            break


def verificar_senha_comum(senha: str, resultado: ResultadoAnalise):
    senha_lower = senha.lower()
    senha_desleet = desleetspeak(senha)

    if senha_lower in SENHAS_COMUNS or senha_desleet in SENHAS_COMUNS:
        resultado.problemas.append("Senha está na lista das mais usadas no mundo!")
        resultado.sugestoes.append(
            "Nunca use senhas óbvias (ex.: sequências numéricas, 'senha123', padrões de teclado)"
        )
        resultado.pontuacao -= 50


def verificar_informacoes_pessoais(senha: str, resultado: ResultadoAnalise):
    senha_lower = senha.lower()
    padroes_pessoais = [
        (r"\b(19|20)\d{2}\b", "ano (ex: 1995, 2001)"),
        (r"\b\d{2}/\d{2}\b",  "data (ex: 12/05)"),
        (r"\b\d{5,}\b",       "número longo (CPF, telefone?)"),
    ]
    for padrao, descricao in padroes_pessoais:
        if re.search(padrao, senha_lower):
            resultado.problemas.append(f"Possível dado pessoal detectado: {descricao}")
            resultado.sugestoes.append("Evite datas de nascimento e documentos pessoais")
            resultado.pontuacao -= 10
            break


def verificar_hibp(senha: str, resultado: ResultadoAnalise):
    count = contagem_vazamentos_hibp(senha)
    if count is None:
        resultado.detalhes["hibp_falhou"] = True
        resultado.sugestoes.append(
            "Consulta Have I Been Pwned indisponível (rede ou serviço). "
            "Verifique depois em https://haveibeenpwned.com/Passwords"
        )
        return

    resultado.detalhes["hibp_contagem"] = count
    if count > 0:
        ocorr = "ocorrência" if count == 1 else "ocorrências"
        resultado.problemas.append(
            f"Senha aparece em vazamentos reais (HIBP: {count:,} {ocorr})"
        )
        resultado.sugestoes.append(
            "Troque esta senha em todos os serviços; use senhas únicas e um gerenciador"
        )
        resultado.pontuacao -= 40


def calcular_forca(pontuacao: int, entropia: float) -> str:
    if pontuacao < 10 or entropia < 28:
        return "MUITO FRACA"
    elif pontuacao < 30 or entropia < 40:
        return "FRACA"
    elif pontuacao < 50 or entropia < 55:
        return "MODERADA"
    elif pontuacao < 70 or entropia < 70:
        return "FORTE"
    else:
        return "MUITO FORTE"


def analisar_senha(senha: str) -> ResultadoAnalise:
    resultado = ResultadoAnalise(senha=senha)

    verificar_comprimento(senha, resultado)
    verificar_complexidade(senha, resultado)
    verificar_repeticoes(senha, resultado)
    verificar_sequencias(senha, resultado)
    verificar_padroes_teclado(senha, resultado)
    verificar_senha_comum(senha, resultado)
    verificar_informacoes_pessoais(senha, resultado)
    verificar_hibp(senha, resultado)

    resultado.entropia = calcular_entropia(senha)
    resultado.pontuacao = max(0, min(100, resultado.pontuacao))
    resultado.forca = calcular_forca(resultado.pontuacao, resultado.entropia)

    return resultado


def exibir_resultado(r: ResultadoAnalise):
    sep = "─" * 50

    print(f"\n{sep}")
    print(f"  RESULTADO DA ANÁLISE")
    print(sep)
    print(f"  Força      : {r.forca}")
    print(f"  Pontuação  : {r.pontuacao}/100")
    print(f"  Entropia   : {r.entropia:.1f} bits")
    print(f"  Comprimento: {r.detalhes.get('comprimento', 0)} caracteres")

    comp = r.detalhes.get("complexidade", {})
    tipos = []
    if comp.get("minusculas"): tipos.append("a-z")
    if comp.get("maiusculas"): tipos.append("A-Z")
    if comp.get("numeros"):    tipos.append("0-9")
    if comp.get("especiais"):  tipos.append("!@#")
    print(f"  Tipos usados: {', '.join(tipos) if tipos else 'nenhum'}")

    if "hibp_contagem" in r.detalhes:
        c = r.detalhes["hibp_contagem"]
        if c > 0:
            ocorr = "ocorrência" if c == 1 else "ocorrências"
            print(f"  Have I Been Pwned: encontrada ({c:,} {ocorr})")
        else:
            print("  Have I Been Pwned: não consta no índice de senhas vazadas")
    elif r.detalhes.get("hibp_falhou"):
        print("  Have I Been Pwned: consulta não realizada")

    if r.problemas:
        print(f"\n  ⚠  PROBLEMAS ENCONTRADOS:")
        for p in r.problemas:
            print(f"     • {p}")

    if r.sugestoes:
        print(f"\n  💡 SUGESTÕES:")
        for s in set(r.sugestoes):
            print(f"     • {s}")

    print(f"\n  📖 Sobre a entropia:")
    print(f"     < 28 bits  → quebrável instantaneamente")
    print(f"     28-40 bits → vulnerável a ataques de dicionário")
    print(f"     40-55 bits → razoável para uso pessoal")
    print(f"     55-70 bits → boa para contas importantes")
    print(f"     > 70 bits  → excelente (recomendado para tudo)")
    print(sep)
