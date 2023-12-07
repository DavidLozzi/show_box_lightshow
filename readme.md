# Show Box Lights and Music

Using an old device that controls my Christmas lights. This has 6 electrical outlets it controls, and can flash them based on music. The device is controlled via [an app](https://apps.apple.com/us/app/show-box/id834313498) that works over local Wifi. As a result, Alexa cannot control this device.

This little project provides an endpoint that I host on my local network on a Raspberry Pi 4 that controls the device. Then I have an Alexa skill that can now control my device!

## What it does

Using Python, it scans your network for UPnP devices, finding one that has `Show_Box` in the name. Once it finds it, it makes the necessary calls to:

- turn it on
- queue up iHeartRadio Christmas Music
- plays the music
- set's the volume
- set's the function to 10 so the lights flash to the music

## Get started

1. Download this repo.
1. Run `pip install -r requirements.txt` to install dependencies
1. Run `uvicorn main:app --reload` to run the server
1. Call `GET http://localhost:8000/all_is_bright` and watch it come alive!

Your terminal will output something similar like:

```sh
Starting up.
Looking for Show Box...
Error ''DstSupported'' for <upnpclient.ssdp.Entry object at 0x10a100070>
Error ''DstSupported'' for <upnpclient.ssdp.Entry object at 0x10a1000d0>
Error ''DstSupported'' for <upnpclient.ssdp.Entry object at 0x109ed9f70>
Found Show_Box_XXXX at http://x.x.x.x:49152/description.xml
Turning box on
Playing music
Setting volume
Changing function to 10
```

Note, the `Error ''DstSupported''` appears to occur for each UPnP on your network, and doesn't signify an actual error.

If you wish to access this endpoint outside of your network, check out [ngrok](https://ngrok.com/).
