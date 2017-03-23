import json
import urllib
from slackclient import SlackClient


class PinguSlack(object):
    def __init__(self, token="", username="pingubot"):
        self.slack_client = SlackClient(token)
        self.slack_client.api_call("api.test")
        self.username = username

    def list_channels(self):
        channels_call = self.slack_client.api_call("channels.list")
        if channels_call.get('ok'):
            return channels_call['channels']
        return None


    def send_weekly_challenge(self, username, opponent):
        print(slack_client.api_call(
            "chat.postMessage",
            channel='@'+username,
            text='This week, you shall face the following opponent: ' + '@' + opponent + " Good luck!",
            link_names=opponent,
            username='Boten Anna',
            icon_emoji=':information_desk_person:'
        ))
    def send_message(channel_id, message):
        rsp = slack_client.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=message,
            username=self.username,
            icon_emoji=':robot_face:'
        )


        for pinned in slack_client.api_call("pins.list", channel=rsp['channel'])['items']:
            slack_client.api_call(
                "pins.remove",
                channel=rsp['channel'],
                timestamp=pinned['message']['ts']
            )


        print(slack_client.api_call(
            "pins.add",
            timestamp=rsp['ts'],
            channel=rsp['channel'],
        ))
