from .ldh_entitiy import LDHEntitiy, InstanceType, Attribute, Relationship

class Study(LDHEntitiy):

    

    # TODO at some point add extended Metadata stuff

    def __init__(self, title: str):
        #super(Study, self).__init__(type=InstanceType.STUDY, title=title)
        self.attributes = {"title": Attribute("title", "Title", None, 0, True), 
                    "description": Attribute("description", "Description", None, 1, False), 
                    "study_position": Attribute("study_position", "Study Position", None, 2, False), 
                    "tags": Attribute("tags", "Tags", [], 3, False),
                    "discussion_channels": Attribute("discussion_channels", "Discussion Channels", [],  4, False)
                    }
        self.type = InstanceType.STUDY
        self.change_title(title)

    
    def change_description(self, description: str):
        self.change_attribute_value("description", description)

    # TODO type URL
    def change_study_position(self, study_position: str):
        self.change_attribute_value("study_position", study_position)
    
    # TODO removal functions
    def add_discussion_channel(self, discussion_channel: str):
        curr_discussion_channel = self["discussion_channel"].value
        if not discussion_channel in curr_discussion_channel:
            curr_discussion_channel.append(discussion_channel)
            self.change_attribute_value("tags", discussion_channel)

    def add_tag(self, tag: str):
        curr_tags = self["tags"].value
        if not tag in curr_tags:
            curr_tags.append(tag)
            self.change_attribute_value("tags", curr_tags)