import subprocess
from datetime import datetime

def run(command):
    """Executa comandos shell e mostra saída."""
    print(f"🔹 {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    return result.returncode == 0

def main():
    # Mensagem automática com data/hora
    data = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    commit_msg = f"Atualização automática em {data}"

    print("📥 Fazendo pull do repositório remoto...")
    run("git pull origin main")

    print("🗂️ Adicionando todos os arquivos...")
    run("git add .")

    print("🔍 Verificando se há alterações para commit...")
    status = subprocess.run("git diff --staged --quiet", shell=True)
    if status.returncode == 0:
        print("⚠️ Nenhuma alteração detectada para commit.")
    else:
        print(f"💾 Fazendo commit com mensagem: '{commit_msg}'")
        run(f'git commit -m "{commit_msg}"')

    print("📤 Enviando para o repositório remoto...")
    run("git push origin main")

    print("✅ Tudo pronto!")

if __name__ == "__main__":
    main()
