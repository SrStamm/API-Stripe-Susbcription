# Stripe Subscription

API developed with **FastAPI** to manage plans and subscriptions using **Stripe**.  
It allows you to create plans with price, name, description, and duration, and for users to subscribe to them.  
Subscriptions are automatically renewed before they expire.

# Features

- Plan management (`FREE`, `PRO`, `ENTERPRISE`, etc.)
- Automatic subscription creation and renewal
- Access validation based on plan
- Integration with Stripe Webhooks
- Notifications and background tasks with Redis + Celery
- Docker containers for rapid deployment
- Automated testing with Pytest

## Installation

First, you need to clone this repository.

```bash
git clone https://github.com/SrStamm/API-Stripe-Susbcription.git

cd API-Stripe-Subscription

pip install -r requirements.txt
```

To validate that everything works, run the tests:

```bash
# Comand to run all the tests
pytest

# Or, you can use bash scripts
./scripts/test.sh
```

## Usage

First, you need to create a `env.py` that will contain:

```
# Stripe API Key 
API_KEY=
# Stripe signature to validate received Webhooks
STRIPE_WEBHOOK_SECRET=

# Redis URL
REDIS_URL=redis://redis:6379/0

# Key and Algorithm for Tokens 
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256

# Expiration time to token 
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Postgres Data
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

# Postgres URL
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@stripe-db:5432/${POSTGRES_DB}
```


You can run the services whit Docker

```bash
# Docker CLI
docker-compose run

# Or whit bash scripts
./scripts/dev-containers.sh
```


And that's it! You should now be able to use the API with your favorite software to test the endpoints.

## License

[MIT](https://choosealicense.com/licenses/mit/)
