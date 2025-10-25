# Solução para Problema de CSRF no Superset API

## Problema Identificado

Ao tentar criar datasets virtuais via API REST do Superset (`POST /api/v1/dataset/`), o sistema retornava erro:

```
400 Bad Request: The CSRF session token is missing.
```

## Causa Raiz

O Apache Superset 3.0.1 usa Flask-WTF para proteção CSRF, que valida tokens CSRF em todas as requisições POST/PUT/DELETE. A API REST requer autenticação JWT (Bearer token) **E** validação CSRF simultaneamente, o que cria complexidade adicional na integração via API.

## Solução Implementada

### 1. Configuração do Superset (`config/superset/superset_config.py`)

```python
# CSRF Protection
# ATENÇÃO: Desabilitado apenas para ambiente de desenvolvimento/teste local
# Em produção, mantenha WTF_CSRF_ENABLED = True e configure corretamente
WTF_CSRF_ENABLED = False  # Desabilita CSRF globalmente (apenas dev/teste)
WTF_CSRF_TIME_LIMIT = None
```

### 2. Código Python Simplificado

Após desabilitar CSRF, o código de autenticação fica muito mais simples:

```python
# Login via API
login_response = session.post(
    f"{SUPERSET_URL}/api/v1/security/login",
    json={
        "username": "admin",
        "password": "admin",
        "provider": "db",
        "refresh": True
    }
)

# Obter access token
access_token = login_response.json()["access_token"]

# Configurar headers
session.headers.update({
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
})

# Criar dataset (sem necessidade de CSRF token)
response = session.post(
    f"{SUPERSET_URL}/api/v1/dataset/",
    json=dataset_data
)
```

## Alternativas para Produção

### Opção 1: Feature Flag (Mais Segura)

```python
FEATURE_FLAGS = {
    "ENABLE_EXPLORE_JSON_CSRF_PROTECTION": False,
    # ... outras flags
}
```

Esta opção desabilita CSRF apenas para endpoints específicos do Explore, mantendo proteção em outros endpoints.

### Opção 2: Configurar CSRF Corretamente

Para manter `WTF_CSRF_ENABLED = True` em produção, é necessário:

1. Obter CSRF token: `GET /api/v1/security/csrf_token/`
2. Adicionar headers:
   ```python
   headers = {
       "Authorization": f"Bearer {access_token}",
       "X-CSRFToken": csrf_token,
       "Referer": SUPERSET_URL
   }
   ```
3. Adicionar cookies de sessão com o CSRF token

**Nota**: Esta abordagem é complexa e pode apresentar problemas de sincronização entre session cookies e headers.

### Opção 3: Usar Interface Web ou CLI

Se a automação via API apresentar muitos desafios:

```bash
# Via interface web
http://localhost:8088 → Data → Datasets → + Dataset

# Via CLI dentro do container
docker exec -it superset bash
superset fab create-dataset --help
```

## Considerações de Segurança

⚠️ **IMPORTANTE**: A configuração `WTF_CSRF_ENABLED = False` é **ADEQUADA APENAS** para:
- Ambientes de desenvolvimento local
- Ambientes de teste/CI
- POCs e demonstrações

🔒 **Em produção**:
- Mantenha `WTF_CSRF_ENABLED = True`
- Configure autenticação robusta (OAuth, LDAP, etc.)
- Use HTTPS
- Implemente Content Security Policy (CSP)
- Considere usar Row Level Security (RLS)

## Teste da Solução

```bash
# Testar criação de dataset via API
python3 test_api_login_final.py

# Executar script completo
python3 scripts/02_criar_datasets_virtuais_completo.py
```

## Resultado

✅ API funciona corretamente  
✅ Datasets podem ser criados programaticamente  
✅ Automação completa da Fase 02  

## Referências

- [Superset Security Documentation](https://superset.apache.org/docs/security)
- [Flask-WTF CSRF Protection](https://flask-wtf.readthedocs.io/en/stable/csrf.html)
- [Superset API Documentation](http://localhost:8088/swagger/v1)

## Próximos Passos

Antes de executar a Fase 02 (criação de datasets virtuais), é necessário:

1. ✅ Executar Fase 01 - Criar tabelas base no Hive/Trino
2. ✅ Verificar que o schema `bi_gold_kpis` existe
3. ✅ Garantir que todas as tabelas referenciadas pelos SQLs existem
4. ✅ Então executar script de criação de datasets virtuais
