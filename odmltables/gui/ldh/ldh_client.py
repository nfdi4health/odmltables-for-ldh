from .client import HttpClient
from .data.project import Project
from .data.collection import Collection
from .data.data_file import DataFile
from .data.ldh_entitiy import LDHEntitiy, InstanceType
import PyQt5.QtWidgets as Qtw
import PyQt5.QtGui as QtGui

client = None

def check_credentials(url, apiToken):
    temp_client = HttpClient(url, apiToken)
    try:
        response = temp_client.get("institutions")
        global client
        client = temp_client
        return True
    except Exception as e:
        print("Credentials are not valid, please check them again.")
        return False

# returns id and name of first institution the user is associated with
def get_first_institution_of_user():
    response = client.get("institutions")
    id = response['data'][0]['id']
    response = client.get("institutions/" + str(id))
    name = response['data']['attributes']['title']
    return id, name

def get_first_user():
    response = client.get("people/current")
    id = response['data']['id']
    return id

def get_all_projects():
    # Get all pages
    current_user = client.get("people/current")
    project_dict = {}

    data = current_user['data']['relationships']['projects']['data']
    for entry in data:
        project_id = entry['id']
        project = fetch_project(project_id)
        project_dict[project_id] = project.get_title()

    return project_dict


def get_insitution_name(institution_id):
    institution = client.get("institutions/" + str(institution_id))
    return institution['data']['attributes']['title']


def create_project(project:Project):
    
    project_json = project.convertToJson()
    response = client.post("projects", json=project_json)

    if response.status_code == 200:
        project_id = response.json()['data']['id']
        project.set_id(project_id)
        return True, project_id
    else:
        return False, ""
    
def update_project(project:Project, attribute_dict):
    
    for key, edit in attribute_dict.items():
            if type(edit) == Qtw.QPlainTextEdit:
                project.change_attribute_value(key, edit.toPlainText())
            else:
                project.change_attribute_value(key, edit.text())

    project_json = project.convertToJson()
    response = client.patch("projects/" + project.id, json=project_json)

    if response.status_code == 200:
        project_id = response.json()['data']['id']
        project.set_id(project_id)
        return True, project_id
    else:
        return False, ""
    
def create_collection(collection: Collection):
    collection_json = collection.convertToJson()
    response = client.post("collections", json=collection_json)

    if response.status_code == 200:
        id = response.json()['data']['id']
        collection.set_id(id)
        return True, id
    else:
        return False, ""


def fetch_project(project_id):

    # 'data' - 'attributes': {'discussion_links': [], 'avatar': None, 'title': 'Default Project', 'description': None, 'web_page': None, 'wiki_page': None, 
    # 'default_license': 'CC-BY-4.0', 'start_date': None, 'end_date': None, 'members': [{'person_id': '1', 'institution_id': '1'}], 'topic_annotations': []},
    # data - 'relationships': {'project_administrators': {'data': []}, 'pals': {'data': []}, 'asset_housekeepers': {'data': []}, 'asset_gatekeepers': {'data': []}, 
    # 'organisms': {'data': []}, 'human_diseases': {'data': []}, 'people': {'data': [{'id': '1', 'type': 'people'}]}, 'institutions': {'data': [{'id': '1', 'type': 'institutions'}]},
    
    project_json = client.get("projects/" + str(project_id))

    project_id = project_json['data']['id']
    title = project_json['data']['attributes']['title']
    description = project_json['data']['attributes']['description']
    web_page = project_json['data']['attributes']['web_page']
    wiki_page = project_json['data']['attributes']['wiki_page']
    default_license = project_json['data']['attributes']['default_license']
    start_date = project_json['data']['attributes']['start_date']
    end_date = project_json['data']['attributes']['end_date']

    project = Project(title)
    project.change_description(description)
    project.change_web_page(web_page)
    project.change_wiki_page(wiki_page)
    project.change_default_license(default_license)
    project.change_start_date(start_date)
    project.change_end_date(end_date)

    # get institution id from here and fetch institution name
    for member in project_json['data']['attributes']['members']:
        project.add_member(member['person_id'], member['institution_id']) 

    #topic_annotations = project_json['data']['attributes']['topic_annotations']

    #organisms = project_json['data']['relationships']['organisms']['data']
    #human_diseases = project_json['data']['relationships']['human_diseases']['data']
    #"institpeople = project_json['data']['relationships']['people']['data']

    # TODO we can only have one institution, for now just take the first insitution in the list or of the member
    if project_json['data']['relationships']['institutions']['data']:
        institution_id = project_json['data']['relationships']['institutions']['data'][0]['id']
        institution_title = get_insitution_name(institution_id)
        project.set_institution(institution_id, institution_title)
    
    project.set_id(project_id)

    return project

        
def create_entity(entity, attribute_dict):

        for key, edit in attribute_dict.items():
            if type(edit) == Qtw.QPlainTextEdit:
                entity.change_attribute_value(key, edit.toPlainText())
            else:
                entity.change_attribute_value(key, edit.text())

        if entity.type == InstanceType.PROJECT:
            created, id = create_project(entity)
        else:
            if entity.type == InstanceType.COLLECTION:
                created, id = create_collection(entity)
            else:
                if entity.type == InstanceType.DATAFILE:
                    created, id = create_and_upload_data_file(entity)
                print("Unknown Entity Type")
                return False

        if created:
            entity.set_id(id)
            return True
        else: 
            return False



def create_and_upload_data_file(data_file, attribute_dict):

    for key, edit in attribute_dict.items():
            if type(edit) == Qtw.QPlainTextEdit:
                data_file.change_attribute_value(key, edit.toPlainText())
            else:
                data_file.change_attribute_value(key, edit.text())

    data_file_json = data_file.convertToJson()

    response = client.post("data_files", json=data_file_json)
    link_for_content_blob = response.json()['data']['attributes']['content_blobs'][0]['link']
    if response.status_code == 200:
        data_file_id = response.json()['data']['id']
        data_file.set_id(data_file_id)
        response = client.upload_file(link_for_content_blob, data_file.file_path)
        if response.status_code == 200:
            return True, data_file_id
        else:
            print("Error uploading file")
            return False, ""
    else:
        print("Error creating data file")
        return False, ""
    
