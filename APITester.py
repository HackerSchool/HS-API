import requests  # Use the 'requests' library to make HTTP requests
from base64 import b64encode, b64decode

BASE_URL = 'http://0.0.0.0:5100'  # Base URL for the API

def request_members(cookies=None):
    try:
        response = requests.get(f'{BASE_URL}/members', cookies=cookies)
        print(response)
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

# Example of a create user function
def create_user(cookies, istID, memberNumber, name, username, password, join_date, course, description, mail):
    create_member_url = f'{BASE_URL}/members'
    data = {
        "istID": istID,
        "memberNumber": memberNumber,
        "name": name,
        "username": username,
        "password": password,
        "join_date": join_date,
        "course": course,
        "description": description,
        "mail": mail
    }
    response = requests.post(create_member_url, json=data, cookies=cookies)
    print(response.json())

def edit_user(cookies, memberNumber, name):
    edit_member_url = f'{BASE_URL}/members/fpicarras'
    data = {
        "memberNumber": memberNumber,
        "name": name,
        "password": "password"
    }
    response = requests.put(edit_member_url, json=data, cookies=cookies)
    print(response.json())

def delete_user(cookies, username_to_delete):
    response = requests.delete(f'{BASE_URL}/members/{username_to_delete}', cookies=cookies)
    print(response.json())

def create_project(cookies, name, description, state, date):
    create_project_url = f'{BASE_URL}/projects'
    data = {
        "name": name,
        "description": description,
        "start_date": date,
        "state": state
    }
    response = requests.post(create_project_url, json=data, cookies=cookies)
    print(response.json())

def request_projects(cookies):
    response = requests.get(f'{BASE_URL}/projects', cookies=cookies)
    print(response.json())

def edit_project(cookies, proj_id, description):
    edit_member_url = f'{BASE_URL}/projects/{proj_id}'
    data = {
        "description": description
    }
    response = requests.put(edit_member_url, json=data, cookies=cookies)
    print(response.json())

def delete_project(cookies, proj_id):
    response = requests.delete(f'{BASE_URL}/projects/{proj_id}', cookies=cookies)
    print(response.json())

def send_image(cookies, username, image_file):
    with open(image_file, 'rb') as file:
        image_data = file.read()
        image_data = b64encode(image_data).decode('utf-8')
    image_url = f'{BASE_URL}/projects/{username}/logo'
    data = {
        "image": image_data
    }
    response = requests.post(image_url, json=data, cookies=cookies)
    print(response.json())

def recieve_image(cookies, username):
    image_url = f'{BASE_URL}/projects/{username}/logo'
    response = requests.get(image_url, cookies=cookies)
    if 'image' in response.json():
        image_data = response.json()['image']
        image_data = b64decode(image_data)
        with open(f'returned-{username}.png', 'wb') as file:
            file.write(image_data)
    else:
        print(response.json())

def link_member_project(cookies, username, proj_id, entry_date, contributions, exit_date):
    link_url = f'{BASE_URL}/link/{username}/{proj_id}'
    data = {
        "entry_date": entry_date,
        "contributions": contributions,
        "exit_date": exit_date
    }
    response = requests.post(link_url, json=data, cookies=cookies)
    print(response.json())

def edit_member_project(cookies, username, proj_id, entry_date, contributions, exit_date):
    link_url = f'{BASE_URL}/link/{username}/{proj_id}'
    data = {
        "contributions": contributions,
    }
    response = requests.put(link_url, json=data, cookies=cookies)
    print(response.json())

def delete_member_project(cookies, username, proj_id):
    link_url = f'{BASE_URL}/link/{username}/{proj_id}'
    response = requests.delete(link_url, cookies=cookies)
    print(response.json())

# Trying the request without cookies
print(request_members())
cookies = login('fpicarras', 'password')
# Make request with cookies to see if authentication works
print(request_members(cookies))

create_user(cookies, "ist123", "69", "João Pinheiros de Sá", "jpinhas", "123", "7/10/2024", "LEFT", "they/them", "mail@mail.mail")
edit_user(cookies, "44", "Filipe Correia")
# Make another request to test if cookies still work
input("Press a key to continue...")
print(request_members(cookies))

create_project(cookies, "Test Project", "ahahahah", "Almost", "7/10/2024")
request_projects(cookies)
edit_project(cookies, 3, "testi")
request_projects(cookies)

delete_project(cookies, 3)
delete_user(cookies, "jpinhas")
print(request_members(cookies))
request_projects(cookies)

send_image(cookies, "1", "img_teste.png")
recieve_image(cookies, "1")

link_member_project(cookies, "fpicarras", 1, "7/10/2024", "All", "7/10/2025")
input("Press a key to continue...")
edit_member_project(cookies, "fpicarras", 1, "7/10/2024", "None, this sucker did nothing", "7/10/2025")
delete_member_project(cookies, "fpicarras", 1)
edit_member_project(cookies, "fpicarras", 1, "7/10/2024", "This should not work, link does not exist", "7/10/2025")