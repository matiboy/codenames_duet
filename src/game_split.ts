import Vue from 'vue'
import {chunk, throttle, range, difference} from 'lodash'
import { DefaultDeviceController, MeetingSessionConfiguration, DefaultMeetingSession, AudioVideoController, AudioVideoFacade, DeviceChangeObserver, AudioVideoObserver, VideoTileState, ConsoleLogger, LogLevel, TimeoutScheduler, MeetingSessionStatus } from 'amazon-chime-sdk-js';
import { logger, QualityMappings } from './chime';
import { login } from './api'
import { TestSound } from './chime/test-sound'
// import Pusher from 'pusher-js' // Broken import :/ using window for now
import 'pusher-js'
import { Game, Attendee } from './game.interface';
import Key from './key.vue'
import { setAuthTokens } from 'axios-jwt';

let meetingSession: DefaultMeetingSession
let audioVideo: AudioVideoFacade
let selectedVideoDevice: string
let selectedAudioOutput: string
const anotherLogger = new ConsoleLogger('CoVIDenames', LogLevel.INFO)
interface UpdateMessage {
  message: string
}
interface HintMessage {
  word: string
  count: number
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

const fromWindowBuilder = <T>(key: string) => () => ((window as any)[key]) as T

const getVideoPreviewElement = (): HTMLVideoElement => {
  return document.getElementById('video-preview') as HTMLVideoElement
}
const getAudioOutputElement = (): HTMLAudioElement => {
  return document.getElementById('meeting-audio') as HTMLAudioElement
}

const getAttendee = fromWindowBuilder<Attendee>('ATTENDEE')
const getUrls = fromWindowBuilder<{[key: string]: string}>('URLS')

const getGame = fromWindowBuilder<Game>('GAME')

const getPlayerNumber = fromWindowBuilder<number>('playerNumber')

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
    
    const videoElement = document.getElementById(`video-${index}`) as HTMLVideoElement;
    audioVideo.bindVideoElement(tileState.tileId, videoElement);
  }
  
  audioVideoDidStop(status: MeetingSessionStatus) {
    anotherLogger.info(`Audio video has stopped, ${status.statusCode}`)
    new TimeoutScheduler(1000).start(() => {
      anotherLogger.info('Attempting restart')
      audioVideo.stop()
      audioVideo.start()
    })
  }

  videoTileWasRemoved() {
    anotherLogger.info('Some video tile was removed but which??')
  }
}

const theGreatObserver = new VueAudioVideoObserver()
let pusher: any

export default {
    components: {
      key: Key
    },
    data: {
      game: (window as any).GAME,
      key: (window as any).KEY,
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'white',
      rulesDialog: false,
      hintDialog: false,
      contactDialog: false,
      playerCantHintDialog: false,
      buyMeDialog: false,
      giveHint: {
        text: '',
        count: 2
      },
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
      localPaused: false,
      otherMuted: false,
      localMuted: false,
      agents: range(0, 15),
      hint: {},
      preview: true
    },
    async mounted() {
      const urlParams = new URLSearchParams(window.location.search)
      const token = urlParams.get('token')
      // Log in
      login(token).then(tokens => setAuthTokens(tokens))
      // Pusher stuff
      pusher = new (window as any).Pusher((window as any).PUSHER_KEY, {
        cluster: (window as any).PUSHER_CLUSTER,
      });
      const channel = pusher.subscribe(getUrls().player_channel)
      // const gameChannel = pusher.subscribe(getUrls().game_channel)
      channel.bind('game_update', (data: UpdateMessage) => {
        this.refreshGame()
        this.showSnackbar(data.message)
      });
      channel.bind('key_update', (data: UpdateMessage) => {
        anotherLogger.info('Key has being updated')
        this.refreshKey()
      });
      channel.bind('new_hint', (data: HintMessage) => {
        anotherLogger.info(`New hint! ${data}`)
        this.hint = data
      });
      // Chime stuff
      const deviceController = new DefaultDeviceController(logger);
      (window as any).dc = deviceController
      const configuration = new MeetingSessionConfiguration((window as any).MEETING, (window as any).ATTENDEE);
      meetingSession = new DefaultMeetingSession(configuration, logger, deviceController)
      audioVideo = meetingSession.audioVideo;
      (window as any).av = audioVideo;
      (window as any).sess = meetingSession;
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
      inVideo() {
        return !(['flow-load-devices', 'flow-devices'].includes(this.videoStep))
      },
      suddenDeath() {
        return this.game.sudden_death
      },
      lost() {
        return Boolean(this.game.lost)
      },
      foundAgents() {
        return range(0, this.game.found.length)
      },
      unfoundAgents() {
        return range(0, this.game.agents - this.game.found.length)
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
        } else if(this.playerIsGuesser) {
          return 'guess'
        } else {
          return 'hint'
        }
      },
      playerGameStatus() {
        return this.game[`player${getPlayerNumber()}`]
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
      playerIsGuesser() {
        return this.next_up === getPlayerNumber()
      },
      playerIsHinter() {
        return !this.playerIsGuesser
      },
      playerCantHint() {
        return this.playerIsHinter && (difference(this.key.green, this.game.found).length === 0)
      },
      bystanders() {
        return [
          'mgonto', 'koridhandy', 'marklamb', '_shahedk', 'RussellBishop', 'shanehudson', 'travis_arnold', 'kushsolitary', 'jeremyshimko', 'atariboy', 'nasirwd', 'danmartin70' 
        ].slice(0, this.game.initialBystanders)
        .map(i => `https://s3.amazonaws.com/uifaces/faces/twitter/${i}/128.jpg`)
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
      async confirmSkip() {
        this.playerCantHintDialog = false
        const {result, game} = await post(`${getUrls().skip}`, {})
        this.game = game
      },
      async confirmHint() {
        this.hintDialog = false
        const {result, game} = await fetch(`${getUrls().hint}?word=${this.giveHint.text}&count=${this.giveHint.count}`)
        .then(x => x.json())
        this.giveHint = {text: '', count: 2}
        this.game = game
      },
      refreshGame() {
        fetch(getUrls().game, {
          headers: {
            'Content-Type': 'application/json'
          }
        }).then(x => x.json())
        .then(x => {
          this.game = x.game
          if(this.playerCantHint) {
            this.playerCantHintDialog = true
          }
        })
      },
      refreshKey() {
        fetch(getUrls().key, {
          headers: {
            'Content-Type': 'application/json'
          }
        }).then(x => x.json())
        .then(x => this.key = x)
      },
      toggleVideoSelf() {
        if(this.localPaused) {
          audioVideo.startLocalVideoTile()
        } else {
          audioVideo.stopLocalVideoTile()
        }
        this.localPaused = !this.localPaused
      },
      toggleAudioSelf() {
        if(this.localMuted) {
          audioVideo.realtimeUnmuteLocalAudio()
        } else {
          audioVideo.realtimeMuteLocalAudio()
        }
        this.localMuted = !this.localMuted
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
        if(this.preview) {
          audioVideo.startVideoPreviewForVideoInput(getVideoPreviewElement())
        }
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
          if(!present) {
            audioVideo.realtimeUnsubscribeFromVolumeIndicator(attendeeId)
          } else {
            if(attendeeId === getAttendee().AttendeeId) {
              // TODO register for sound etc
            } else {
              audioVideo.realtimeSubscribeToVolumeIndicator(attendeeId, this.onVolumeIndicator.bind(this))
            }
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
      async showSnackbar(text: string) {
        if(!text) {
          return
        }
        // Make sure snackbar was gone first
        this.snackbar = false
        await this.$nextTick()
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
        if(this.isFound(word) || this.playerAttempted(word)) {
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
        this.game = game
        if([1, 4].includes(result)) {
          // The lost/win status is in the game already now
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
        }
        return result
      },
      playerAttempted(word: string) {
        if(this.game.found.includes(word)) { return false }
        return this.playerGameStatus.attempted_words.includes(word)
      },
      onVolumeIndicator(attendeeId: string, volume: number, muted: boolean, signalStrength: number, externalUserId?: string) {
        anotherLogger.info(`Attendee ${attendeeId} s volume is set to ${volume} and muted is ${muted}`)
        anotherLogger.debug(() => `This attendee is ${getAttendee().AttendeeId}`)
        if(attendeeId !== getAttendee().AttendeeId) {
          this.otherMuted = muted
        }
      }
    }
  }