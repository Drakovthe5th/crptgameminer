from src.web.flask_app import create_app

app = create_app()

if __name__ == '__main__':
    # This is just for local testing
    app.run(host='0.0.0.0', port=5000)