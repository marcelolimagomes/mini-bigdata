#!/usr/bin/env python3
"""
recreate_stack.py - Recria toda a stack Big Data do zero

Este script:
1. Para e remove todos os containers
2. Remove volumes Docker
3. Apaga a pasta de dados
4. Recria a estrutura de diretórios
5. Sobe a stack completa
6. Valida os serviços
"""

import subprocess
import sys
import time
import shutil
from pathlib import Path


class Colors:
    """Cores ANSI para terminal"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color


def print_header(message):
    """Imprime cabeçalho formatado"""
    print(f"\n{Colors.CYAN}{'=' * 72}")
    print(f"  {message}")
    print(f"{'=' * 72}{Colors.NC}\n")


def print_success(message):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.GREEN}✅ {message}{Colors.NC}")


def print_error(message):
    """Imprime mensagem de erro"""
    print(f"{Colors.RED}❌ {message}{Colors.NC}")


def print_warning(message):
    """Imprime mensagem de aviso"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")


def print_info(message):
    """Imprime mensagem informativa"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.NC}")


def run_command(cmd, check=True, shell=True, capture_output=True):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        if check:
            raise
        return e


def confirm_action():
    """Solicita confirmação do usuário"""
    print()
    print(f"{Colors.CYAN}{'=' * 72}")
    print("           RECRIAÇÃO COMPLETA DA STACK MINI BIGDATA")
    print(f"{'=' * 72}{Colors.NC}")
    print()
    print(f"{Colors.YELLOW}⚠️  ATENÇÃO: Este script irá:{Colors.NC}")
    print()
    print("  1. ❌ Parar e remover TODOS os containers")
    print("  2. ❌ Remover TODOS os volumes Docker")
    print("  3. ❌ APAGAR todos os dados em: /media/marcelo/dados1/bigdata-docker")
    print("  4. ✅ Recriar a estrutura de diretórios")
    print("  5. ✅ Subir a stack completa novamente")
    print("  6. ✅ Validar os serviços")
    print()
    print(f"{Colors.RED}⚠️  TODOS OS DADOS SERÃO PERDIDOS!{Colors.NC}")
    print()
    print(f"{Colors.CYAN}{'=' * 72}{Colors.NC}")
    print()

    confirmacao = input("Tem certeza que deseja continuar? (digite 'SIM' para confirmar): ")
    if confirmacao != "SIM":
        print_warning("Operação cancelada pelo usuário")
        sys.exit(0)

    print()
    confirmacao_final = input("Última chance! Digite 'CONFIRMO' para prosseguir: ")
    if confirmacao_final != "CONFIRMO":
        print_warning("Operação cancelada pelo usuário")
        sys.exit(0)


def stop_and_remove_containers():
    """Para e remove todos os containers"""
    print_header("ETAPA 1/6: Parando e removendo containers")

    print_info("Parando todos os containers...")
    run_command("docker compose down --remove-orphans -v", check=False)
    print_success("Containers parados e removidos")

    print_info("Removendo containers órfãos...")
    container_filters = [
        "superset", "airflow", "spark", "trino",
        "hive", "minio", "postgres", "redis"
    ]

    for filter_name in container_filters:
        run_command(
            f"docker ps -a --filter 'name={filter_name}' --format '{{{{.ID}}}}' | xargs -r docker rm -f",
            check=False
        )

    print_success("Containers órfãos removidos")


def remove_docker_volumes():
    """Remove volumes Docker"""
    print_header("ETAPA 2/6: Removendo volumes Docker")

    print_info("Removendo volumes do projeto...")
    run_command(
        "docker volume ls --filter 'name=mini-bigdata' --format '{{.Name}}' | xargs -r docker volume rm -f",
        check=False
    )
    print_success("Volumes Docker removidos")

    print_info("Limpando volumes órfãos...")
    run_command("docker volume prune -f", check=False)
    print_success("Volumes órfãos removidos")


def remove_data_directory():
    """Remove pasta de dados"""
    print_header("ETAPA 3/6: Apagando pasta de dados")

    data_root = Path("/media/marcelo/dados1/bigdata-docker")

    if data_root.exists():
        print_warning(f"Removendo todo o conteúdo de: {data_root}")
        print_info("Aguarde, isso pode levar alguns segundos...")

        try:
            shutil.rmtree(data_root)
            print_success("Pasta de dados removida")
        except PermissionError:
            print_info("Necessário permissões de administrador para remover...")
            run_command(f"sudo rm -rf {data_root}")
            print_success("Pasta de dados removida (com sudo)")
    else:
        print_info("Pasta de dados não existe (já foi removida)")


def create_directory_structure():
    """Recria estrutura de diretórios"""
    print_header("ETAPA 4/6: Recriando estrutura de diretórios")

    data_root = Path("/media/marcelo/dados1/bigdata-docker")

    print_info(f"Criando diretório raiz: {data_root}")
    try:
        data_root.mkdir(parents=True, exist_ok=True)
        print_success("Diretório raiz criado")
    except PermissionError:
        print_info("Criando com sudo...")
        run_command(f"sudo mkdir -p {data_root}")
        run_command(f"sudo chown -R $USER:$USER {data_root}")
        print_success("Diretório raiz criado (com sudo)")

    print_info("Criando subdiretórios...")
    subdirs = [
        "postgres", "minio", "hive", "trino", "superset", "redis",
        "airflow/dags", "airflow/logs", "airflow/plugins",
        "spark/master", "spark/worker"
    ]

    for subdir in subdirs:
        (data_root / subdir).mkdir(parents=True, exist_ok=True)

    print_success("Subdiretórios criados")

    print_info("Configurando permissões...")
    run_command(f"chmod -R 777 {data_root}", check=False)
    print_success("Permissões configuradas")

    print_info("Ajustando permissões específicas do Airflow...")
    airflow_dir = data_root / "airflow"
    try:
        run_command(f"chown -R 50000:0 {airflow_dir}", check=False)
        print_success("Permissões do Airflow configuradas")
    except:
        run_command(f"sudo chown -R 50000:0 {airflow_dir}")
        print_success("Permissões do Airflow configuradas (com sudo)")


def start_stack():
    """Sobe a stack completa"""
    print_header("ETAPA 5/6: Subindo a stack completa")

    print_info("Verificando arquivo .env...")
    if not Path(".env").exists():
        print_error("Arquivo .env não encontrado!")
        sys.exit(1)
    print_success("Arquivo .env encontrado")

    print_info("Iniciando serviços com docker compose...")
    run_command("docker compose up -d", capture_output=False)
    print_success("Comando de inicialização executado")

    print_info("Aguardando serviços inicializarem (30 segundos)...")
    time.sleep(30)


def validate_services():
    """Valida os serviços"""
    print_header("ETAPA 6/6: Validando serviços")

    print_info("Verificando status dos containers...")
    print()
    run_command("docker compose ps", capture_output=False)
    print()

    # Verificar serviços críticos
    services = [
        "postgres", "redis", "minio", "hive-metastore",
        "spark-master", "spark-worker", "trino", "superset",
        "airflow-webserver", "airflow-scheduler"
    ]

    failed_services = []

    result = run_command("docker compose ps", check=False)
    output = result.stdout if result.returncode == 0 else ""

    for service in services:
        if service in output and "Up" in output:
            print_success(f"Serviço {service} está rodando")
        else:
            print_error(f"Serviço {service} NÃO está rodando")
            failed_services.append(service)

    return failed_services


def print_summary(failed_services):
    """Imprime resumo final"""
    print_header("RESUMO DA RECRIAÇÃO")

    print()
    print(f"{Colors.CYAN}📊 Status dos Serviços:{Colors.NC}")
    print()

    # Obter lista de serviços rodando
    result = run_command("docker compose ps", check=False)
    running_services = result.stdout if result.returncode == 0 else ""

    # Tabela de serviços
    services_info = [
        ("postgres", "localhost:5432"),
        ("redis", "localhost:6379"),
        ("minio", "http://localhost:9001"),
        ("hive-metastore", "localhost:9083"),
        ("spark-master", "http://localhost:8080"),
        ("spark-worker", "http://localhost:8081"),
        ("trino", "http://localhost:8085"),
        ("superset", "http://localhost:8088"),
        ("airflow-webserver", "http://localhost:8082"),
        ("airflow-scheduler", "-"),
    ]

    print(f"{'SERVIÇO':<20} {'STATUS':<15} {'URL':<40}")
    print("─" * 72)

    for service, url in services_info:
        if service in running_services and "Up" in running_services:
            status = f"{Colors.GREEN}✅ Rodando{Colors.NC}"
        else:
            status = f"{Colors.RED}❌ Parado{Colors.NC}"
        print(f"{service:<20} {status:<24} {url:<40}")

    print()
    print(f"{Colors.CYAN}🔑 Credenciais de Acesso:{Colors.NC}")
    print()
    print("  Airflow:  http://localhost:8082")
    print("    Usuário: airflow")
    print("    Senha: airflow")
    print()
    print("  Superset: http://localhost:8088")
    print("    Usuário: admin")
    print("    Senha: admin")
    print()
    print("  MinIO:    http://localhost:9001")
    print("    Usuário: minioadmin")
    print("    Senha: minioadmin123")
    print()

    if not failed_services:
        print_success("STACK RECRIADA COM SUCESSO! 🎉")
        print()
        print(f"{Colors.GREEN}Todos os serviços estão rodando corretamente!{Colors.NC}")
        return 0
    else:
        print_warning("STACK RECRIADA COM AVISOS ⚠️")
        print()
        print(f"{Colors.YELLOW}Os seguintes serviços apresentaram problemas:{Colors.NC}")
        for service in failed_services:
            print(f"  - {service}")
        print()
        print("Execute 'docker compose logs <serviço>' para mais detalhes")
        return 1


def main():
    """Função principal"""
    # Mudar para o diretório do projeto
    project_root = Path(__file__).parent.parent
    import os
    os.chdir(project_root)

    # Solicitar confirmação
    if "--auto" not in sys.argv:
        confirm_action()

    try:
        # Executar etapas
        stop_and_remove_containers()
        remove_docker_volumes()
        remove_data_directory()
        create_directory_structure()
        start_stack()
        failed_services = validate_services()

        # Imprimir resumo
        exit_code = print_summary(failed_services)

        print()
        print(f"{Colors.CYAN}{'=' * 72}{Colors.NC}")
        print()

        sys.exit(exit_code)

    except KeyboardInterrupt:
        print()
        print_warning("Operação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print()
        print_error(f"Erro durante execução: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
