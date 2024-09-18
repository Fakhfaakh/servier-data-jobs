# servier-data-jobs

## How to generate the desired graph ?
1. Create and activate your virtual env

```
    python -m venv your_venv_name
    source your_venv_name/bin/activate
```

2. Install Requirements from requirements.txt

```
    pip install -r requirements.txt
```

3. Run the script

if your data is in a folder named 'data' within the same directory you can run:

```
Python graph_generator.py --data_path ./data --destination ./data

```