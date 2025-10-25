#!/usr/bin/env python3
"""
full_setup.py - Setup completo e automatizado da stack Big Data

Este script executa todo o processo de setup:
1. Criação da estrutura de diretórios
2. Limpeza do ambiente Docker
3. Build das imagens personalizadas
4. Inicialização dos serviços em ordem
5. Validação dos serviços
6. Configuração automática (MinIO, Trino, Superset)
"""

import subprocess
import sys
import time
import os
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
    print(f"\n{Colors.CYAN}{'=' * 70}")
    print(f"  {message}")
    print(f"{'=' * 70}{Colors.NC}\n")


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


def run_command(cmd, description, check=True, shell=True, timeout=None):
    """Executa comando e retorna resultado"""
    print_info(description)
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            check=check,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print_error(f"Timeout ao executar: {description}")
        return False
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Erro ao executar: {description}")
            print_error(f"Saída: {e.stderr}")
        return False
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        return False


def create_directory_structure():
    """Cria estrutura de diretórios"""
    print_header("ETAPA 1/7: Criando estrutura de diretórios")

    data_root = Path("/media/marcelo/dados1/bigdata-docker")

    # Criar diretório raiz se não existir
    if not data_root.exists():
        print_warning(f"Diretório {data_root} não existe. Criando...")
        try:
            data_root.mkdir(parents=True, exist_ok=True)
            run_command(f"sudo chown -R $USER:$USER {data_root}", "Ajustando permissões")
        except Exception as e:
            print_error(f"Erro ao criar {data_root}: {e}")
            return False

    # Criar subdiretórios
    subdirs = [
        "postgres", "minio", "hive", "trino", "superset", "redis",
        "airflow/dags", "airflow/logs", "airflow/plugins",
        "spark/master", "spark/worker"
    ]

    for subdir in subdirs:
        (data_root / subdir).mkdir(parents=True, exist_ok=True)

    # Configurar permissões
    run_command(f"chmod -R 755 {data_root}", "Configurando permissões gerais", check=False)
    run_command(f"sudo chown -R 50000:0 {data_root}/airflow", "Configurando permissões do Airflow", check=False)

    print_success("Estrutura de diretórios criada")
    return True


def clean_docker_environment():
    """Limpa ambiente Docker"""
    print_header("ETAPA 2/7: Limpando ambiente Docker")

    # Verificar se Docker está rodando
    if not run_command("docker info", "Verificando Docker", check=False):
        print_error("Docker não está rodando")
        return False

    # Parar containers (usar docker compose sem hífen)
    run_command("docker compose down -v", "Parando containers", check=False)

    # Limpar volumes e redes
    run_command("docker volume prune -f", "Removendo volumes órfãos", check=False)
    run_command("docker network prune -f", "Removendo redes não utilizadas", check=False)

    print_success("Ambiente Docker limpo")
    return True


def build_custom_images():
    """Constrói imagens personalizadas"""
    print_header("ETAPA 3/7: Construindo imagens personalizadas")

    if not run_command("docker compose build hive-metastore", "Construindo Hive Metastore", timeout=300):
        print_warning("Falha ao construir Hive Metastore")

    if not run_command("docker compose build trino", "Construindo Trino", timeout=300):
        print_warning("Falha ao construir Trino")

    print_success("Imagens construídas")
    return True


def start_base_services():
    """Inicia serviços base"""
    print_header("ETAPA 4/7: Iniciando serviços base")

    # Subir PostgreSQL, MinIO e Redis
    run_command("docker compose up -d postgres minio redis", "Subindo serviços base")

    # Aguardar PostgreSQL
    print_info("Aguardando PostgreSQL ficar pronto...")
    for i in range(30):
        if run_command("docker exec postgres pg_isready -U admin", "Verificando PostgreSQL", check=False):
            print_success("PostgreSQL está pronto")
            break
        time.sleep(2)
    else:
        print_error("PostgreSQL não ficou pronto a tempo")
        run_command("docker compose logs postgres", "Logs do PostgreSQL", check=False)
        return False

    # Aguardar MinIO
    print_info("Aguardando MinIO ficar pronto...")
    for i in range(30):
        if run_command("docker exec minio curl -sf http://localhost:9000/minio/health/live", "Verificando MinIO", check=False):
            print_success("MinIO está pronto")
            break
        time.sleep(2)
    else:
        print_error("MinIO não ficou pronto a tempo")
        return False

    # Aguardar Redis
    print_info("Aguardando Redis ficar pronto...")
    for i in range(15):
        if run_command("docker exec redis redis-cli ping", "Verificando Redis", check=False):
            print_success("Redis está pronto")
            break
        time.sleep(2)
    else:
        print_error("Redis não ficou pronto a tempo")
        return False

    # Criar buckets no MinIO
    run_command("docker compose up -d minio-client", "Criando buckets no MinIO")
    time.sleep(5)
    print_success("Buckets criados")

    return True


def start_hive_metastore():
    """Inicia Hive Metastore"""
    print_header("ETAPA 5/7: Iniciando Hive Metastore")

    run_command("docker compose up -d hive-metastore", "Subindo Hive Metastore")

    print_info("Aguardando Hive Metastore ficar pronto (até 90s)...")
    for i in range(45):
        if run_command('docker exec hive-metastore timeout 2 bash -c "</dev/tcp/localhost/9083"',
                       "Verificando Hive Metastore", check=False):
            print_success("Hive Metastore está pronto")
            return True
        time.sleep(2)

    print_error("Hive Metastore não ficou pronto a tempo")
    run_command("docker compose logs --tail=50 hive-metastore", "Logs do Hive Metastore", check=False)
    return False


def start_remaining_services():
    """Inicia serviços restantes"""
    print_header("ETAPA 6/7: Iniciando serviços restantes")

    # Spark
    run_command("docker compose up -d spark-master spark-worker", "Subindo Spark")

    # Trino
    run_command("docker compose up -d trino", "Subindo Trino")

    # Airflow
    run_command("docker compose up -d airflow-init", "Inicializando banco do Airflow")
    print_info("Aguardando inicialização do Airflow...")
    time.sleep(30)

    run_command("docker compose up -d airflow-webserver airflow-scheduler", "Subindo Airflow")

    # Superset
    run_command("docker compose up -d superset", "Subindo Superset")

    print_success("Todos os serviços iniciados")
    return True


def validate_services():
    """Valida serviços"""
    print_header("ETAPA 7/7: Validando serviços")

    print_info("Aguardando serviços estabilizarem (60s)...")
    time.sleep(60)

    # Verificar status
    run_command("docker compose ps", "Status dos containers", check=False)

    services_ok = True

    # Validar cada serviço
    validations = [
        ("docker exec postgres pg_isready -U admin", "PostgreSQL"),
        ("docker exec minio curl -sf http://localhost:9000/minio/health/live", "MinIO"),
        ("docker exec redis redis-cli ping", "Redis"),
        ('docker exec hive-metastore timeout 2 bash -c "</dev/tcp/localhost/9083"', "Hive Metastore"),
        ("docker exec trino curl -sf http://localhost:8080/v1/info", "Trino"),
        ("docker exec spark-master curl -sf http://localhost:8080", "Spark Master"),
        ("docker exec airflow-webserver curl -sf http://localhost:8080/health", "Airflow"),
        ("docker exec superset curl -sf http://localhost:8088/health", "Superset"),
    ]

    for cmd, service in validations:
        if run_command(cmd, f"Validando {service}", check=False):
            print_success(f"{service}: OK")
        else:
            print_warning(f"{service}: Verificar manualmente")
            if service in ["PostgreSQL", "MinIO", "Redis", "Hive Metastore"]:
                services_ok = False

    return services_ok


def configure_stack():
    """Configura stack usando script Python"""
    print_header("Configuração automática")

    print_info("Aguardando mais 30s para garantir estabilidade...")
    time.sleep(30)

    script_path = Path(__file__).parent / "setup_stack.py"
    if script_path.exists():
        print_info("Executando configuração do MinIO, Trino e Superset...")
        try:
            result = subprocess.run(
                [sys.executable, str(script_path), "--auto"],
                check=False
            )
            if result.returncode == 0:
                print_success("Configuração concluída")
            else:
                print_warning("Configuração completada com avisos")
        except Exception as e:
            print_warning(f"Erro na configuração automática: {e}")
    else:
        print_warning(f"Script de configuração não encontrado: {script_path}")


def print_summary(services_ok):
    """Imprime resumo final"""
    print_header("🎉 SETUP COMPLETO!")

    print(f"\n{Colors.GREEN}✅ Stack Big Data iniciada com sucesso!{Colors.NC}\n")

    print(f"{Colors.YELLOW}📊 URLs de Acesso:{Colors.NC}")
    print(f"  {Colors.CYAN}MinIO Console:{Colors.NC}  http://localhost:9001 {Colors.GREEN}(minioadmin / minioadmin123){Colors.NC}")
    print(f"  {Colors.CYAN}Airflow:{Colors.NC}        http://localhost:8080 {Colors.GREEN}(airflow / airflow){Colors.NC}")
    print(f"  {Colors.CYAN}Superset:{Colors.NC}       http://localhost:8088 {Colors.GREEN}(admin / admin){Colors.NC}")
    print(f"  {Colors.CYAN}Trino:{Colors.NC}          http://localhost:8085 {Colors.GREEN}(trino / sem senha){Colors.NC}")
    print(f"  {Colors.CYAN}Spark Master:{Colors.NC}   http://localhost:8080")
    print(f"  {Colors.CYAN}Spark Worker:{Colors.NC}   http://localhost:8081")

    print(f"\n{Colors.YELLOW}📁 Dados persistidos em:{Colors.NC}")
    print(f"  {Colors.GREEN}/media/marcelo/dados1/bigdata-docker{Colors.NC}")

    print(f"\n{Colors.YELLOW}🔍 Comandos úteis:{Colors.NC}")
    print(f"  {Colors.CYAN}Ver logs:{Colors.NC}         docker-compose logs -f [serviço]")
    print(f"  {Colors.CYAN}Status:{Colors.NC}           docker-compose ps")
    print(f"  {Colors.CYAN}Reiniciar:{Colors.NC}        docker-compose restart [serviço]")
    print(f"  {Colors.CYAN}Parar tudo:{Colors.NC}       docker-compose down")
    print(f"  {Colors.CYAN}Validar:{Colors.NC}          python3 scripts/validate_all_services.py")

    print(f"\n{Colors.YELLOW}📚 Documentação:{Colors.NC}")
    print(f"  {Colors.GREEN}docs/INDICE.md{Colors.NC}\n")

    if services_ok:
        print_success("Todos os serviços críticos estão funcionando!")
    else:
        print_warning("Alguns serviços podem precisar de atenção. Verifique os logs.")
        print(f"\n{Colors.YELLOW}Para ver logs de um serviço específico:{Colors.NC}")
        print(f"  {Colors.CYAN}docker-compose logs -f <nome-do-serviço>{Colors.NC}")

    print()


def main():
    """Função principal"""
    # Mudar para o diretório do projeto
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print_header("🚀 SETUP COMPLETO DA STACK BIG DATA")
    print_info(f"Diretório do projeto: {project_root}")

    # Executar etapas
    steps = [
        ("Criação de diretórios", create_directory_structure),
        ("Limpeza do Docker", clean_docker_environment),
        ("Build de imagens", build_custom_images),
        ("Serviços base", start_base_services),
        ("Hive Metastore", start_hive_metastore),
        ("Serviços restantes", start_remaining_services),
    ]

    for step_name, step_func in steps:
        if not step_func():
            print_error(f"Falha na etapa: {step_name}")
            sys.exit(1)

    # Validação
    services_ok = validate_services()

    # Configuração automática
    if services_ok:
        configure_stack()

    # Resumo
    print_summary(services_ok)

    sys.exit(0 if services_ok else 1)


if __name__ == "__main__":
    main()
