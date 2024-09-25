# servier-data-jobs

## How to generate the desired graph ?
1. Create and activate your virtual env

```bash
    python -m venv your_venv_name
    source your_venv_name/bin/activate
```

2. Install poetry using pip

```bash
    pip install poetry
```

3. Install dependencies

```bash
    poetry install
```
4. Run Tests

```bash
    poetry run python3 -m unittest discover tests
```

5. Run the script

if your data is in a folder named 'data' within the same directory you can run:

```bash
poetry run python main.py --data_path ./data --destination ./data

```

## Bonus part

1. Extract the journal that mentions the most different drugs:

We just need to add the flag --bonus

```bash
poetry run python main.py --data_path ./data --destination ./data --bonus

```
2. For a specific drug, find all the drugs mentionned by the same journals, referenced by PubMed but not clinical trials:

We should add the argument --target_drug 'drug'

```bash
poetry run python main.py --data_path ./data --destination ./data --bonus --target_drug 'tetracycline'

```

## Questions
1. Quels sont les éléments à considérer pour faire évoluer votre code afin qu’il puisse gérer de grosses
volumétries de données (fichiers de plusieurs To ou millions de fichiers par exemple) ?

On peut essayer de pallèliser et distribuer le traitement et pour le faire on peut essayer de combiner Airflow avec Dask.  

2. Pourriez-vous décrire les modifications qu’il faudrait apporter, s’il y en a, pour prendre en considération de
telles volumétries ?

- Lire les données par chunk
- Remplacer pandas dataframes par dask dataframes
- Créer un DAG en utilisant Airflow en utilisant soit des PythonOperator soit un KubernetesPodOperator si on a une image Docker deployé sur Artifact registry (si on est sur GCP/Composer)
- Modifier la logique de traitement en favorisant le modèle MapReduce
- Utiliser DaskExecutor au lieu de Celery

## SQL 

1. Montant total des ventes entre le 01/01/2019 et le 31/12/2019:

```sql
SELECT 
    date AS transaction_date,
    SUM(prod_price * prod_qty) AS daily_revenue
FROM 
    TRANSACTIONS
WHERE 
    date BETWEEN '2019-01-01' AND '2019-12-31'
GROUP BY 
    date
ORDER BY 
    transaction_date ASC;

```

2. Montant total des ventes 'Meuble' et 'Deco' par client, entre le 01/01/2019 et le 31/12/2019:

```sql
SELECT 
    t.client_id,
    SUM(CASE WHEN p.product_type = 'MEUBLE' THEN t.prod_price * t.prod_qty ELSE 0 END) AS ventes_meuble,
    SUM(CASE WHEN p.product_type = 'DECO' THEN t.prod_price * t.prod_qty ELSE 0 END) AS ventes_deco
FROM 
    TRANSACTIONS t
JOIN 
    PRODUCT_NOMENCLATURE p
ON 
    t.prod_id = p.product_id
WHERE 
    t.date BETWEEN '2019-01-01' AND '2019-12-31'
GROUP BY 
    t.client_id
ORDER BY 
    t.client_id;

```