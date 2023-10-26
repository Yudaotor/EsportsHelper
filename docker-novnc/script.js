//PCM Player : https://github.com/samirkumardas/pcm-player/blob/master/example/server/server.js

window.onload = function () {
    var socketURL = 'ws://' + window.location.hostname + ':56780'
    var player = new PCMPlayer({
        encoding: '16bitInt',
        channels: 2,
        sampleRate: 48000,
        flushingTime: 100
    })

    var ws = new WebSocket(socketURL)
    ws.binaryType = 'arraybuffer'
    ws.addEventListener('message', function (event) {
        var data = new Uint16Array(event.data)
        player.feed(data)
        player.volume(1)
    })
}
