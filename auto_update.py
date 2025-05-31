#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
from datetime import datetime

def run(command: str, check: bool = False) -> bool:
    """
    Executa um comando no shell, exibe a saída (stdout e stderr) e retorna True se 
    o comando teve exit code 0. Se check=True, encerra o script em caso de erro.
    """
    print(f"🔹 Executando: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    
    if result.returncode != 0:
        print(f"❌ Comando falhou com exit code {result.returncode}: '{command}'", file=sys.stderr)
        if check:
            print("Encerrando o script devido ao erro.", file=sys.stderr)
            sys.exit(result.returncode)
        return False
    
    return True

def main():
    # Gera a mensagem de commit com data/hora atuais
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    commit_msg = f"Atualização automática em {agora}"

    print("📥 Fazendo pull do repositório remoto...")
    # Se git pull falhar, interrompe o script
    run("git pull origin main", check=True)

    print("🗂️ Adicionando todos os arquivos no stage...")
    run("git add .", check=True)

    print("🔍 Verificando se há alterações para commit...")
    # git diff --staged --quiet retorna 0 se não houver diferenças, 1 se houver
    status = subprocess.run("git diff --staged --quiet", shell=True)
    if status.returncode == 0:
        print("⚠️ Nenhuma alteração detectada para commit.")
    else:
        print(f"💾 Fazendo commit com mensagem: '{commit_msg}'")
        run(f'git commit -m "{commit_msg}"', check=True)

    print("📤 Enviando para o repositório remoto...")
    run("git push origin main", check=True)

    # Agora, sobe a aplicação no Railway
    print("🚀 Executando 'railway up' para publicar a aplicação no Railway...")
    run("railway up", check=True)

    print("✅ Script concluído com sucesso!")

if __name__ == "__main__":
    main()
