# 🚀 Quick Start - Mini Big Data Stack

## Setup em 1 Comando

```bash
python3 scripts/full_setup.py
```

**Tempo estimado:** 8 minutos  
**Resultado:** Stack completa funcionando

---

## 🌐 URLs de Acesso

Após o setup, acesse:

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **Superset** (BI) | http://localhost:8088 | `admin` / `admin` |
| **Airflow** (Orquestração) | http://localhost:8080 | `airflow` / `airflow` |
| **MinIO** (Storage) | http://localhost:9001 | `minioadmin` / `minioadmin123` |
| **Trino** (Query) | http://localhost:8085 | `trino` / (sem senha) |
| **Spark Master** | http://localhost:8081 | - |
| **Spark Worker** | http://localhost:8082 | - |

---

## ⚡ Comandos Rápidos

### Ver Status
```bash
docker compose ps
```

### Ver Logs
```bash
docker compose logs -f superset
docker compose logs -f airflow-webserver
docker compose logs -f trino
```

### Reiniciar Tudo
```bash
docker compose restart
```

### Parar Tudo
```bash
docker compose down
```

### Setup do Zero
```bash
docker compose down -v
python3 scripts/full_setup.py
```

### Validar Serviços
```bash
python3 scripts/validate_all_services.py
```

---

## 📊 Primeiro Dashboard

1. **Acesse Superset:** http://localhost:8088
2. **Faça login:** `admin` / `admin`
3. **Database → + Database**
   - Tipo: **Trino**
   - URI: `trino://trino@trino:8080/hive`
4. **SQL Lab → SQL Editor**
   - Escreva query
   - Execute
5. **Charts → + Chart**
   - Selecione dataset
   - Crie visualização

---

## 🔧 Troubleshooting

### Serviço não inicia?
```bash
docker compose logs [servico]
docker compose restart [servico]
```

### Porta ocupada?
```bash
sudo lsof -i :8088  # Verificar quem está usando
docker compose down  # Parar tudo
```

### Reset completo?
```bash
docker compose down -v
sudo rm -rf /media/marcelo/dados1/bigdata-docker/*
python3 scripts/full_setup.py
```

---

## 📚 Documentação Completa

- **Índice:** `docs/INDICE.md`
- **Resumo Setup:** `RESUMO-SETUP-AUTOMATIZADO.md`
- **Guias Detalhados:** `docs/`

---

**Desenvolvido por:** Marcelo Lima Gomes  
**Versão:** 2.0 (Setup Automatizado)
