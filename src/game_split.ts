import Vue from 'vue'
import {chunk, throttle} from 'lodash'
import { DefaultDeviceController, MeetingSessionConfiguration, DefaultMeetingSession, AudioVideoController, AudioVideoFacade, DeviceChangeObserver, AudioVideoObserver, VideoTileState, ConsoleLogger, LogLevel } from 'amazon-chime-sdk-js';
import { logger, QualityMappings } from './chime';
import { TestSound } from './chime/test-sound'
// import Pusher from 'pusher-js' // Broken import :/ using window for now
import 'pusher-js'
import { Game, Attendee } from './game.interface';

let meetingSession: DefaultMeetingSession
let audioVideo: AudioVideoFacade
let selectedVideoDevice: string
let selectedAudioOutput: string
const anotherLogger = new ConsoleLogger('JOHN', LogLevel.INFO)
interface UpdateMessage {
  updater: number
}
interface ApiResponse {
  result: number, 
  game: Game
}

class VueDeviceChangeObserver implements DeviceChangeObserver {
  vm: Vue
  constructor(vm: Vue) {
    this.vm = vm
  }
  videoInputsChanged() {
    console.log("RIIIIIGGGGT", arguments)
  }
  audioInputsChanged() {
    console.log('BLALA', arguments)
  }
  audioOutputsChanged() {
    console.log(arguments)
  }
}

export const enum Flows {
  LOAD_DEVICES = 'flow-load-devices',
  CHOOSE_DEVICES = 'flow-devices',
  IN_MEETING = 'flow-in-meeting'
}

const getVideoPreviewElement = (): HTMLVideoElement => {
  return document.getElementById('video-preview') as HTMLVideoElement
}
const getAudioOutputElement = (): HTMLAudioElement => {
  return document.getElementById('meeting-audio') as HTMLAudioElement
}

const getAttendee = (): Attendee => {
  return (window as any).ATTENDEE
}

const getGame = (): Game => {
  return (window as any).GAME
}

const getPlayerNumber = () => {
  return (window as any).playerNumber
}

const logMe = function(whatever) {
  console.log(whatever)
}
const throttledLogMe = throttle(logMe, 500)

const post: (url: string, data: {[key: string]: any}) => Promise<ApiResponse> = (window as any).post

let localTileId: number

class VueAudioVideoObserver implements AudioVideoObserver {
  videoTileDidUpdate(tileState: VideoTileState) {
    anotherLogger.info('Tile status ' + JSON.stringify(tileState))
    let index = 16
    if(tileState.localTile) {
      index = 0
      localTileId = tileState.tileId
    }
    anotherLogger.info('Index ' + JSON.stringify(index))
    
    const tileElement = document.getElementById(`tile-${index}`) as HTMLDivElement;
    anotherLogger.info('tileElement' + tileElement)
    const videoElement = document.getElementById(`video-${index}`) as HTMLVideoElement;
    anotherLogger.info('videoElement' + videoElement)
    console.log(`binding video element`, tileState, videoElement)
    audioVideo.bindVideoElement(tileState.tileId, videoElement);
    // throttledLogMe(arguments)
  }
}

const theGreatObserver = new VueAudioVideoObserver()
let pusher: any

export default {
    data: {
      game: (window as any).GAME,
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'white',
      loading: false,
      firstPlayer: null,
      selectedAudioInput: null,
      selectedVideoInput: null,
      selectedVideoQuality: null,
      selectedAudioOutput: null,
      audioInputDevices: [],
      audioOutputDevices: [],
      videoInputDevices: [],
      videoStep: Flows.LOAD_DEVICES,
      localPaused: false
    },
    async mounted() {
      // Pusher stuff
      pusher = new (window as any).Pusher((window as any).PUSHER_KEY, {
        cluster: (window as any).PUSHER_CLUSTER,
      });
      const channel = pusher.subscribe((window as any).channel)
      channel.bind('game_update', (data: UpdateMessage) => {
        console.log(data, getPlayerNumber(), data.updater !== getPlayerNumber())
        if(data.updater !== getPlayerNumber()) {
          this.refreshGame()
        }
      });
      // Chime stuff
      const deviceController = new DefaultDeviceController(logger)
      const configuration = new MeetingSessionConfiguration((window as any).MEETING, (window as any).ATTENDEE);
      meetingSession = new DefaultMeetingSession(configuration, logger, deviceController)
      audioVideo = meetingSession.audioVideo
      const deviceChangeObserver = new VueDeviceChangeObserver(this)
      audioVideo.addDeviceChangeObserver(deviceChangeObserver)
      // Let's load devices
      const audioInputPromise = audioVideo.listAudioInputDevices().then(devices => {
        this.audioInputDevices = devices.map(({label, deviceId}) => ({
          text: label,
          value: deviceId
        }))
      })
      const audioOutputPromise = audioVideo.listAudioOutputDevices().then(devices => {
        this.audioOutputDevices = devices.map(({label, deviceId}) => ({
          text: label,
          value: deviceId
        }))
      })
      const videoInputPromise = audioVideo.listVideoInputDevices().then(devices => {
        this.videoInputDevices = devices.map(({label, deviceId}) => ({
          text: label,
          value: deviceId
        }))
      })
      await Promise.all([videoInputPromise, audioInputPromise, audioOutputPromise])
      this.videoStep = Flows.CHOOSE_DEVICES
      await this.$nextTick()
      // Choose first items as defaults
      this.selectedVideoQuality = this.qualityOptions[0].value
      this.selectedAudioInput = this.audioInputDevices[0].value
      this.selectedVideoInput = this.videoInputDevices[0].value
      if(this.audioOutputDevices.length) {
        this.selectedAudioOutput = this.audioOutputDevices[0].value
      }
      // Trigger changes
      this.selectAudioInput(this.selectedAudioInput)
      this.selectVideoInput(this.selectedVideoInput)
      this.selectVideoQuality(this.selectedVideoQuality)
      this.selectAudioOutput(this.selectedAudioOutput)
    },
    computed: {
      lost() {
        return Boolean(this.game.lost)
      },
      won() {
        return Boolean(this.game.won)
      },
      qualityOptions() {
        return [
          {value: "360p", text: "360p (nHD) @ 15 fps (600 Kbps max)"},
          {value: "540p", text: "540p (qHD) @ 15 fps (1.4 Mbps max)"},
          {value: "720p", text: "720p (HD) @ 15 fps (1.4 Mbps max)"},
        ]
      },
      iAmGuessing() {
        return this.playerStatus === 'guess'
      },
      playerStatus() {
        if(!this.game.next_up) {
          return 'open'
        } else if(this.game.next_up === getPlayerNumber()) {
          return 'guess'
        } else {
          return 'hint'
        }
      },
      playerStatusText() {
        if (this.playerStatus === 'guess') {return 'guessing'}
        if (this.playerStatus === 'hint') {return 'giving hint'}
      },
      nextPlayer() {
        if(this.game.next_up) {
          return this.game[`player${this.game.next_up}`]
        }
        return {}
      },
      rows() {
        return chunk(this.game.words, 5)
      },
      noPlayer() {
        return this.game.next_up === null
      },
      next_up() {
        console.log(this.game.next_up)
        return this.game.next_up
      },
      player() {
        return this.next_up
      },
      player1() {
        return this.next_up === 1
      },
      player2() {
        return this.next_up === 2
      },
      bystanders() {
        return [
        1005, 1011, 1012, 1025, 129, 177, 22, 281, 338, 395
        ].slice(0, this.game.initialBystanders)
        .map(i => `https://i.picsum.photos/id/${i}/60/60.jpg`)
      },
      ended() {
        return (this.lost || this.won)
      },
      overlayColor() {
        return this.lost ? 'error' : this.won ? 'success' : null
      }
    },
    methods: {
      async startNew() {
        await post(`/game/${getGame().id}/new`, {})
        this.refreshGame()
      },
      refreshGame() {
        fetch(window.location.toString(), {
          headers: {
            'Content-Type': 'application/json'
          }
        }).then(x => x.json())
        .then(x => this.game = x.game)
      },
      toggleVideoSelf() {
        if(this.localPaused) {
          audioVideo.unpauseVideoTile(localTileId)
        } else {
          audioVideo.pauseVideoTile(localTileId)
        }
        this.localPaused = !this.localPaused
      },
      selectAudioInput(deviceId: string) {
        audioVideo.chooseAudioInputDevice(deviceId)
      },
      async selectAudioOutput(deviceId: string) {
        await audioVideo.chooseAudioOutputDevice(deviceId)
        selectedAudioOutput = deviceId
        const audioMix = getAudioOutputElement();
        audioVideo.bindAudioElement(audioMix);
      },
      async selectVideoInput(deviceId: string) {
        selectedVideoDevice = deviceId
        await audioVideo.chooseVideoInputDevice(deviceId)
        audioVideo.startVideoPreviewForVideoInput(getVideoPreviewElement())
      },
      async selectVideoQuality(value: string) {
        const quality: [number, number, number, number] = QualityMappings[value]
        audioVideo.chooseVideoInputQuality(...quality)
        if(selectedVideoDevice) {
          await audioVideo.chooseVideoInputDevice(selectedVideoDevice)
        }
      },
      testSpeaker() {
        if(selectedAudioOutput) {
          new TestSound(selectedAudioOutput);
        }
      },
      async join() {
        audioVideo.stopVideoPreviewForVideoInput(getVideoPreviewElement())
        await audioVideo.chooseVideoInputDevice(selectedVideoDevice)
        this.videoStep = Flows.IN_MEETING
        audioVideo.addObserver(theGreatObserver)
        audioVideo.start()
        audioVideo.startLocalVideoTile()
        audioVideo.realtimeSubscribeToAttendeeIdPresence((attendeeId, present, externalUserId) => {
          if(attendeeId === getAttendee().AttendeeId) {
            // TODO register for sound etc
          }
        })
      },
      selectFirstPlayer(v: number) {
        this.firstPlayer = v + 1
      },
      snackChange(v: boolean) {
        this.snackbar = v
      },
      isFound(word: string) {
        return this.game.found.includes(word)
      },
      showSnackbar(text) {
        this.snackbar = true
        this.snackbarText = text
      },
      async stopGuessing() {
        await this.serverAction(`/stop/${this.game.id}/${getAttendee().ExternalUserId}`, {
          player: this.player
        })
      },
      async pointed(word: string) {
        if(this.game.next_up !== null && this.game.next_up !== getPlayerNumber()) {
          return
        }
        if(this.isFound(word) || (this.player1 && this.player1Attempted(word)) || (this.player2 && this.player2Attempted(word))) {
          return
        }
        const result = await this.serverAction(`/guess/${this.game.id}/${getAttendee().ExternalUserId}`, {
          word,
          player: this.player || this.firstPlayer
        })
      },
      async serverAction(url: string, data: any) {
        this.loading = true
        const {result, game} = await post(url, data)
        if([1, 4].includes(result)) {
        } else {
          if(result === 6) {
            this.showSnackbar('🙄')
          } else {
            let message = ''
            switch(result) {
              case 3:
                message = 'Nope'
                break;
              case 2:
                message = 'Well done'
                break;
              case 8:
                message = 'Ok, moving on then'
                break;
            }
            this.showSnackbar(message)
          }
          this.game = game
        }
        return result
      },
      player1Attempted(word) {
        if(this.game.found.includes(word)) { return false }
        return this.game.player1.attempted_words.includes(word)
      },
      player2Attempted(word) {
        if(this.game.found.includes(word)) { return false }
        return this.game.player2.attempted_words.includes(word)
      }
    }
  }