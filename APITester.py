import requests  # Use the 'requests' library to make HTTP requests

BASE_URL = 'http://0.0.0.0:5100'  # Base URL for the API

def request_members(cookies=None):
    try:
        response = requests.get('http://0.0.0.0:5100/members/fpicarras', cookies=cookies)
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
        return response.cookies  # Return cookies to maintain session
    else:
        print("Login failed:", response.json())
        return None

print(request_members())
cookies = login('fpicarras', 'password')
print(request_members(cookies))
wait = input("Press Enter to continue...")  # Wait for user input
print(request_members(cookies))

