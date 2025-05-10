# 🤖 Kraken DCA Bot

This is a simple and fully customizable Python bot for performing periodic purchases (**DCA – Dollar Cost Averaging**) on **Kraken**, with email notifications once an order is completed.

You can freely configure the **order type**, **execution frequency**, **investment strategy**, and even the **crypto asset to buy** (BTC, ETH, or any other available on Kraken).

By default, the bot places **limit orders with post-only mode**, which means it acts as a **maker** (the order is added to the order book at a price below market and doesn't execute immediately). This avoids the higher fees Kraken charges to **takers**, reducing transaction costs.

---

## ⚠️ Security Warning

> **This script can execute real purchase orders on Kraken.**  
> Before running it, make sure to review your `.env` file carefully and set `EXECUTE_BOT=false` if you just want to test it in safe mode.  
> **Never share your real `.env` file. Use the included `.env.example` as a template.**

---

## 🛠 Requirements

- Python 3.8+
- Kraken account with API access enabled
- Gmail account (recommended with an app password)
- A `.env` file with your credentials

---

## 🚀 Usage

1. Clone this repository:

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Copy the example environment file and edit it:

```bash
cp .env.example .env
```

4. Fill in the `.env` file with your actual credentials.

5. Run the bot:

```bash
python dca_bot.py
```

---

## 🔧 Configuration

- `EXECUTE_BOT=true`: enables the bot (executes real orders)
- `EXECUTE_BOT=false`: safe mode, the bot won’t run
- `to_invest`: amount to invest, defined directly in the script (`20.83 EUR` by default)

---

## 📬 Notification

You’ll receive an email with the order details (or error info) after each attempt.  
The notification is sent from your Gmail account to the address configured in `.env`.

---

## ✅ Status

This script is functional and has been tested with real money, but it is provided **as-is** with no warranty or support.  
**Use at your own risk.**

---

## 📄 License

MIT
