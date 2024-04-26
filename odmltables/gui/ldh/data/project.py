from .ldh_entitiy import LDHEntitiy, InstanceType, Attribute, Relationship
import json

class Project(LDHEntitiy):

    

    def __init__(self, title: str):
        #super(Project, self).__init__(type=InstanceType.PROJECT, title=title)
        self.attributes = {"title": Attribute("title", "Title", None, 0, True), 
                    "description": Attribute("description", "Description", None, 1, False), 
                    "web_page": Attribute("web_pag", "Web page", None,  2, False),
                    "wiki_page": Attribute("wiki_page", "Wiki page", None,  4, False),
                    "default_license": Attribute("default_license", "Default license", None,  5, False),
                    "start_date": Attribute("start_date", "Start date", None,  6, False),
                    "end_date": Attribute("end_date", "End date", None,  7, False),
                    "institution_name": Attribute("institution_name", "Type the name of the Institution", None, 4, True)
                    }
    
        self.institution = {}
        self.members = []

        self.type = InstanceType.PROJECT
        self.change_title(title)
        #self.change_institution_name(institution_name)

    def get_title(self):
        return self.get_attribute_value("title")

    def set_id(self, id):
        self.id = id

    def set_institution(self, id, title):
        self.institution["id"] = id
        self.institution["title"] = title
        self.change_institution_name(title)

    def add_member(self, person_id, institution_id):
        self.members.append([person_id, institution_id])

    # make it not settabel for now, only chose insitute of user
    def change_institution_name(self, institution_name: str):
        self.change_attribute_value("institution_name", institution_name)

    def change_wiki_page(self, wiki_page: str):
        self.change_attribute_value("wiki_page", wiki_page)

    def change_default_license(self, default_license: str):
        self.change_attribute_value("default_license", default_license)
    
    def change_start_date(self, start_date: str):
        self.change_attribute_value("start_date", start_date)

    def change_end_date(self, end_date: str):
        self.change_attribute_value("end_date", end_date)

    def get_description(self):
        return self.get_attribute_value("description")

    def change_description(self, description: str):
        self.change_attribute_value("description", description)

    # TODO type URL
    def change_web_page(self, web_page: str):
        self.change_attribute_value("web_page", web_page)


    def get_title(self):
        return self.get_attribute_value("title")
    
    def convertToJson(self):
        attributes = {}
        for key, attribute in self.attributes.items():
            if attribute.value and attribute.value != "" and attribute.key != "institution_name":
                    attributes[key] = attribute.value

        attributes["members"] = []
        people_data = []
        if self.members:
            for member in self.members:
                attributes["members"].append({"person_id": member[0], "institution_id": member[1]})
                person = {"id": member[0], "type": "people"}
                people_data.append(person)
        
        institution_data = []
        if self.institution:
            institution_data.append({"id": self.institution["id"], "type": "institutions"})
        data = {"data": {
                "type": "projects",
                "attributes": attributes,
                "relationships": {
                    "institutions": {
                            "data": institution_data
                    },
                    "people": {
                        "data": people_data
                    }
                }
            }
        }

        return data