from flask import Flask, request, render_template
import joblib
import numpy as np

# Load both models
rf_model = joblib.load('random_forest_model.pkl')
svc_model = joblib.load('linear_svc_model.pkl')

# Initialize Flask app
app = Flask(__name__)

# Function to safely convert hex to integer
def safe_hex_to_int(hex_str):
    try:
        return int(hex_str, 16)
    except ValueError:
        return None  # Return None if conversion fails

@app.route('/', methods=['GET', 'POST'])
def index():
    # Default attack status (green for all)
    attack_status = {
        'Fuzzy': 'green',
        'DoS': 'green',
        'Gear': 'green',
        'RPM': 'green',
    }

    if request.method == 'POST':
        try:
            # Get the input CAN IDs
            can_ids = request.form['can_ids']
            can_ids_list = []
            
            # Process each CAN ID (hexadecimal format)
            for can_id in can_ids.split(','):
                can_id = can_id.strip()
                if can_id:
                    # Convert CAN ID from hex to integer
                    converted_can_id = safe_hex_to_int(can_id)
                    if converted_can_id is not None:
                        can_ids_list.append(converted_can_id)
                    else:
                        raise ValueError(f"Invalid CAN ID: {can_id} (not a valid hexadecimal number)")

            # Check if the list is empty
            if not can_ids_list:
                return render_template('index.html', error="Please enter valid CAN IDs.", attack_status=attack_status)

            # Prepare features for prediction (assuming Flag = 1 for abnormal)
            input_features = np.array([[can_id, 1] for can_id in can_ids_list])

            # Predict using both models
            rf_predictions = rf_model.predict(input_features)
            svc_predictions = svc_model.predict(input_features)

            print("rf_predictions : " , rf_predictions)
            print("svc_predictions : " , svc_predictions)
            # Combine predictions from both models
            combined_prediction = list(rf_predictions) + list(svc_predictions)
            
            # this is our final predictions
            combined_predictions = rf_predictions

            # Determine which attacks are predicted
            attack_status = {
                'Fuzzy': 'red' if 'FUZZY' in combined_predictions else 'green',
                'DoS': 'red' if 'DOS' in combined_predictions else 'green',
                'Gear': 'red' if 'GEAR' in combined_predictions else 'green',
                'RPM': 'red' if 'RPM' in combined_predictions else 'green',
            }

            return render_template('index.html', attack_status=attack_status)

        except Exception as e:
            return render_template('index.html', error=f"An error occurred: {str(e)}", attack_status=attack_status)

    # Render the form for GET requests
    return render_template('index.html', attack_status=attack_status)

if __name__ == '__main__':
    app.run(debug=True)
