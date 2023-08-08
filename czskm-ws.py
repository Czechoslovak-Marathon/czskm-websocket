import asyncio
import simpleobsws
import requests

parameters = simpleobsws.IdentificationParameters(ignoreNonFatalRequestChecks = False)
ws = simpleobsws.WebSocketClient(
    url='ws://host.docker.internal:4455',
    password='###',
    identification_parameters=parameters
)
key = '###'
ip = '###'
music_url = 'http://host.docker.internal:8000'

async def switch_layout():
    await ws.connect()
    await ws.wait_until_identified()

    old_layout = None
    old_rtmp = None
    old_music = None
    while True:
        itemlist_request = simpleobsws.Request('GetSceneItemList', {'sceneName': 'Speedcontrol'})
        itemlist = await ws.call(itemlist_request)
        if itemlist.ok():
            itemlist = itemlist.responseData['sceneItems']
        request = requests.get(f'https://{ip}/nodecg-czskm/ws', {'key': key}).json()
        current_layout = request['layout']
        rtmp_settings = request['rtmp']
        music = request['music']
        run = request['currentRun']
        recorded = False
        if current_layout:
            current_layout = current_layout.split('.')[0]
            if current_layout != old_layout:
                await asyncio.sleep(0.5)
                for item in itemlist:
                    if item['sourceName'] == current_layout:
                        request = simpleobsws.Request('SetSceneItemEnabled', {
                            'sceneName': 'Speedcontrol',
                            'sceneItemId': item['sceneItemId'],
                            'sceneItemEnabled': True
                        })
                        await ws.call(request)
                        continue
                    if item['sourceName'] == 'Snow' and current_layout in ['continue', 'end', 'start', 'intermission']:
                        request = simpleobsws.Request('SetSceneItemEnabled', {
                            'sceneName': 'Speedcontrol',
                            'sceneItemId': item['sceneItemId'],
                            'sceneItemEnabled': True
                        })
                        await ws.call(request)
                        continue
                    if item['sourceName'] not in ['Background', 'Graphics', 'Donationtotal', 'Donation', 'Music']:
                        request = simpleobsws.Request('SetSceneItemEnabled', {
                            'sceneName': 'Speedcontrol',
                            'sceneItemId': item['sceneItemId'],
                            'sceneItemEnabled': False
                        })
                        await ws.call(request)
                if current_layout not in ['continue', 'end', 'start', 'intermission']:
                    request = simpleobsws.Request('StartRecord')
                else:
                    request = simpleobsws.Request('StopRecord')
                    requests.get(music_url)
                    recorded = True
                if not recorded:
                    await ws.call(request)
                else:
                    output = await ws.call(request)
                    recorded = False
                    if output.responseData:
                        path = output.responseData["outputPath"].split('/')[-1]
                        with open('/app/data/runs.txt', 'a') as file:
                            run = run.replace('|', '｜')
                            file.write(f'{path}|Czechoslovak Marathon Winter 2023 ｜ {run}\n')
                old_layout = current_layout
        if rtmp_settings:
            if rtmp_settings != old_rtmp:
                rtmp_request = simpleobsws.Request('GetInputList')
                inputs = await ws.call(rtmp_request)
                if inputs.ok():
                    inputs = inputs.responseData['inputs']
                split_settings = rtmp_settings.split('|')
                for input in inputs:
                    if input['inputName'] == split_settings[0]:
                        settings_request = simpleobsws.Request('SetInputSettings', {
                            'inputName': input['inputName'],
                            'inputSettings': {'input': split_settings[1]}
                        })
                        await ws.call(settings_request)
                old_rtmp = rtmp_settings
        if music:
            if music != old_music:
                requests.get(music_url)
                old_music = music
        await asyncio.sleep(0.2)

loop = asyncio.get_event_loop()
loop.run_until_complete(switch_layout())
