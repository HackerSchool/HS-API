import requests  # Use the 'requests' library to make HTTP requests

BASE_URL = 'http://0.0.0.0:5100'  # Base URL for the API

def request_members(cookies=None):
    try:
        response = requests.get(f'{BASE_URL}/members/fpicarras', cookies=cookies)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Function to log in
def login(username, password):
    login_url = f'{BASE_URL}/login'
    data = {'username': username, 'password': password}
    response = requests.post(login_url, json=data)
    
    if response.status_code == 200:
        print(f"Logged in as {username}")
        # Inspect cookies received from server after login
        print("Cookies received after login:", response.cookies)
        return response.cookies  # Return cookies to maintain session
    else:
        print("Login failed:", response.json())
        return None

# Trying the request without cookies
print(request_members())
cookies = login('fpicarras', 'password')
# Make request with cookies to see if authentication works
print(request_members(cookies))

# Wait for user input
input("Press Enter to continue...")  # Wait for user input

# Make another request to test if cookies still work
print(request_members(cookies))
