#!/usr/bin/env python3
"""
Script de Validação Completa da Stack Mini BigData
Valida todos os serviços: PostgreSQL, MinIO, Hive Metastore, Spark, Trino, Airflow, Superset, Redis
"""

import requests
import time
import sys
import socket
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ServiceStatus:
    """Status de um serviço"""
    name: str
    status: str  # 'OK', 'FAIL', 'WARN'
    message: str
    details: Optional[Dict] = field(default_factory=dict)


class StackValidator:
    """Validador completo da stack BigData"""

    def __init__(self):
        self.results: List[ServiceStatus] = []
        self.start_time = datetime.now()

    def print_header(self, title: str):
        """Imprime cabeçalho formatado"""
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")

    def print_result(self, service: str, success: bool, message: str = "", details: Dict = None):
        """Imprime e armazena resultado"""
        status = "✓ OK" if success else "✗ FAIL"
        color = "\033[92m" if success else "\033[91m"
        reset = "\033[0m"

        print(f"{color}{status}{reset} - {service}")
        if message:
            print(f"  → {message}")
        if details:
            for key, value in details.items():
                print(f"    • {key}: {value}")

        self.results.append(ServiceStatus(
            name=service,
            status="OK" if success else "FAIL",
            message=message,
            details=details or {}
        ))

    def validate_postgresql(self) -> bool:
        """Valida PostgreSQL"""
        self.print_header("1. POSTGRESQL")

        try:
            import psycopg2

            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="admin",
                password="admin123",
                database="postgres",
                connect_timeout=5
            )

            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            result = cursor.fetchone()
            version = result[0] if result else "Unknown"

            cursor.execute("""
                SELECT datname FROM pg_database 
                WHERE datname IN ('airflow', 'superset', 'metastore')
            """)
            databases = [row[0] for row in cursor.fetchall()]

            conn.close()

            self.print_result("PostgreSQL", True, "Conectado com sucesso", {
                "Versão": version.split(',')[0],
                "Databases": ', '.join(databases)
            })
            return True

        except Exception as e:
            self.print_result("PostgreSQL", False, str(e))
            return False

    def validate_redis(self) -> bool:
        """Valida Redis"""
        self.print_header("2. REDIS")

        try:
            response = requests.get("http://localhost:6379", timeout=5)
            # Redis responde com erro mas está online
            self.print_result("Redis", True, "Serviço respondendo")
            return True
        except requests.exceptions.ConnectionError:
            # Tentar com protocolo Redis nativo seria melhor, mas validamos pela porta
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            try:
                result = sock.connect_ex(('localhost', 6379))
                sock.close()
                if result == 0:
                    self.print_result("Redis", True, "Porta 6379 acessível")
                    return True
                else:
                    self.print_result("Redis", False, "Porta 6379 não acessível")
                    return False
            except Exception as e:
                self.print_result("Redis", False, str(e))
                return False
        except Exception as e:
            self.print_result("Redis", False, str(e))
            return False

    def validate_minio(self) -> bool:
        """Valida MinIO"""
        self.print_header("3. MINIO (Object Storage)")

        try:
            # Console
            response = requests.get("http://localhost:9001/login", timeout=5)
            console_ok = response.status_code == 200

            # API
            response = requests.get("http://localhost:9000/minio/health/live", timeout=5)
            api_ok = response.status_code == 200

            if console_ok and api_ok:
                self.print_result("MinIO", True, "Console e API operacionais", {
                    "Console": "http://localhost:9001",
                    "API": "http://localhost:9000"
                })
                return True
            else:
                self.print_result("MinIO", False, f"Console: {console_ok}, API: {api_ok}")
                return False

        except Exception as e:
            self.print_result("MinIO", False, str(e))
            return False

    def validate_hive_metastore(self) -> bool:
        """Valida Hive Metastore"""
        self.print_header("4. HIVE METASTORE")

        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', 9083))
            sock.close()

            if result == 0:
                self.print_result("Hive Metastore", True, "Porta 9083 acessível", {
                    "Serviço": "Thrift Server",
                    "Porta": "9083"
                })
                return True
            else:
                self.print_result("Hive Metastore", False, "Porta 9083 não acessível")
                return False

        except Exception as e:
            self.print_result("Hive Metastore", False, str(e))
            return False

    def validate_spark(self) -> bool:
        """Valida Spark Master e Worker"""
        self.print_header("5. APACHE SPARK")

        try:
            # Spark Master UI
            response = requests.get("http://localhost:8081", timeout=5)
            master_ok = response.status_code == 200

            # Spark Worker UI
            response = requests.get("http://localhost:8082", timeout=5)
            worker_ok = response.status_code == 200

            if master_ok and worker_ok:
                self.print_result("Spark", True, "Master e Worker operacionais", {
                    "Master UI": "http://localhost:8081",
                    "Worker UI": "http://localhost:8082",
                    "Master Port": "7077"
                })
                return True
            else:
                self.print_result("Spark", False, f"Master: {master_ok}, Worker: {worker_ok}")
                return False

        except Exception as e:
            self.print_result("Spark", False, str(e))
            return False

    def validate_trino(self) -> bool:
        """Valida Trino"""
        self.print_header("6. TRINO")

        try:
            response = requests.get("http://localhost:8085/v1/info", timeout=10)

            if response.status_code == 200:
                info = response.json()
                self.print_result("Trino", True, "Query engine operacional", {
                    "Versão": info.get('nodeVersion', {}).get('version', 'N/A'),
                    "Environment": info.get('environment', 'N/A'),
                    "UI": "http://localhost:8085"
                })
                return True
            else:
                self.print_result("Trino", False, f"Status: {response.status_code}")
                return False

        except Exception as e:
            self.print_result("Trino", False, str(e))
            return False

    def validate_airflow(self) -> bool:
        """Valida Airflow"""
        self.print_header("7. APACHE AIRFLOW")

        try:
            # Webserver
            response = requests.get("http://localhost:8080/health", timeout=10)

            if response.status_code == 200:
                health = response.json()
                metadatabase_ok = health.get('metadatabase', {}).get('status') == 'healthy'
                scheduler_ok = health.get('scheduler', {}).get('status') == 'healthy'

                self.print_result("Airflow", metadatabase_ok and scheduler_ok,
                                  "Webserver e Scheduler operacionais", {
                                    "Webserver": "http://localhost:8080",
                                    "Metadatabase": "healthy" if metadatabase_ok else "unhealthy",
                                    "Scheduler": "healthy" if scheduler_ok else "unhealthy"
                                  })
                return metadatabase_ok and scheduler_ok
            else:
                self.print_result("Airflow", False, f"Status: {response.status_code}")
                return False

        except Exception as e:
            self.print_result("Airflow", False, str(e))
            return False

    def validate_superset(self) -> bool:
        """Valida Apache Superset"""
        self.print_header("8. APACHE SUPERSET")

        try:
            # Health check
            response = requests.get("http://localhost:8088/health", timeout=10)

            if response.status_code == 200:
                # Tentar login
                login_response = requests.post(
                    "http://localhost:8088/api/v1/security/login",
                    json={
                        "username": "admin",
                        "password": "admin",
                        "provider": "db",
                        "refresh": True
                    },
                    timeout=10
                )

                login_ok = login_response.status_code == 200

                details = {
                    "UI": "http://localhost:8088",
                    "API": "Operacional" if login_ok else "Erro no login",
                    "Health": "OK"
                }

                if login_ok:
                    # Verificar databases
                    token = login_response.json().get('access_token')
                    db_response = requests.get(
                        "http://localhost:8088/api/v1/database/",
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=10
                    )

                    if db_response.status_code == 200:
                        db_count = len(db_response.json().get('result', []))
                        details["Databases"] = str(db_count)

                self.print_result("Superset", login_ok, "BI Platform operacional", details)
                return login_ok
            else:
                self.print_result("Superset", False, f"Status: {response.status_code}")
                return False

        except Exception as e:
            self.print_result("Superset", False, str(e))
            return False

    def print_summary(self):
        """Imprime resumo final"""
        self.print_header("RESUMO DA VALIDAÇÃO")

        ok_count = sum(1 for r in self.results if r.status == "OK")
        total = len(self.results)

        elapsed = (datetime.now() - self.start_time).total_seconds()

        print(f"Serviços Validados: {total}")
        print(f"Serviços OK: {ok_count}")
        print(f"Serviços com Problemas: {total - ok_count}")
        print(f"Taxa de Sucesso: {(ok_count/total)*100:.1f}%")
        print(f"Tempo de Execução: {elapsed:.2f}s\n")

        # Lista de status
        print("Status por Serviço:")
        for result in self.results:
            color = "\033[92m" if result.status == "OK" else "\033[91m"
            reset = "\033[0m"
            status_icon = "✓" if result.status == "OK" else "✗"
            print(f"  {color}{status_icon}{reset} {result.name}")

        print("\n" + "=" * 80 + "\n")

        # URLs de acesso
        if ok_count > 0:
            print("🌐 URLS DE ACESSO:")
            print("-" * 80)

            urls = [
                ("MinIO Console", "http://localhost:9001", "minioadmin / minioadmin123"),
                ("Spark Master", "http://localhost:8081", ""),
                ("Spark Worker", "http://localhost:8082", ""),
                ("Trino", "http://localhost:8085", ""),
                ("Airflow", "http://localhost:8080", "airflow / airflow"),
                ("Superset", "http://localhost:8088", "admin / admin"),
            ]

            for name, url, creds in urls:
                print(f"\n{name}:")
                print(f"  URL: {url}")
                if creds:
                    print(f"  Credenciais: {creds}")

            print("\n" + "=" * 80 + "\n")

        # Código de saída
        return 0 if ok_count == total else 1

    def run_all_validations(self) -> int:
        """Executa todas as validações"""
        print("\n" + "=" * 80)
        print("  VALIDAÇÃO COMPLETA DA STACK MINI-BIGDATA")
        print("  Data:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 80)

        # Executar validações
        self.validate_postgresql()
        self.validate_redis()
        self.validate_minio()
        self.validate_hive_metastore()
        self.validate_spark()
        self.validate_trino()
        self.validate_airflow()
        self.validate_superset()

        # Resumo
        return self.print_summary()


def main():
    """Função principal"""
    validator = StackValidator()
    exit_code = validator.run_all_validations()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
