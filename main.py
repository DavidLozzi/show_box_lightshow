import socket
import upnpclient
import time
from fastapi import FastAPI

app = FastAPI()


def send_command_to_box(command, ip):
    try:
        command_bytes = bytes.fromhex(command.encode("utf-8").hex())
        port = 959
        timeout = 1
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((ip, port))
            sock.sendall(command_bytes)
            # Wait for a response and return it
            return sock.recv(1024)
    except socket.timeout:
        return b"Connection timed out."
    except Exception as e:
        return str(e).encode()


@app.post("/all_is_bright")
def all_is_bright(payload: dict):
    print(f"Starting up. {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(payload["request"])
    amount = 0
    volume = 0
    intent = ""
    return_message = "The magic is on!"
    if payload["request"]["type"] == "IntentRequest":
        intent = payload["request"]["intent"]["name"]
        if "slots" in payload["request"]["intent"]:
            if "value" in payload["request"]["intent"]["slots"]["amount"]:
                print(
                    f"Amount: {payload['request']['intent']['slots']['amount']['value']}"
                )
                amount = int(payload["request"]["intent"]["slots"]["amount"]["value"])
            if "value" in payload["request"]["intent"]["slots"]["volume"]:
                print(
                    f"Volume: {payload['request']['intent']['slots']['volume']['value']}"
                )
                volume = int(payload["request"]["intent"]["slots"]["volume"]["value"])
    elif payload["request"]["type"] == "SessionEndedRequest":
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Goodbye",
                    "playBehavior": "REPLACE_ENQUEUED",
                },
                "shouldEndSession": True,
            },
        }

    cnt = 0
    show_box = None
    while True:
        print("Looking for Show Box...")
        cnt += 1
        devices = upnpclient.discover()
        for device in devices:
            if "Show_Box" in device.friendly_name:
                show_box = device

        if cnt > 10 or show_box is not None:
            break

    print(f"Found {show_box.friendly_name} at {show_box.location}")

    ip = show_box.location.split("//")[1].split(":")[0]

    av_transport = show_box.services[0]
    # connection_mgr = show_box.services[1]
    rendering_ctrl = show_box.services[2]
    play_queue = show_box.services[3]

    queue = '<?xml version="1.0"?><PlayList><ListName>iHeartRadio</ListName><ListInfo><Radio>1</Radio><SourceName>iHeartRadio</SourceName><PicUrl></PicUrl><TrackNumber>1</TrackNumber><SearchUrl></SearchUrl><Quality>0</Quality></ListInfo><Tracks><Track1><URL>http://stream.revma.ihrhls.com/zc4596</URL><Source>iHeartRadio</Source><Key></Key><Id></Id><Metadata>&amp;lt;?xml version=&amp;quot;1.0&amp;quot; encoding=&amp;quot;UTF-8&amp;quot;?&amp;gt;&amp;lt;DIDL-Lite xmlns:dc=&amp;quot;http://purl.org/dc/elements/1.1/&amp;quot; xmlns:upnp=&amp;quot;urn:schemas-upnp-org:metadata-1-0/upnp/&amp;quot; xmlns:song=&amp;quot;www.wiimu.com/song/&amp;quot; xmlns:custom=&amp;quot;www.wiimu.com/custom/&amp;quot; xmlns=&amp;quot;urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/&amp;quot;&amp;gt;&amp;lt;upnp:class&amp;gt;object.item.audioItem.musicTrack&amp;lt;/upnp:class&amp;gt;&amp;lt;item&amp;gt;&amp;lt;song:id&amp;gt;&amp;lt;/song:id&amp;gt;&amp;lt;song:albumid&amp;gt;&amp;lt;/song:albumid&amp;gt;&amp;lt;song:singerid&amp;gt;&amp;lt;/song:singerid&amp;gt;&amp;lt;dc:title&amp;gt;iHeart Christmas&amp;lt;/dc:title&amp;gt;&amp;lt;upnp:artist&amp;gt;iHeartRadio&amp;lt;/upnp:artist&amp;gt;&amp;lt;upnp:album&amp;gt;iHeartRadio&amp;lt;/upnp:album&amp;gt;&amp;lt;res&amp;gt;http://stream.revma.ihrhls.com/zc4596&amp;lt;/res&amp;gt;&amp;lt;upnp:albumArtURI&amp;gt;https://i.iheart.com/v3/re/new_assets/b85767b2-d530-468e-8979-d0aa0319b7c8&amp;lt;/upnp:albumArtURI&amp;gt;&amp;lt;/item&amp;gt;&amp;lt;/DIDL-Lite&amp;gt;</Metadata></Track1></Tracks></PlayList>'

    try:
        if intent == "LowerVolumeIntent":
            print("Getting volume")
            current_volume = rendering_ctrl.GetVolume(InstanceID=0, Channel="Master")
            print(f"Current vol: {current_volume['CurrentVolume']}")
            new_volume = 0
            if volume > 0 and amount == 0:
                new_volume = volume
            elif volume == 0 and amount > 0:
                new_volume = current_volume["CurrentVolume"] - amount

            print(f"Setting volume to {new_volume}")
            rendering_ctrl.SetVolume(
                InstanceID=0,
                Channel="Master",
                DesiredVolume=new_volume,
            )
            return_message = f"Volume set to {new_volume}"
        elif intent == "PauseMusic":
            av_transport.Pause(InstanceID=0)
            print("Paused music")
            return_message = "Music paused"
        elif intent == "PlayMusic":
            play_queue.CreateQueue(QueueContext=queue)
            play_queue.PlayQueueWithIndex(QueueName="iHeartRadio", Index=1)
            print("Play music")
            return_message = "Playing music"
        else:
            print("Turning box on")
            send_command_to_box("FFAA MODE START BB", ip)

            print("Playing music")
            play_queue.CreateQueue(QueueContext=queue)
            play_queue.PlayQueueWithIndex(QueueName="iHeartRadio", Index=1)

            print("Setting volume")
            rendering_ctrl.SetVolume(InstanceID=0, Channel="Master", DesiredVolume=70)

            print("Changing function to 10")
            send_command_to_box("FFAA MODE CHOICE 10 BB", ip)

            print("All done, merry christmas!")

        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": return_message,
                    "playBehavior": "REPLACE_ENQUEUED",
                },
                "shouldEndSession": True,
            },
        }
    except Exception as e:
        print(e)
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "He's a south pole elf.",
                    "playBehavior": "REPLACE_ENQUEUED",
                },
                "shouldEndSession": True,
            },
        }
