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

        # if endpoint == 'institutions':
        #     return {
        #         'data': [
        #             {
        #                 'id': '1',
        #                 'type': 'institutions',
        #                 'attributes': {
        #                     'title': 'Default Institution'
        #                 },
        #                 'links': {
        #                     'self': '/institutions/1'
        #                 }
        #             }
        #         ],
        #         'jsonapi': {
        #             'version': '1.0'
        #         },
        #         'links': {
        #             'self': '/institutions?page%5Bnumber%5D=1&page%5Bsize%5D=1000000',
        #             'first': '/institutions?page%5Bnumber%5D=1&page%5Bsize%5D=1000000',
        #             'prev': None,
        #             'next': None,
        #             'last': '/institutions?page%5Bnumber%5D=1&page%5Bsize%5D=1000000'
        #         },
        #         'meta': {
        #             'base_url': 'http://localhost:3000',
        #             'api_version': '0.3'
        #         }
        #     }
        # elif endpoint == 'projects/1':
        #     return {
        #         'data': {
        #             'id': '1',
        #             'type': 'projects',
        #             'attributes': {
        #                 'discussion_links': [],
        #                 'avatar': None,
        #                 'title': 'Default Project',
        #                 'description': None,
        #                 'web_page': None,
        #                 'wiki_page': None,
        #                 'default_license': 'CC-BY-4.0',
        #                 'start_date': None,
        #                 'end_date': None,
        #                 'members': [
        #                     {'person_id': '1', 'institution_id': '1'}
        #                 ],
        #                 'topic_annotations': []
        #             },
        #             'relationships': {
        #                 'project_administrators': {'data': []},
        #                 'pals': {'data': []},
        #                 'asset_housekeepers': {'data': []},
        #                 'asset_gatekeepers': {'data': []},
        #                 'organisms': {'data': []},
        #                 'human_diseases': {'data': []},
        #                 'people': {'data': [{'id': '1', 'type': 'people'}]},
        #                 'institutions': {'data': [{'id': '1', 'type': 'institutions'}]},
        #                 'programmes': {'data': []},
        #                 'investigations': {'data': []},
        #                 'studies': {'data': []},
        #                 'assays': {'data': []},
        #                 'data_files': {'data': []},
        #                 'file_templates': {'data': []},
        #                 'placeholders': {'data': []},
        #                 'models': {'data': []},
        #                 'sops': {'data': []},
        #                 'publications': {'data': []},
        #                 'presentations': {'data': []},
        #                 'events': {'data': []},
        #                 'documents': {'data': []},
        #                 'workflows': {'data': []},
        #                 'collections': {'data': []}
        #             },
        #             'links': {
        #                 'self': '/projects/1'
        #             },
        #             'meta': {
        #                 'created': '2024-08-15T09:58:08.000Z',
        #                 'modified': '2024-08-15T09:58:44.000Z',
        #                 'api_version': '0.3',
        #                 'base_url': 'http://localhost:3000',
        #                 'uuid': 'cbfeb080-3d1a-013d-a97d-799025de9a5d'
        #             }
        #         },
        #         'jsonapi': {
        #             'version': '1.0'
        #         }
        #     }
        # elif endpoint == 'institutions/1':
        #     return {
        #         'data': {
        #             'id': '1',
        #             'type': 'institutions',
        #             'attributes': {
        #                 'discussion_links': [],
        #                 'avatar': None,
        #                 'title': 'Default Institution',
        #                 'country': 'United Kingdom',
        #                 'country_code': 'GB',
        #                 'city': None,
        #                 'address': None,
        #                 'web_page': None
        #             },
        #             'relationships': {
        #                 'people': {
        #                     'data': [{'id': '1', 'type': 'people'}]
        #                 },
        #                 'projects': {
        #                     'data': [{'id': '1', 'type': 'projects'}]
        #                 }
        #             },
        #             'links': {
        #                 'self': '/institutions/1'
        #             },
        #             'meta': {
        #                 'created': '2024-08-15T09:58:08.000Z',
        #                 'modified': '2024-08-15T09:58:08.000Z',
        #                 'api_version': '0.3',
        #                 'base_url': 'http://localhost:3000',
        #                 'uuid': 'cc02d4e0-3d1a-013d-a97d-799025de9a5d'
        #             }
        #         },
        #         'jsonapi': {
        #             'version': '1.0'
        #         }
        #     }

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