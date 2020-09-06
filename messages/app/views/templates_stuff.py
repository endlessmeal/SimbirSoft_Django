import json


def temp_text(template, params):
    temp_dict = template.to_dict()
    return temp_dict["text"].format(**params)


def msg_to_json(msg_text, msg_to, msg_subject):
    return json.dumps({"text": msg_text, "to": msg_to, "subject": msg_subject,})
