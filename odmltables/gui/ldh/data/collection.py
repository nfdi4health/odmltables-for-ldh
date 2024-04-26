from .ldh_entitiy import LDHEntitiy, InstanceType, Attribute, Relationship


class Collection(LDHEntitiy):


    def __init__(self, title: str):
        self.attributes = {"title": Attribute("title", "Title", None, 0, True), 
                    "description": Attribute("description", "Description", None, 1, False), 
                    "license": Attribute("license", "License", None, 2, False),
                    "sharing": Attribute("sharing", "Sharing", None, 3, False),
                    "tags": Attribute("tags", "Tags", [], 4, False),
                    "attributions": Attribute("attributions", "Attributions", [], 5, False),
                    "projects": Attribute("projects", "Projects", None, 6, False),
                    }
    
        self.relationships = {}
        self.institution = {}
        self.members = []
        self.projects = []

        self.type = InstanceType.COLLECTION
        self.change_title(title)


    def set_id(self, id):
        self.id = id

    def set_institution(self, id, title):
        self.institution["id"] = id
        self.institution["title"] = title
        self.change_institution_name(title)

    def change_institution_name(self, institution_name: str):
        self.change_attribute_value("institution_name", institution_name)

    def change_web_page(self, web_page: str):
        self.change_attribute_value("web_page", web_page)


    def change_sharing(self, sharing: str):
        self.change_attribute_value("sharing", sharing)

    def change_description(self, description: str):
        self.change_attribute_value("description", description)

    def change_tags(self, tags: list[str]):
        self.change_attribute_value("tags", tags)

    def change_attributions(self, attributions: list[str]):
        self.change_attribute_value("attributions", attributions)

    def add_member(self, person_id, institution_id):
        self.members.append([person_id, institution_id])

    def add_project(self, project_id, title):
        self.projects.append(project_id)
        self.change_attribute_value("projects", title)

    # make it not settabel for now, only chose insitute of user
    def change_institution_name(self, institution_name: str):
        self.change_attribute_value("institution_name", institution_name)

    def get_title(self):
        return self.get_attribute_value("title")
    
    def convertToJson(self):
        # TODO anpassen an Collection
        attributes = {}
        for key, attribute in self.attributes.items():
            if attribute.value and attribute.value != "" and attribute.key != "institution_name" and attribute.key != "projects":
                    attributes[key] = attribute.value

        creators = []
        if self.members:
            for member in self.members:
                creators.append({"person_id": member[0], "institution_id": member[1]})

        
        projects = []
        for project in self.projects:
            projects.append({"id": project, "type": "projects"})

        data = {"data": {
                "type": "collections",
                "attributes": attributes,
                "relationships": {
                    "projects": {
                            "data": projects
                    },
                    "creators": {
                        "data": creators
                    }
                }
            }
        }


        return data
