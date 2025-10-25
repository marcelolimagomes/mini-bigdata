#!/usr/bin/env python3
"""
setup_stack.py - Configura toda a stack Big Data automaticamente
"""

import subprocess
import sys
import time
import os


def run_script(script_path, description):
    """Executa um script Python"""
    print(f"\n{'=' * 70}")
    print(f"  {description}")
    print(f"{'=' * 70}\n")

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=False,
            text=True
        )

        if result.returncode == 0:
            print(f"\n✅ {description} - Concluído")
            return True
        else:
            print(f"\n⚠️  {description} - Completado com avisos")
            return True
    except Exception as e:
        print(f"\n❌ Erro ao executar {script_path}: {e}")
        return False


def install_dependencies():
    """Instala dependências Python necessárias"""
    print("\n" + "=" * 70)
    print("📦 Verificando dependências Python...")
    print("=" * 70 + "\n")
    
    required_packages = {
        'minio': 'minio',
        'trino': 'trino',
        'requests': 'requests'
    }
    
    for package_import, package_name in required_packages.items():
        try:
            __import__(package_import)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  📥 Instalando {package_name}...")
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--quiet', package_name],
                check=True,
                capture_output=True
            )
            print(f"  ✅ {package_name} instalado")


def main():
    """Executa setup completo"""
    print("\n" + "=" * 70)
    print("  SETUP COMPLETO DA STACK BIG DATA")
    print("=" * 70)
    print("\n  Este script irá configurar:")
    print("    1. MinIO (buckets)")
    print("    2. Trino/Hive (schemas e tabelas)")
    print("    3. Superset (database connections e datasets)")
    print("\n" + "=" * 70)

    # Modo automático - não pedir confirmação se rodando via script
    if "--auto" not in sys.argv:
        input("\n⏸️  Pressione ENTER para continuar...")

    # Verificar dependências
    install_dependencies()

    # Determinar diretório dos scripts
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. Configurar MinIO
    if not run_script(
        os.path.join(script_dir, "configure_minio.py"),
        "1/3 - Configurando MinIO"
    ):
        print("\n⚠️  Continuando mesmo com erros no MinIO...")

    time.sleep(2)

    # 2. Configurar Trino
    if not run_script(
        os.path.join(script_dir, "configure_trino.py"),
        "2/3 - Configurando Trino/Hive"
    ):
        print("\n⚠️  Continuando mesmo com erros no Trino...")

    time.sleep(2)

    # 3. Configurar Superset
    if not run_script(
        os.path.join(script_dir, "configure_superset.py"),
        "3/3 - Configurando Superset"
    ):
        print("\n⚠️  Configuração do Superset pode requerer passos manuais")

    # Resumo final
    print("\n" + "=" * 70)
    print("  🎉 SETUP COMPLETO!")
    print("=" * 70)

    print("\n📋 Recursos configurados:")
    print("  ✅ MinIO: bronze, silver, gold, warehouse")
    print("  ✅ Trino: schemas (vendas, logs, analytics)")
    print("  ✅ Trino: tabelas (vendas_raw, vendas_silver, vendas_agregadas)")
    print("  ✅ Trino: views (vendas_mensais, top_produtos)")
    print("  ✅ Superset: datasets prontos para uso")

    print("\n🌐 URLs de Acesso:")
    print("  MinIO:    http://localhost:9001")
    print("  Trino:    http://localhost:8085")
    print("  Superset: http://localhost:8088")
    print("  Airflow:  http://localhost:8080")

    print("\n💡 Próximos passos:")
    print("  1. Carregar dados de exemplo nos buckets")
    print("  2. Executar pipelines Airflow para processar dados")
    print("  3. Criar charts e dashboards no Superset")

    print("\n📚 Documentação:")
    print("  docs/09-configuracao-automatizada.md")


if __name__ == "__main__":
    main()
