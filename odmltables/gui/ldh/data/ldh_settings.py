from .odmlwithselection import OdmlTableWithSelection
from .project import Project

class LDHSetting():

    project = None
    study = None
    investigation = None
    #collection = None
    url = None
    api_token = None
    input_file = None
    odml_selection = None
    client = None
    institution_id = None
    institution_name = None
    user_id = None

    private_odml_path = None
    private_odml_summary = None


    data_set_link_text = None

    def __init__(self):
        pass

    def set_data_set_link_text(self, text):
        self.data_set_link_text = text

    def set_private_odml_path(self, path):
        self.private_odml_path = path

    def set_private_odml_summary_path(self, path):
        self.private_odml_summary = path

    def set_client(self, client):
        self.client = client

    def set_project(self, project: Project):
        self.project = project

    def set_study(self, study: str):
        self.study = study

    def set_investigation(self, investigation: str):
        self.investigation = investigation

    def set_url(self, url: str):
        self.url = url

    def set_api_token(self, api_token: str):
        self.api_token = api_token

    def set_input_file(self, input_file: str):
        self.input_file = input_file
    
    def set_odml_selection(self, odml_selection: OdmlTableWithSelection):
        self.odml_selection = odml_selection

    def set_institution(self, institution_id: str, institution_name):
        self.institution_id = institution_id
        self.institution_name = institution_name

    def set_user(self, user_id: str):
        self.user_id = user_id

    #def set_collection(self, collection):
    #    self.collection = collection
