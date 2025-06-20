# roast-my-code
We provide the best roasts.

## Installation
Install ollama. See the [ollama installation guide](https://ollama.com/docs/installation).

To install the dependencies, run:
```bash
conda create -n roaster python=3.12
```
Then activate the environment:
```bash
conda activate roaster
```
Install the requirements:
```bash
pip install -r requirements.txt
```
We are using Ollama to serve local LLMs:
```bash
sudo snap install ollama
```

If you want to use the speech output feature, you need to install `espeak-ng`. You can do this by running:
```bash
sudo apt-get -y install espeak-ng
```

### Environment Variables
To authenticate to services, you can either export env vars in your shell or create a `.env` file at the project root (see `.env.example`).

For GitHub profile roasting:
```bash
export GITHUB_TOKEN=your_token_here
```

If you plan to use the OpenAI Python client in the future (not required for Ollama):
```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

### Docker Compose Setup

```bash
sudo docker compose up --build
```

## Usage
Pull your favourite LLM:
```bash
ollama pull mistral:latest
```

To run the application, use:
```bash
streamlit run main.py
```
  
## Stripe Integration

We support purchasing "pay-it-forward" credits (roasts) via Stripe Checkout.  Credits are used to generate code roasts.
Before you begin, register for a free Stripe account at https://dashboard.stripe.com/register. In the Dashboard, toggle “Viewing test data” (top right) to work in Test mode.

### 1) Environment Variables
Add the following variables to your `.env` file (or export in your shell):
```ini
# Stripe API Keys (get these from your Stripe Dashboard)
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
# Your Stripe webhook signing secret (from Developers → Webhooks → your endpoint)
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

### 2) Install and Configure Stripe CLI (for local testing)
Follow Stripe's [CLI install guide](https://stripe.com/docs/stripe-cli#install) for your platform, or use Docker:

- macOS (Homebrew):
  ```bash
  brew install stripe/stripe-cli/stripe
  ```
- Debian/Ubuntu (apt):
  ```bash
  curl -sS https://packages.stripe.dev/debian/checkout/install.sh | sudo bash
  sudo apt-get install stripe
  ```
- RHEL/CentOS (yum):
  ```bash
  curl -sS https://packages.stripe.dev/rpm/checkout/install.sh | sudo bash
  sudo yum install stripe
  ```
- Windows (Scoop):
  ```powershell
  scoop install stripe
  ```
- Or via Docker (no local install required):
  ```bash
  docker run --rm -it stripe/stripe-cli:latest listen --forward-to localhost:5030/webhook
  ```

After installation or Docker launch, authenticate your CLI session (if installed locally):
```bash
stripe login
```

### 3) Forward Webhooks Locally
Use the Stripe CLI to forward events to your local FastAPI server:
```bash
stripe listen --forward-to localhost:5030/webhook
```
This will print out a webhook signing secret (`whsec_...`) and forward `checkout.session.completed` events to `http://localhost:5030/webhook`.
### 4) Testing Purchases
1. Start your FastAPI server (default at port 5030).
2. Open the web UI, enter a dollar amount and click **Pay & Buy Roasts**, then complete the test checkout.
3. After payment, the CLI will forward the webhook and your local DB will increment the roast counter.
  
#### Test Cards
Use Stripe’s Test mode (Dashboard toggle “Viewing test data”).  In Checkout, try:
- 4242 4242 4242 4242 — successful payment
- 4000 0000 0000 9995 — generic decline
- 4000 0000 0000 3220 — requires 3D Secure authentication
1. Start your FastAPI server (default at port 5030).
2. Open the web UI, click **Buy Credits**, and complete the test checkout.
3. After payment, the CLI will forward the webhook and your local DB will increment the credit counter.

Now you’re all set to accept test payments and see credits update in real-time!

## Docker Compose Support for Stripe CLI
We've added a `stripe-cli` service to `docker-compose.yml` that will forward webhooks from Stripe into your local FastAPI server, with login state persisted across restarts.

1. Perform a one-time login in the Stripe CLI container (credentials are stored in a Docker volume):
```bash
docker compose run --rm stripe-cli login
```
This will open the Stripe authentication flow; follow the prompts to log in.

2. Start (or restart) all services, including stripe-cli:
```bash
docker compose up --build
```
The `stripe-cli` container will now automatically forward `checkout.session.completed` events to `http://localhost:5030/webhook`.