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


@app.get("/all_is_bright")
@app.post("/all_is_bright")
def all_is_bright():
    print(f"Starting up. {time.strftime('%Y-%m-%d %H:%M:%S')}")

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

    print("Turning box on")
    send_command_to_box("FFAA MODE START BB", ip)

    # av_transport = show_box.services[0]
    # connection_mgr = show_box.services[1]
    rendering_ctrl = show_box.services[2]
    play_queue = show_box.services[3]

    queue = '<?xml version="1.0"?><PlayList><ListName>iHeartRadio</ListName><ListInfo><Radio>1</Radio><SourceName>iHeartRadio</SourceName><PicUrl></PicUrl><TrackNumber>1</TrackNumber><SearchUrl></SearchUrl><Quality>0</Quality></ListInfo><Tracks><Track1><URL>http://stream.revma.ihrhls.com/zc4596</URL><Source>iHeartRadio</Source><Key></Key><Id></Id><Metadata>&amp;lt;?xml version=&amp;quot;1.0&amp;quot; encoding=&amp;quot;UTF-8&amp;quot;?&amp;gt;&amp;lt;DIDL-Lite xmlns:dc=&amp;quot;http://purl.org/dc/elements/1.1/&amp;quot; xmlns:upnp=&amp;quot;urn:schemas-upnp-org:metadata-1-0/upnp/&amp;quot; xmlns:song=&amp;quot;www.wiimu.com/song/&amp;quot; xmlns:custom=&amp;quot;www.wiimu.com/custom/&amp;quot; xmlns=&amp;quot;urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/&amp;quot;&amp;gt;&amp;lt;upnp:class&amp;gt;object.item.audioItem.musicTrack&amp;lt;/upnp:class&amp;gt;&amp;lt;item&amp;gt;&amp;lt;song:id&amp;gt;&amp;lt;/song:id&amp;gt;&amp;lt;song:albumid&amp;gt;&amp;lt;/song:albumid&amp;gt;&amp;lt;song:singerid&amp;gt;&amp;lt;/song:singerid&amp;gt;&amp;lt;dc:title&amp;gt;iHeart Christmas&amp;lt;/dc:title&amp;gt;&amp;lt;upnp:artist&amp;gt;iHeartRadio&amp;lt;/upnp:artist&amp;gt;&amp;lt;upnp:album&amp;gt;iHeartRadio&amp;lt;/upnp:album&amp;gt;&amp;lt;res&amp;gt;http://stream.revma.ihrhls.com/zc4596&amp;lt;/res&amp;gt;&amp;lt;upnp:albumArtURI&amp;gt;https://i.iheart.com/v3/re/new_assets/b85767b2-d530-468e-8979-d0aa0319b7c8&amp;lt;/upnp:albumArtURI&amp;gt;&amp;lt;/item&amp;gt;&amp;lt;/DIDL-Lite&amp;gt;</Metadata></Track1></Tracks></PlayList>'

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
                "text": "The magic is on!",
                "playBehavior": "REPLACE_ENQUEUED",
            },
            "shouldEndSession": True,
        },
    }
