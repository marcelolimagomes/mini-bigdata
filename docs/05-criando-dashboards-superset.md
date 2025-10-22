# 📊 Criando Dashboards com Apache Superset

## 🎯 Visão Geral

O Apache Superset é uma plataforma de BI moderna para criar visualizações e dashboards interativos.

- **URL:** http://localhost:8088
- **Usuário:** `admin`
- **Senha:** `admin`

## 🚀 Primeiros Passos

### 1. Conectar ao Trino

1. Faça login no Superset
2. Clique em **Settings** (⚙️) → **Database Connections**
3. Clique em **+ Database**
4. Selecione **Trino**
5. Preencha:
   ```
   Display Name: Trino Big Data
   SQLAlchemy URI: trino://trino@trino:8080/hive
   ```
6. Clique em **Test Connection**
7. Clique em **Connect**

### 2. Adicionar Dataset

1. Vá em **Data** → **Datasets**
2. Clique em **+ Dataset**
3. Selecione:
   - **Database:** Trino Big Data
   - **Schema:** vendas
   - **Table:** vendas_silver
4. Clique em **Create Dataset and Create Chart**

## 📈 Criando Visualizações

### Gráfico 1: Receita Mensal (Linha)

1. **Chart Type:** Time-series Line Chart
2. **Time Column:** `data`
3. **Metrics:** 
   - Clique em **Simple** → **Aggregate:** `SUM`
   - **Column:** `valor_total`
   - **Label:** Receita Total
4. **Time Grain:** Month
5. **Filters:**
   - `ano` ≥ 2025
6. Clique em **Run**
7. Clique em **Save** → Nome: "Receita Mensal 2025"

### Gráfico 2: Top 10 Produtos (Barra)

1. **Chart Type:** Bar Chart
2. **Dimensions:**
   - **Column:** `produto`
3. **Metrics:**
   - Aggregate: `SUM(valor_total)`
   - Label: Receita
4. **Row Limit:** 10
5. **Sort By:** Receita (Descending)
6. Personalize cores em **Customize** → **Color Scheme**
7. **Save:** "Top 10 Produtos"

### Gráfico 3: Distribuição por Produto (Pizza)

1. **Chart Type:** Pie Chart
2. **Dimensions:** `produto`
3. **Metric:** `SUM(valor_total)`
4. **Row Limit:** 5
5. **Customize:**
   - Show Labels: ✓
   - Show Legend: ✓
   - Donut: ✓ (opcional)
6. **Save:** "Distribuição Receita"

### Gráfico 4: KPIs (Big Number)

#### KPI: Receita Total
1. **Chart Type:** Big Number
2. **Metric:** `SUM(valor_total)`
3. **Subheader:** Total de Receita
4. **Customize:**
   - Number Format: `$,.2f`
5. **Save:** "KPI - Receita Total"

#### KPI: Quantidade Vendida
1. **Chart Type:** Big Number
2. **Metric:** `SUM(quantidade)`
3. **Subheader:** Total de Itens
4. **Customize:**
   - Number Format: `,d`
5. **Save:** "KPI - Itens Vendidos"

#### KPI: Ticket Médio
1. **Chart Type:** Big Number
2. **Metric:** `AVG(valor_total)`
3. **Subheader:** Ticket Médio
4. **Customize:**
   - Number Format: `$,.2f`
5. **Save:** "KPI - Ticket Médio"

### Gráfico 5: Heatmap Produto x Mês

1. **Chart Type:** Heatmap
2. **X Axis:** `mes`
3. **Y Axis:** `produto`
4. **Metric:** `SUM(valor_total)`
5. **Customize:**
   - Color Scheme: blue_white_yellow
   - Linear Color Scheme: ✓
6. **Save:** "Heatmap Vendas"

### Gráfico 6: Tabela Dinâmica

1. **Chart Type:** Table
2. **Columns:**
   - `produto`
   - `ano`
   - `mes`
3. **Metrics:**
   - `SUM(quantidade)` → Quantidade
   - `SUM(valor_total)` → Receita
   - `COUNT(*)` → Nº Vendas
4. **Filters:**
   - `ano` = 2025
5. **Customize:**
   - Page Length: 20
   - Search Box: ✓
6. **Save:** "Tabela Vendas Detalhada"

## 🎨 Criando Dashboard

### 1. Criar Novo Dashboard

1. Vá em **Dashboards** → **+ Dashboard**
2. Nome: "Análise de Vendas 2025"
3. Clique em **Save**

### 2. Organizar Layout

1. Clique em **Edit Dashboard**
2. Arraste os gráficos da barra lateral:
   ```
   ┌──────────────────────────────────────┐
   │  KPI Receita │ KPI Itens │ KPI Ticket│
   ├──────────────────────────────────────┤
   │                                      │
   │        Receita Mensal (Linha)        │
   │                                      │
   ├────────────────────┬─────────────────┤
   │                    │                 │
   │  Top 10 Produtos   │  Distribuição   │
   │    (Barra)         │    (Pizza)      │
   │                    │                 │
   ├────────────────────┴─────────────────┤
   │                                      │
   │      Heatmap Produto x Mês           │
   │                                      │
   ├──────────────────────────────────────┤
   │                                      │
   │      Tabela Vendas Detalhada         │
   │                                      │
   └──────────────────────────────────────┘
   ```

### 3. Adicionar Filtros

1. No modo de edição, clique em **Filters**
2. Adicione filtros:
   - **Período:** `data` (Time Range)
   - **Produto:** `produto` (Filter Select)
   - **Ano:** `ano` (Filter Select)
3. Configure para aplicar a todos os gráficos
4. **Save Changes**

### 4. Personalizar Dashboard

1. Clique em **⋮** → **Dashboard Properties**
2. Configure:
   - **Title:** Dashboard de Vendas
   - **Description:** Análise detalhada de vendas
   - **Color Scheme:** supersetColors
   - **Refresh Interval:** 60 seconds (opcional)
3. **Save**

## 🔄 Dashboard com SQL Customizado

### Criar Virtual Dataset

1. **SQL Lab** → **SQL Editor**
2. Selecione: **Database:** Trino Big Data
3. Execute query customizada:

```sql
SELECT 
    CAST(ano AS VARCHAR) || '-' || LPAD(CAST(mes AS VARCHAR), 2, '0') as periodo,
    produto,
    SUM(quantidade) as quantidade_total,
    SUM(valor_total) as receita_total,
    AVG(valor) as preco_medio,
    COUNT(*) as num_vendas,
    SUM(valor_total) / COUNT(*) as ticket_medio
FROM hive.vendas.vendas_silver
GROUP BY ano, mes, produto
ORDER BY periodo, receita_total DESC
```

4. Clique em **Save** → **Save Dataset**
5. Nome: "vendas_analytics"
6. Agora use este dataset em gráficos

### Exemplo: Crescimento Mensal

```sql
WITH vendas_mensais AS (
    SELECT 
        CAST(ano AS VARCHAR) || '-' || LPAD(CAST(mes AS VARCHAR), 2, '0') as periodo,
        SUM(valor_total) as receita
    FROM hive.vendas.vendas_silver
    GROUP BY ano, mes
    ORDER BY ano, mes
)
SELECT 
    periodo,
    receita,
    LAG(receita) OVER (ORDER BY periodo) as receita_anterior,
    ((receita - LAG(receita) OVER (ORDER BY periodo)) / 
     LAG(receita) OVER (ORDER BY periodo) * 100) as crescimento_percentual
FROM vendas_mensais
```

## 🎯 Templates de Gráficos Prontos

### Dashboard Executivo

**Componentes:**
1. **Header:** 4 KPIs principais (Receita, Vendas, Ticket, Produtos)
2. **Tendência:** Gráfico de linha com receita mensal
3. **Comparativo:** Gráfico de barras comparando períodos
4. **Distribuição:** Pizza ou Treemap de categorias
5. **Detalhamento:** Tabela com drill-down

### Dashboard Operacional

**Componentes:**
1. **Métricas tempo real:** Big Numbers com refresh automático
2. **Alertas:** Indicadores de metas (verde/amarelo/vermelho)
3. **Tendências:** Sparklines para métricas chave
4. **Top/Bottom:** Rankings de melhor e pior desempenho
5. **Detalhes:** Tabelas filtráveis

### Dashboard Analítico

**Componentes:**
1. **Correlações:** Scatter plot
2. **Distribuições:** Histogramas e box plots
3. **Séries temporais:** Múltiplas linhas
4. **Heatmaps:** Identificação de padrões
5. **Cohorts:** Análise de grupos

## 🎨 Customização Avançada

### CSS Personalizado

1. **Settings** → **CSS Templates**
2. Adicione estilos:

```css
/* Header personalizado */
.dashboard-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
}

/* KPIs destacados */
.big-number-total {
    font-size: 48px;
    font-weight: bold;
    color: #667eea;
}

/* Tabelas zebradas */
.dataTable tbody tr:nth-child(even) {
    background-color: #f8f9fa;
}
```

### Jinja Templates

Use no SQL para parametrização dinâmica:

```sql
SELECT *
FROM hive.vendas.vendas_silver
WHERE data >= '{{ from_dttm }}'
  AND data < '{{ to_dttm }}'
{% if filter_values('produto') %}
  AND produto IN ({{ "'" + "','".join(filter_values('produto')) + "'" }})
{% endif %}
```

## 📧 Alertas e Agendamento

### Configurar Alerta

1. Abra o gráfico
2. Clique em **⋮** → **Set up an alert**
3. Configure:
   - **Alert Name:** Receita abaixo da meta
   - **Condition:** `SUM(valor_total) < 10000`
   - **Recipients:** seu@email.com
   - **Schedule:** Daily at 8:00 AM
4. **Save**

### Agendar Envio de Dashboard

1. Abra o Dashboard
2. Clique em **⋮** → **Schedule email report**
3. Configure:
   - **Recipients:** equipe@empresa.com
   - **Schedule:** Weekly on Monday at 9:00 AM
   - **Format:** PDF ou PNG
4. **Save**

## 🔌 Incorporar em Aplicações

### Embed Dashboard (iframe)

```html
<iframe
  src="http://localhost:8088/superset/dashboard/1/?standalone=true"
  width="100%"
  height="800px"
  frameborder="0">
</iframe>
```

### API REST

```python
import requests

# Login
login_url = "http://localhost:8088/api/v1/security/login"
credentials = {"username": "admin", "password": "admin"}
response = requests.post(login_url, json=credentials)
access_token = response.json()["access_token"]

# Buscar dashboards
headers = {"Authorization": f"Bearer {access_token}"}
dashboards_url = "http://localhost:8088/api/v1/dashboard/"
dashboards = requests.get(dashboards_url, headers=headers)
print(dashboards.json())
```

## 💡 Boas Práticas

### 1. Performance
- Usar datasets agregados para dashboards
- Limitar queries com filtros
- Cachear resultados frequentes
- Usar materialização para cálculos complexos

### 2. Design
- Máximo de 6-8 visualizações por dashboard
- Cores consistentes
- KPIs no topo
- Hierarquia visual clara

### 3. Interatividade
- Adicionar filtros globais
- Configurar cross-filtering
- Drill-down em gráficos
- Tooltips informativos

### 4. Manutenção
- Documentar queries SQL
- Versionamento de dashboards
- Revisar periodicamente
- Arquivar dashboards obsoletos

## 🆘 Troubleshooting

### Gráfico não carrega
- Verificar query no SQL Lab
- Checar conexão com Trino
- Ver logs: `docker compose logs superset`

### Erro de permissão
- Verificar role do usuário
- Adicionar permissões em: **Settings** → **Roles**

### Dashboard lento
- Otimizar queries SQL
- Adicionar índices no Trino
- Habilitar cache
- Reduzir intervalo de dados

## 🎓 Próximos Passos

- **Catálogo Hive:** `06-catalogo-hive-metastore.md`
- **APIs de acesso:** `07-apis-rest-jdbc.md`
- **Casos de uso:** `08-casos-uso-praticos.md`
