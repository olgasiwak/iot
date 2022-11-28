import paho.mqtt.client as mqtt
import json

# Mqtt Dynamic Security guides
# https://mosquitto.org/documentation/dynamic-security/
# https://github.com/eclipse/mosquitto/blob/master/plugins/dynamic-security/README.md#list-clients

class AdminClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.adminTopic = "$CONTROL/dynamic-security/v1"

    def createRole(self, roleName, topicsToSend, topicsToSubscribe):
        message = {
            "commands": [
                {
                    "command": "createRole",
                    "rolename": roleName,
                    "acls":
                        [{"acltype": "publishClientSend", "topic": topicToSend, "allow": True}
                         for topicToSend in topicsToSend] +
                        [{"acltype": "subscribeLiteral", "topic": topicToSubscribe, "allow": True}
                         for topicToSubscribe in topicsToSubscribe]
                }
            ]
        }
        self.client.publish(self.adminTopic, json.dumps(message))

    def createClient(self, clientName, clientPassword, roleName):
        message = {
            "commands": [
                {
                    "command": "createClient",
                    "username": clientName,
                    "password": clientPassword,
                    "roles": [
                        {"rolename": roleName, "priority": -1}
                    ]
                }
            ]
        }
        self.client.publish(self.adminTopic, json.dumps(message))


if __name__ == '__main__':
    adminClient = AdminClient()
    adminClient.client.username_pw_set("adminLogin", "adminPass")
    adminClient.client.connect("localhost", 1883)

    adminClient.createRole(
        roleName="RoleName",
        topicsToSend=["topicToSend1", "topicToSend2", "topicToSend3"],
        topicsToSubscribe=["topicToSub1", "topicToSub2", "topicToSub3"]
    )

    adminClient.createClient(
        clientName="ClientName",
        clientPassword="ClientPassword",
        roleName="RoleName"
    )
