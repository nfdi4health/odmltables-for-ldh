from .ldh_entitiy import LDHEntitiy, InstanceType, Attribute, Relationship
import json

class DataFile(LDHEntitiy):

    def __init__(self, title: str):
        #super(DataFile, self).__init__(type=InstanceType.DATAFILE, title=title)
        self.attributes = {"title": Attribute("title", "Title", None, 0, True), 
                    "description": Attribute("description", "Description", None, 1, False), 
                    "projects": Attribute("projects", "Projects", None, 2, True),
                    "tags": Attribute("tags", "Tags", None,  3, False),
                    "license": Attribute("license", "License", None,  4, False),
                    }
    
        self.institution = {}
        self.projects = []
        self.members = []
        self.content_blobs = []
        self.file_path = None
        self.data_format = ""

        self.type = InstanceType.DATAFILE
        self.change_title(title)



    def set_id(self, id):
        self.id = id

    def add_tags(self, tags):
        old_tags = self.get_attribute_value("tags")
        if old_tags == None:
            old_tags = []
        self.change_attribute_value("tags", old_tags + tags)

    def add_member(self, person_id, institution_id):
        self.members.append([person_id, institution_id])

    # should originally be gotten from Project
    def change_default_license(self, default_license: str):
        self.change_attribute_value("default_license", default_license)


    def change_description(self, description: str):
        self.change_attribute_value("description", description)

    def set_content_blob(self, path):
        original_filename = path.split("/")[-1]
        if original_filename.endswith(".odml"):
            content_type = "application/xml"
            self.data_format = "xml"
        elif original_filename.endswith(".csv"):
            content_type = "text/csv"
            self.data_format = "csv"
        
        self.file_path = path

        self.content_blobs.append({"original_filename": original_filename, "content_type": content_type})


    def add_project(self, project_id, title):
        self.projects.append(project_id)
        self.change_attribute_value("projects", title)

    def get_title(self):
        return self.get_attribute_value("title")
    
    def convertToJson(self):
        attributes = {}
        for key, attribute in self.attributes.items():
            if attribute.value and attribute.value != "" and attribute.key != "projects":
                    attributes[key] = attribute.value

        attributes["members"] = []
        people_data = []
        if self.members:
            for member in self.members:
                attributes["members"].append({"person_id": member[0], "institution_id": member[1]})
                person = {"id": member[0], "type": "people"}
                people_data.append(person)

        # add content blob 
        attributes["content_blobs"] = self.content_blobs

        # not mandatory - what would fit??
        #attributes["data_type_annotations"] =  [
        #                                            {
        ##                                            "label": "Sequence features metadata",
        #                                            "identifier": "http://edamontology.org/data_2914"
        ##                                            }
        #                                        ]
        
        # for data file you can select an assy - but not mandatory 
        # data files cannot be associated with collections during creation (?) - can be added to a collection later 
        # depenending on path either xml or csv
        # csv does not exists in the edam ontology
        #if self.data_format == "xml":
         #   attributes["data_format_annotations"] = [
          #                                          {
           #                                         "label": "XML",
            #                                        "identifier": "http://edamontology.org/format_2333"
             #                                       }
              #                                  ]
        
        projects = []
        for project in self.projects:
            projects.append({"id": project, "type": "projects"})

        data = {"data": {
                "type": "data_files",
                "attributes": attributes,
                "relationships":{
                    "creators": {
                        "data": people_data
                    },
                    "projects": {
                        "data": projects
                    }
                }
            }
        }

        return data