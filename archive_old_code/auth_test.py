import requests
import json
import getpass

# Your TastyTrade credentials
USERNAME = "robertwayne"  # Replace with your username
PASSWORD = "Tastytrade168*"      # Replace with your password

# The API endpoint for authentication
url = "https://api.tastytrade.com/sessions"

# The first request to initiate the login
print("Attempting to authenticate with username and password...")
initial_headers = {
    'Content-Type': 'application/json'
}
data = {
    "login": USERNAME,
    "password": PASSWORD
}

# Make the initial request
response = requests.post(url, headers=initial_headers, json=data)

# Check the response
if response.status_code == 201:
    print("SUCCESS: Authentication worked without TFA!")
    result = response.json()
    print("Session token received.")
    # You can save the session token here for future requests
    session_token = result['data']['session-token']
    print("Session token: ", session_token)

elif response.status_code == 401 and "two-factor" in response.headers.get("WWW-Authenticate", "").lower():
    print("TFA is required. Please enter your authentication code.")
    
    # Prompt the user to enter the TFA code from their authenticator app
    tfa_code = input("Enter your TFA code: ")
    
    # The second request, including the TFA code in the headers
    tfa_headers = {
        'Content-Type': 'application/json',
        'X-Tastytrade-Two-Factor-Auth': tfa_code
    }
    
    print("Attempting to authenticate with TFA code...")
    tfa_response = requests.post(url, headers=tfa_headers, json=data)
    
    # Check the TFA response
    if tfa_response.status_code == 201:
        print("SUCCESS: TFA authentication worked!")
        result = tfa_response.json()
        print("Session token received.")
        # You can save the session token here
        # session_token = result['data']['session-token']
    else:
        print("FAILED: TFA authentication failed.")
        print(f"Status code: {tfa_response.status_code}")
        print(f"Error: {tfa_response.text}")

else:
    print("FAILED: Initial authentication failed.")
    print(f"Status code: {response.status_code}")
    print(f"Error: {response.text}")
