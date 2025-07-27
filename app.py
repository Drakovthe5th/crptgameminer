from src.web.flask_app import create_app

app = create_app()

if __name__ == '__main__':
    # Remove app.run() for production
    pass
   # app.run(host='0.0.0.0', port=5000)