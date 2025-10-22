-- Queries de exemplo para executar no Trino
-- Acesse via: http://localhost:8085
-- Ou conecte via JDBC: jdbc:trino://localhost:8085/hive/default
-- ============================================
-- 1. EXPLORAÇÃO DE DADOS
-- ============================================
-- Listar todos os catálogos disponíveis
SHOW CATALOGS;

-- Listar schemas no catálogo hive
SHOW SCHEMAS
FROM
	hive;

-- Listar tabelas no schema sales
SHOW TABLES
FROM
	hive.sales;

-- ============================================
-- 2. CONSULTAS BÁSICAS
-- ============================================
-- Ver primeiros registros da tabela silver
SELECT
	*
FROM
	hive.sales.sales_silver
LIMIT
	10;

-- Contar total de transações
SELECT
	COUNT(*) as total_transactions
FROM
	hive.sales.sales_silver;

-- ============================================
-- 3. ANÁLISES POR CATEGORIA
-- ============================================
-- Top categorias por receita
SELECT
	product_category,
	SUM(total_revenue) as total_revenue,
	SUM(total_quantity) as items_sold,
	SUM(total_transactions) as num_transactions
FROM
	hive.sales.sales_by_category
GROUP BY
	product_category
ORDER BY
	total_revenue DESC;

-- Receita mensal por categoria
SELECT
	year,
	month,
	product_category,
	SUM(total_revenue) as monthly_revenue
FROM
	hive.sales.sales_by_category
GROUP BY
	year,
	month,
	product_category
ORDER BY
	year DESC,
	month DESC,
	monthly_revenue DESC;

-- ============================================
-- 4. ANÁLISES POR REGIÃO
-- ============================================
-- Performance por região
SELECT
	region,
	SUM(total_revenue) as revenue,
	SUM(total_transactions) as transactions,
	SUM(unique_customers) as customers,
	ROUND(SUM(total_revenue) / SUM(total_transactions), 2) as avg_ticket
FROM
	hive.sales.sales_by_region
GROUP BY
	region
ORDER BY
	revenue DESC;

-- Crescimento mensal por região
SELECT
	region,
	year,
	month,
	total_revenue,
	LAG(total_revenue) OVER (
		PARTITION BY region
		ORDER BY
			year,
			month
	) as prev_month_revenue,
	ROUND(
		(
			total_revenue - LAG(total_revenue) OVER (
				PARTITION BY region
				ORDER BY
					year,
					month
			)
		) / LAG(total_revenue) OVER (
			PARTITION BY region
			ORDER BY
				year,
				month
		) * 100,
		2
	) as growth_pct
FROM
	hive.sales.sales_by_region
ORDER BY
	region,
	year DESC,
	month DESC;

-- ============================================
-- 5. MÉTRICAS DIÁRIAS
-- ============================================
-- Últimos 7 dias de métricas
SELECT
	transaction_date,
	daily_revenue,
	daily_transactions,
	daily_customers,
	avg_ticket
FROM
	hive.sales.daily_metrics
ORDER BY
	transaction_date DESC
LIMIT
	7;

-- Média móvel de 7 dias
SELECT
	transaction_date,
	daily_revenue,
	AVG(daily_revenue) OVER (
		ORDER BY
			transaction_date ROWS BETWEEN 6 PRECEDING
			AND CURRENT ROW
	) as moving_avg_7d
FROM
	hive.sales.daily_metrics
ORDER BY
	transaction_date DESC
LIMIT
	30;

-- ============================================
-- 6. ANÁLISES AVANÇADAS
-- ============================================
-- Produtos mais vendidos por região
WITH ranked_products AS (
	SELECT
		s.region,
		s.product_name,
		s.product_category,
		SUM(s.total_amount) as revenue,
		ROW_NUMBER() OVER (
			PARTITION BY s.region
			ORDER BY
				SUM(s.total_amount) DESC
		) as rank
	FROM
		hive.sales.sales_silver s
	GROUP BY
		s.region,
		s.product_name,
		s.product_category
)
SELECT
	*
FROM
	ranked_products
WHERE
	rank <= 5
ORDER BY
	region,
	rank;

-- Análise de cesta média por categoria
SELECT
	product_category,
	COUNT(DISTINCT transaction_id) as num_transactions,
	SUM(quantity) as total_items,
	ROUND(
		CAST(SUM(quantity) AS DOUBLE) / COUNT(DISTINCT transaction_id),
		2
	) as items_per_transaction,
	ROUND(
		SUM(total_amount) / COUNT(DISTINCT transaction_id),
		2
	) as avg_transaction_value
FROM
	hive.sales.sales_silver
GROUP BY
	product_category
ORDER BY
	avg_transaction_value DESC;

-- Distribuição de vendas por hora (se tiver timestamp)
SELECT
	product_category,
	COUNT(*) as transactions,
	ROUND(SUM(total_amount), 2) as revenue
FROM
	hive.sales.sales_silver
GROUP BY
	product_category
ORDER BY
	revenue DESC;

-- ============================================
-- 7. COHORT ANALYSIS
-- ============================================
-- Clientes por mês de primeira compra
WITH first_purchase AS (
	SELECT
		customer_id,
		MIN(transaction_date) as first_purchase_date,
		YEAR(MIN(transaction_date)) as cohort_year,
		MONTH(MIN(transaction_date)) as cohort_month
	FROM
		hive.sales.sales_silver
	GROUP BY
		customer_id
)
SELECT
	cohort_year,
	cohort_month,
	COUNT(DISTINCT customer_id) as new_customers
FROM
	first_purchase
GROUP BY
	cohort_year,
	cohort_month
ORDER BY
	cohort_year DESC,
	cohort_month DESC;

-- ============================================
-- 8. QUERIES PARA DASHBOARD
-- ============================================
-- KPIs principais
SELECT
	SUM(daily_revenue) as total_revenue,
	SUM(daily_transactions) as total_transactions,
	SUM(daily_customers) as total_customers,
	ROUND(SUM(daily_revenue) / SUM(daily_transactions), 2) as overall_avg_ticket
FROM
	hive.sales.daily_metrics;

-- Tendência semanal
SELECT
	YEAR(transaction_date) as year,
	WEEK(transaction_date) as week,
	SUM(daily_revenue) as weekly_revenue,
	SUM(daily_transactions) as weekly_transactions
FROM
	hive.sales.daily_metrics
GROUP BY
	YEAR(transaction_date),
	WEEK(transaction_date)
ORDER BY
	year DESC,
	week DESC
LIMIT
	12;

-- ============================================
-- 9. QUERIES DE DADOS BRUTOS (direto do S3)
-- ============================================
-- Consultar dados direto do MinIO/S3 (sem Hive Metastore)
-- Útil para exploração ad-hoc
/*
 SELECT *
 FROM hive.default."s3a://bronze/raw/sales/"
 WHERE "$path" LIKE '%20251021%'
 LIMIT 10;
 */
-- ============================================
-- 10. PERFORMANCE E OTIMIZAÇÃO
-- ============================================
-- Ver estatísticas da tabela
SHOW STATS FOR hive.sales.sales_silver;

-- Analisar plano de execução
EXPLAIN
SELECT
	product_category,
	SUM(total_amount)
FROM
	hive.sales.sales_silver
GROUP BY
	product_category;

-- ============================================
-- EXEMPLO DE USO VIA REST API
-- ============================================
/*
 curl -X POST http://localhost:8085/v1/statement \
 -H "X-Trino-User: trino" \
 -H "X-Trino-Catalog: hive" \
 -H "X-Trino-Schema: sales" \
 -d "SELECT COUNT(*) FROM sales_silver"
 */