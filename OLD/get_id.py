import requests

def get_session_id(username, password):
    url = 'https://example.com/login'  # Replace with the actual login URL
    payload = {
        'username': username,
        'password': password
    }
    
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        # Assuming the session ID is returned in the response
        session_id = response.cookies.get('session_id')  # Adjust based on how the session ID is returned
        return session_id
    else:
        raise Exception("Login failed with status code: {}".format(response.status_code))
