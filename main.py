import getpass
import os
import sys

from analise import analisar_senha, exibir_resultado
from gerador import (
    exibir_senha_gerada,
    gerar_senha,
    perguntar_sim_nao,
    perguntar_tamanho,
)


def ler_senha_com_mascara(prompt: str) -> str:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return getpass.getpass(prompt)

    if sys.platform == "win32":
        return _ler_senha_windows(prompt)
    try:
        import termios
    except ImportError:
        return getpass.getpass(prompt)
    return _ler_senha_unix(prompt)


def _ler_senha_windows(prompt: str) -> str:
    import msvcrt

    sys.stdout.write(prompt)
    sys.stdout.flush()
    chars: list[str] = []
    while True:
        ch = msvcrt.getwch()
        if ch in ("\r", "\n"):
            sys.stdout.write("\r\n")
            sys.stdout.flush()
            break
        if ch in ("\x08", "\x7f"):
            if chars:
                chars.pop()
                sys.stdout.write("\b \b")
                sys.stdout.flush()
            continue
        if ch == "\x03":
            raise KeyboardInterrupt
        if ch == "\x04" and not chars:
            raise EOFError
        chars.append(ch)
        sys.stdout.write("*")
        sys.stdout.flush()
    return "".join(chars)


def _ler_senha_unix(prompt: str) -> str:
    import termios
    import tty

    sys.stdout.write(prompt)
    sys.stdout.flush()
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    pending = bytearray()
    chars: list[str] = []
    try:
        tty.setraw(fd)
        while True:
            b = os.read(fd, 1)
            if not b:
                break
            byte = b[0]
            if byte in (13, 10):
                sys.stdout.write("\r\n")
                sys.stdout.flush()
                break
            if byte == 3:
                raise KeyboardInterrupt
            if byte == 4 and not chars and not pending:
                raise EOFError
            if byte in (127, 8):
                if pending:
                    pending.pop()
                elif chars:
                    chars.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue

            pending.append(byte)
            try:
                text = pending.decode("utf-8")
            except UnicodeDecodeError:
                if len(pending) > 6:
                    pending.clear()
                continue
            pending.clear()
            chars.extend(text)
            sys.stdout.write("*" * len(text))
            sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return "".join(chars)


def main():
    print("\n" + "═" * 50)
    print("ANALISADOR DE SENHAS")
    print("═" * 50)

    while True:
        print()
        print("  [1] Analisar uma senha")
        print("  [2] Gerar uma senha nova")
        print("  [3] Sair")
        print()

        try:
            opcao = input("  Escolha uma opção: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Saindo...")
            break

        if opcao == "1":
            try:
                senha = ler_senha_com_mascara("  Digite a senha para analisar: ")
            except (KeyboardInterrupt, EOFError):
                print("\n\n  Saindo...")
                break

            if not senha:
                print("  ⚠  Digite uma senha válida.")
                continue

            resultado = analisar_senha(senha)
            exibir_resultado(resultado)

        elif opcao == "2":
            tamanho = perguntar_tamanho()
            tem_maiuscula = perguntar_sim_nao("Incluir letras maiúsculas?")
            tem_numero = perguntar_sim_nao("Incluir números?")
            tem_simbolo = perguntar_sim_nao("Incluir símbolos?")

            senha_nova = gerar_senha(
                tamanho=tamanho,
                incluir_maiusculas=tem_maiuscula,
                incluir_numeros=tem_numero,
                incluir_simbolos=tem_simbolo,
            )

            exibir_senha_gerada(senha_nova)

            resultado = analisar_senha(senha_nova)
            exibir_resultado(resultado)

        elif opcao == "3":
            print("  Até logo!")
            break

        else:
            print("  ⚠  Opção inválida. Escolha 1, 2 ou 3.")


if __name__ == "__main__":
    main()
