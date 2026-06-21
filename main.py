import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Porta 5000 é ocupada pelo AirPlay Receiver no macOS; usa 5001 por padrão.
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, port=port)
