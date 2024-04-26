import requests

class HttpClient:

    def __init__(self, base_url, apitoken):

        self.base_url = base_url
        self.apitoken = apitoken
        self.headers = {
            "Authorization": "Token " + self.apitoken,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
            }

        # fetch projects of user
        # add a new project
        # update an existing project

    def get(self, endpoint, params=None):
        response = requests.get(self.base_url + endpoint, params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint, json=None):
        response = requests.post(self.base_url + endpoint, json=json, headers=self.headers)
        response.raise_for_status()
        return response

    def patch(self, endpoint, json=None):
        response = requests.patch(self.base_url + endpoint,json=json, headers=self.headers)
        response.raise_for_status()
        return response

    def delete(self, endpoint):
        response = requests.delete(self.base_url + endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()
        
    def upload_file(self, link, file_path):
        with open(file_path, 'rb') as f:
            file_content = f.read()
        headers = self.headers.copy()
        headers['Content-Type'] = 'application/octet-stream'
        response = requests.put(link, data=file_content, headers=headers)

        response.raise_for_status()
        return response