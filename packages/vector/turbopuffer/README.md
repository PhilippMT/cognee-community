# Cognee Turbopuffer Adapter

## Installation

If published, the package can be simply installed via pip:

```bash
pip install cognee-community-vector-adapter-turbopuffer
```

In case it is not published yet, you can use poetry to locally build the adapter package:

```bash
pip install poetry
poetry install # run this command in the directory containing the pyproject.toml file
```

## Connection Setup

1. Create an account at [turbopuffer.com](https://turbopuffer.com)
2. Get your API key from the [dashboard](https://turbopuffer.com/dashboard)
3. Set the `TURBOPUFFER_API_KEY` environment variable
4. Optionally set `TURBOPUFFER_REGION` (defaults to `gcp-us-central1`). See [available regions](https://turbopuffer.com/docs/regions).

## Usage

Import and register the adapter in your code:
```python
from cognee_community_vector_adapter_turbopuffer import register
```

Also, specify the dataset handler in the .env file:
```dotenv
VECTOR_DATASET_DATABASE_HANDLER="turbopuffer"
```

## Example
See example in `example.py` file.
