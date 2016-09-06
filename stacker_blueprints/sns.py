from stacker.blueprints.base import Blueprint

from troposphere import (
    sns,
    Ref,
    GetAtt,
    Output,
)

def check_topic(topic):
    sns_topic_properties = [
        "DisplayName",
        "Subscription",
    ]

    for key in topic.keys():
        # Check to see if there are any keys not the properties list.
        # If that's the case, bail since that could cause unexpected
        # outcomes.
        if key not in sns_topic_properties:
            raise ValueError(
                "%s is not a valid SNS topic property" % key
            )

        if key == "Subscription":
            subs = []
            for sub in topic["Subscription"]:
                subs.append(sns.Subscription(**sub))

            topic["Subscription"] = subs

    return topic

class Topics(Blueprint):
    """Manages the creation of SNS topics."""

    VARIABLES = {
        "Topics": {
            "type": dict,
            "description": "Dictionary of SNS Topic definitions",
        }
    }

    def create_template(self):
        variables = self.get_variables()

        for topic_name, topic_config in variables["Topics"].items():
            topic_config = check_topic(topic_config)
            self.create_topic(topic_name, topic_config)

    def create_topic(self, topic_name, topic_config):
        t = self.template

        t.add_resource(
            sns.Topic(
                topic_name,
                **topic_config
            )
        )

        t.add_output(Output(topic_name + "Name", Value=GetAtt(topic_name, "TopicName")))
        t.add_output(Output(topic_name + "Arn", Value=Ref(topic_name)))
