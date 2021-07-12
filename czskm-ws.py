import asyncio
import simpleobsws
import requests

loop = asyncio.get_event_loop()
ws = simpleobsws.obsws(host='localhost', port=4444, password='', loop=loop)
key = '9be3e8f8-336a-43ee-aeb7-3cc403b97f46'

async def switch_layout():
    await ws.connect()
    old_layout = None
    old_rtmp = None
    while True:
        itemlist = await ws.call('GetSceneItemList')
        itemlist = itemlist['sceneItems']
        current_layout = requests.get('http://localhost:9090/bundles/nodecg-czskm/dashboard/currentlayout.json?key=' + key).text
        rtmp_settings = requests.get('http://localhost:9090/bundles/nodecg-czskm/dashboard/rtmpchange.json?key=' + key).text
        split_settings = rtmp_settings.split('|')
        if current_layout:
            if current_layout != old_layout:
                await asyncio.sleep(0.5)
                for item in itemlist:
                    if item['sourceName'] == current_layout:
                        await ws.call('SetSceneItemRender', data={
                            'scene-name': 'Speedcontrol',
                            'source': item['sourceName'],
                            'render': True
                        })
                        old_layout = current_layout
                        continue
                    if item['sourceName'] not in ['Background', 'Layout']:
                        await ws.call('SetSceneItemRender', data={
                            'scene-name': 'Speedcontrol',
                            'source': item['sourceName'],
                            'render': False
                        })
        if rtmp_settings:
            if rtmp_settings != old_rtmp:
                await ws.call('SetSourceSettings', data={
                    'sourceName': split_settings[0],
                    'sourceSettings': {
                        'input': split_settings[1]
                    }
                })
                old_rtmp = rtmp_settings
        await asyncio.sleep(0.2)

loop.run_until_complete(switch_layout())
