import requests

client_id = 'u6bpzmGFnxEJ18MR6wRi69cj8aPEZ6OG'
client_secret = 'qXqQGbWkNvB4me6H'

token_url = 'https://test.api.amadeus.com/v1/security/oauth2/token'

data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret
}

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

try:
    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        print(f"Access Token: {access_token}")
    else:
        print(f"Failed to retrieve access token: {response.status_code} - {response.text}")

except requests.exceptions.RequestException as e:
    print(f"Error retrieving access token: {e}")
