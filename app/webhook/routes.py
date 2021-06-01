from flask import Blueprint, jsonify,json,request
from app.extensions import mongo
webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    if request.headers['Content-Type'] == 'application/json':
        data = json.dumps(request.json,indent=4)
        parsed_data = json.loads(data)
        object = {}
        if request.headers['X-GitHub-Event'] == 'pull_request':
            base = parsed_data["pull_request"] 
            if parsed_data["action"] == "closed":
                object["action"] = "MERGE_REQ"
                object["request_id"] = base["merge_commit_sha"]
                object["timestamp"] = base["merged_at"]
            elif parsed_data["action"] == "opened":
                object["action"] = "PULL_REQ"
                object["request_id"] = str(base["id"])
                object["author"] = base["user"]["login"]
                object["timestamp"] = base["created_at"]
            if object["action"] == "MERGE_REQ" or object["action"] == "PULL_REQ":
                object["author"] = base["user"]["login"]
                object["from_branch"] = base["head"]["ref"]
                object["to_branch"] = base["base"]["ref"]
                mongo.db.hooks.insert_one(object)
            
        elif request.headers['X-GitHub-Event'] == 'push':
            object["action"] = "PUSH_REQ"
            object["request_id"] = parsed_data["head_commit"]["id"]
            base = parsed_data["repository"]
            object["author"] = base["owner"]["name"]
            object["time_stamp"] = base["updated_at"] 
            ref = parsed_data["ref"].split('/')
            object["to_branch"] = ref[2]
            mongo.db.hooks.insert_one(object)
        print(object)
        return data
@webhook.route('/')
def display_hooks():
    hooks = []
    for h in mongo.db.hooks.find():
        h['_id'] = str(h['_id']) 
        hooks.append(h)
    return jsonify(hooks)
