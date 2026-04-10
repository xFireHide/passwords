import secrets
import string


def gerar_senha(tamanho=16, incluir_maiusculas=True, incluir_numeros=True, incluir_simbolos=True):
    chars_disponiveis = string.ascii_lowercase
    obrigatorios = [secrets.choice(string.ascii_lowercase)]

    if incluir_maiusculas:
        chars_disponiveis += string.ascii_uppercase
        obrigatorios.append(secrets.choice(string.ascii_uppercase))

    if incluir_numeros:
        chars_disponiveis += string.digits
        obrigatorios.append(secrets.choice(string.digits))

    if incluir_simbolos:
        chars_disponiveis += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        obrigatorios.append(secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))

    if tamanho < len(obrigatorios):
        tamanho = len(obrigatorios)

    restante = tamanho - len(obrigatorios)
    for _ in range(restante):
        obrigatorios.append(secrets.choice(chars_disponiveis))

    secrets.SystemRandom().shuffle(obrigatorios)

    return "".join(obrigatorios)


def exibir_senha_gerada(senha: str):
    sep = "─" * 41

    print(f"\n{sep}")
    print(f"  SENHA GERADA")
    print(sep)
    print(f"  {senha}")
    print()
    print(f"  Copiando manualmente? Confira cada")
    print(f"  caractere com cuidado.")
    print(sep)


def perguntar_sim_nao(pergunta):
    while True:
        resposta = input(f"  {pergunta} (s/n): ").strip().lower()
        if resposta in ("s", "n"):
            return resposta == "s"
        print("  ⚠  Responda com 's' ou 'n'.")


def perguntar_tamanho():
    while True:
        try:
            valor = int(input("  Tamanho da senha (8-128): ").strip())
            if 8 <= valor <= 128:
                return valor
            print("  ⚠  Escolha um valor entre 8 e 128.")
        except ValueError:
            print("  ⚠  Digite um número válido.")
