from flask import Flask, jsonify, request
from datetime import datetime
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
import os

app = Flask(__name__)

# Configure Application Insights only if connection string is present
if 'APPLICATIONINSIGHTS_CONNECTION_STRING' in os.environ:
    middleware = FlaskMiddleware(
        app,
        exporter=AzureLogHandler(connection_string=os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING'])
    )
    logger = logging.getLogger(__name__)
    logger.addHandler(AzureLogHandler(connection_string=os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING']))
else:
    logger = logging.getLogger(__name__) # Fallback logger

@app.route('/')
def hello():
    logger.warning('Hello endpoint was hit!')
    return "Hello from Azure Microservice!"

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/age', methods=['GET', 'POST'])
def calculate_age():
    year_of_birth = None
    if request.method == 'GET':
        year_of_birth = request.args.get('year_of_birth')
        if year_of_birth is None:
            return '''
            <h3>Calculate Age</h3>
            <form action="/age" method="get">
                <label for="year_of_birth">Enter Year of Birth:</label>
                <input type="number" id="year_of_birth" name="year_of_birth" required>
                <button type="submit">Calculate</button>
            </form>
            '''
    elif request.method == 'POST':
        data = request.get_json()
        if data:
            year_of_birth = data.get('year_of_birth')
    
    if not year_of_birth:
        return jsonify({"error": "year_of_birth is required. Pass it as a query parameter or in JSON body."}), 400
    
    try:
        yob = int(year_of_birth)
        current_year = datetime.now().year
        if yob > current_year:
             return jsonify({"error": "Year of birth cannot be in the future"}), 400
        age = current_year - yob
        return jsonify({"age": age, "year_of_birth": yob, "current_year": current_year})
    except ValueError:
        return jsonify({"error": "Invalid year_of_birth. Must be an integer."}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
