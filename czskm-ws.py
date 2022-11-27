import asyncio
import simpleobsws
import requests

loop = asyncio.get_event_loop()
ws = simpleobsws.obsws(host='host.docker.internal', port=4444, password='', loop=loop)
key = ''
ip = ''

async def switch_layout():
    await ws.connect()
    old_layout = None
    old_rtmp = None
    while True:
        itemlist = await ws.call('GetSceneItemList')
        itemlist = itemlist['sceneItems']
        request = requests.get(f'http://{ip}/nodecg-czskm/ws', {'key': key}).json()
        current_layout = request['layout']
        rtmp_settings = request['rtmp']
        if current_layout:
            current_layout = current_layout.split('.')[0]
            if current_layout != old_layout:
                await asyncio.sleep(0.5)
                for item in itemlist:
                    if item['sourceName'] == current_layout:
                        await ws.call('SetSceneItemRender', data={
                            'scene-name': 'Speedcontrol',
                            'source': item['sourceName'],
                            'render': True
                        })
                        continue
                    if item['sourceName'] not in ['Background', 'Layout', 'Donationtotal']:
                        await ws.call('SetSceneItemRender', data={
                            'scene-name': 'Speedcontrol',
                            'source': item['sourceName'],
                            'render': False
                        })
                old_layout = current_layout
        if rtmp_settings:
            if rtmp_settings != old_rtmp:
                split_settings = rtmp_settings.split('|')
                await ws.call('SetSourceSettings', data={
                    'sourceName': split_settings[0],
                    'sourceSettings': {
                        'input': split_settings[1]
                    }
                })
                old_rtmp = rtmp_settings
        await asyncio.sleep(0.2)

loop.run_until_complete(switch_layout())
