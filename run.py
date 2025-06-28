from dotenv import load_dotenv
load_dotenv()
from applications.pdf import create_app

app = create_app()

if __name__ == '__main__':
    # Only use Flask dev server in development
    import os
    if os.environ.get('FLASK_ENV') == 'development':
        app.run(debug=True, host='0.0.0.0', port=8000)
    else:
        # In production, this file is used by Gunicorn
        # The app object is imported by gunicorn
        pass 