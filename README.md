# czskm-websocket
Official Czechoslovak Marathon OBS websocket script for switching layouts and RTMP inputs. Designed to work with [nodecg-czskm](https://github.com/KawaiiWafu/nodecg-czskm), a NodeCG bundle.

## Usage

Needs [czskm-music](https://github.com/WafuRuns/czskm-music) running to function.

```sh
docker build -t czskm-websocket .
docker run -v C:\Path\To\OBSRecordings:/app/data -d --restart unless-stopped czskm-websocket
```
