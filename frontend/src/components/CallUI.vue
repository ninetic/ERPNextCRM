<template>
  <div
    v-show="showCallPopup"
    ref="callPopup"
    class="fixed select-none z-10 bg-gray-900 text-gray-300 rounded-lg shadow-2xl p-4 flex flex-col w-60 cursor-move"
    :style="style"
  >
    <div class="flex items-center flex-row-reverse gap-1">
      <MinimizeIcon class="w-4 h-4 cursor-pointer" @click="toggleCallWindow" />
    </div>
    <div class="flex flex-col justify-center items-center gap-3">
      <Avatar
        :image="contact.image"
        :label="contact.full_name"
        class="flex items-center justify-center [&>div]:text-[30px] !h-24 !w-24 relative"
        :class="onCall || calling ? '' : 'pulse'"
      />
      <div class="flex flex-col items-center justify-center gap-1">
        <div class="text-xl font-medium">
          {{ contact.full_name }}
        </div>
        <div class="text-sm text-gray-600">{{ contact.mobile_no }}</div>
      </div>
      <CountUpTimer ref="counterUp">
        <div v-if="onCall" class="text-base my-1">
          {{ counterUp?.updatedTime }}
        </div>
      </CountUpTimer>
      <div v-if="!onCall" class="text-base my-1">
        {{
          callStatus == 'ringing'
            ? 'Ringing...'
            : calling
            ? 'Calling...'
            : 'Incoming call...'
        }}
      </div>
      <div v-if="onCall" class="flex gap-2">
        <Button
          :icon="muted ? 'mic-off' : 'mic'"
          class="rounded-full"
          @click="toggleMute"
        />
        <Button class="rounded-full">
          <template #icon>
            <DialpadIcon class="rounded-full cursor-pointer" />
          </template>
        </Button>
        <Button class="rounded-full">
          <template #icon>
            <NoteIcon
              class="text-gray-900 rounded-full cursor-pointer h-4 w-4"
              @click="showNoteModal = true"
            />
          </template>
        </Button>
        <Button class="rounded-full bg-red-600 hover:bg-red-700">
          <template #icon>
            <PhoneIcon
              class="text-white fill-white h-4 w-4 rotate-[135deg]"
              @click="hangUpCall"
            />
          </template>
        </Button>
      </div>
      <div v-else-if="calling">
        <Button
          size="md"
          variant="solid"
          theme="red"
          label="Cancel"
          @click="cancelCall"
          class="rounded-lg"
        >
          <template #prefix>
            <PhoneIcon class="fill-white h-4 w-4 rotate-[135deg]" />
          </template>
        </Button>
      </div>
      <div v-else class="flex gap-2">
        <Button
          size="md"
          variant="solid"
          theme="green"
          label="Accept"
          class="rounded-lg"
          @click="acceptIncomingCall"
        >
          <template #prefix>
            <PhoneIcon class="fill-white h-4 w-4" />
          </template>
        </Button>
        <Button
          size="md"
          variant="solid"
          theme="red"
          label="Reject"
          class="rounded-lg"
          @click="rejectIncomingCall"
        >
          <template #prefix>
            <PhoneIcon class="fill-white h-4 w-4 rotate-[135deg]" />
          </template>
        </Button>
      </div>
    </div>
  </div>
  <div
    v-show="showSmallCallWindow"
    class="flex items-center justify-between gap-3 bg-gray-900 text-base text-gray-300 ml-2 px-2 py-[7px] rounded-lg cursor-pointer select-none"
    @click="toggleCallWindow"
  >
    <div class="flex items-center gap-2">
      <Avatar
        :image="contact.image"
        :label="contact.full_name"
        class="flex items-center justify-center !h-5 !w-5 relative"
      />
      <div class="truncate max-w-[120px]">
        {{ contact.full_name }}
      </div>
    </div>
    <div v-if="onCall" class="flex items-center gap-2">
      <div class="my-1 min-w-[40px] text-center">
        {{ counterUp?.updatedTime }}
      </div>
      <Button variant="solid" theme="red" class="rounded-full !h-6 !w-6">
        <template #icon>
          <PhoneIcon
            class="fill-white h-4 w-4 rotate-[135deg]"
            @click.stop="hangUpCall"
          />
        </template>
      </Button>
    </div>
    <div v-else-if="calling" class="flex items-center gap-3">
      <div class="my-1">
        {{ callStatus == 'ringing' ? 'Ringing...' : 'Calling...' }}
      </div>
      <Button
        variant="solid"
        theme="red"
        class="rounded-full !h-6 !w-6"
        @click.stop="cancelCall"
      >
        <template #icon>
          <PhoneIcon class="fill-white h-4 w-4 rotate-[135deg]" />
        </template>
      </Button>
    </div>
    <div v-else class="flex items-center gap-2">
      <Button
        variant="solid"
        theme="green"
        class="rounded-full !h-6 !w-6 pulse relative"
        @click.stop="acceptIncomingCall"
      >
        <template #icon>
          <PhoneIcon class="fill-white h-4 w-4 animate-pulse" />
        </template>
      </Button>
      <Button
        variant="solid"
        theme="red"
        class="rounded-full !h-6 !w-6"
        @click.stop="rejectIncomingCall"
      >
        <template #icon>
          <PhoneIcon class="fill-white h-4 w-4 rotate-[135deg]" />
        </template>
      </Button>
    </div>
  </div>
  <NoteModal v-model="showNoteModal" :note="note" @updateNote="updateNote" />
</template>

<script setup>
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import MinimizeIcon from '@/components/Icons/MinimizeIcon.vue'
import DialpadIcon from '@/components/Icons/DialpadIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import CountUpTimer from '@/components/CountUpTimer.vue'
import { Device } from '@twilio/voice-sdk'
import { useDraggable, useWindowSize } from '@vueuse/core'
import { contactsStore } from '@/stores/contacts'
import { Avatar, call } from 'frappe-ui'
import { onMounted, ref, watch, getCurrentInstance } from 'vue'
import NoteModal from './NoteModal.vue'

const { getContact } = contactsStore()

let device = ''
let log = ref('Connecting...')
let _call = ref(null)
const contact = ref({
  full_name: '',
  mobile_no: '',
})

let showCallPopup = ref(false)
let showSmallCallWindow = ref(false)
let onCall = ref(false)
let calling = ref(false)
let muted = ref(false)
let callPopup = ref(null)
let counterUp = ref(null)
let callStatus = ref('')
const showNoteModal = ref(false)
const note = ref({
  title: '',
  content: '',
})

async function updateNote(_note) {
  if (_note.name) {
    await call('frappe.client.set_value', {
      doctype: 'CRM Note',
      name: _note.name,
      fieldname: _note,
    })
    note.value = _note
  } else {
    let d = await call('frappe.client.insert', {
      doc: {
        doctype: 'CRM Note',
        title: _note.title,
        content: _note.content,
      },
    })
    if (d.name) {
      note.value = d
      await call('crm.twilio.api.add_note_to_call_log', {
        call_sid: _call.value.parameters.CallSid,
        note: d.name,
      })
    }
  }
}

const { width, height } = useWindowSize()

let { style } = useDraggable(callPopup, {
  initialValue: { x: width.value - 280, y: height.value - 310 },
  preventDefault: true,
})

async function startupClient() {
  log.value = 'Requesting Access Token...'

  try {
    const data = await call('crm.twilio.api.generate_access_token')
    log.value = 'Got a token.'
    intitializeDevice(data.token)
  } catch (err) {
    log.value = 'An error occurred. ' + err.message
  }
}

function intitializeDevice(token) {
  device = new Device(token, {
    codecPreferences: ['opus', 'pcmu'],
    fakeLocalDTMF: true,
    enableRingingState: true,
  })

  addDeviceListeners()

  device.register()
}

function addDeviceListeners() {
  device.on('registered', () => {
    log.value = 'Ready to make and receive calls!'
  })

  device.on('unregistered', (device) => {
    log.value = 'Logged out'
  })

  device.on('error', (error) => {
    log.value = 'Twilio.Device Error: ' + error.message
  })

  device.on('incoming', handleIncomingCall)

  device.on('tokenWillExpire', async () => {
    const data = await call('crm.twilio.api.generate_access_token')
    device.updateToken(data.token)
  })
}

function toggleMute() {
  if (_call.value.isMuted()) {
    _call.value.mute(false)
    muted.value = false
  } else {
    _call.value.mute()
    muted.value = true
  }
}

function handleIncomingCall(call) {
  log.value = `Incoming call from ${call.parameters.From}`

  // get name of the caller from the phone number

  contact.value = getContact(call.parameters.From)

  if (!contact.value) {
    contact.value = {
      full_name: 'Unknown',
      mobile_no: call.parameters.From,
    }
  }

  showCallPopup.value = true
  _call.value = call

  _call.value.on('accept', (conn) => {
    console.log('conn', conn)
  })

  // add event listener to call object
  call.on('cancel', handleDisconnectedIncomingCall)
  call.on('disconnect', handleDisconnectedIncomingCall)
  call.on('reject', handleDisconnectedIncomingCall)
}

async function acceptIncomingCall() {
  log.value = 'Accepted incoming call.'
  onCall.value = true
  await _call.value.accept()
  counterUp.value.start()
}

function rejectIncomingCall() {
  _call.value.reject()
  log.value = 'Rejected incoming call'
  showCallPopup.value = false
  if (showSmallCallWindow.value == undefined) {
    showSmallCallWindow = false
  } else {
    showSmallCallWindow.value = false
  }
  callStatus.value = ''
  muted.value = false
}

function hangUpCall() {
  _call.value.disconnect()
  log.value = 'Hanging up incoming call'
  onCall.value = false
  callStatus.value = ''
  muted.value = false
  note.value = {
    title: '',
    content: '',
  }
  counterUp.value.stop()
}

function handleDisconnectedIncomingCall() {
  log.value = `Call ended from handle disconnected Incoming call.`
  showCallPopup.value = false
  if (showSmallCallWindow.value == undefined) {
    showSmallCallWindow = false
  } else {
    showSmallCallWindow.value = false
  }
  _call.value = null
  muted.value = false
  onCall.value = false
  counterUp.value.stop()
}

async function makeOutgoingCall(number) {
  contact.value = getContact(number)

  if (device) {
    log.value = `Attempting to call ${contact.value.mobile_no} ...`

    try {
      _call.value = await device.connect({
        params: { To: contact.value.mobile_no },
      })

      _call.value.on('messageReceived', (message) => {
        let info = message.content
        callStatus.value = info.CallStatus

        log.value = `Call status: ${info.CallStatus}`

        if (info.CallStatus == 'in-progress') {
          log.value = `Call in progress.`
          calling.value = false
          onCall.value = true
          counterUp.value.start()
        }
      })

      _call.value.on('accept', () => {
        log.value = `Initiated call!`
        showCallPopup.value = true
        calling.value = true
        onCall.value = false
      })
      _call.value.on('disconnect', (conn) => {
        log.value = `Call ended from makeOutgoing call disconnect.`
        calling.value = false
        onCall.value = false
        showCallPopup.value = false
        showSmallCallWindow = false
        _call.value = null
        callStatus.value = ''
        muted.value = false
        counterUp.value.stop()
        note.value = {
          title: '',
          content: '',
        }
      })
      _call.value.on('cancel', () => {
        log.value = `Call ended from makeOutgoing call cancel.`
        calling.value = false
        onCall.value = false
        showCallPopup.value = false
        showSmallCallWindow = false
        _call.value = null
        callStatus.value = ''
        muted.value = false
        note.value = {
          title: '',
          content: '',
        }
        counterUp.value.stop()
      })
    } catch (error) {
      log.value = `Could not connect call: ${error.message}`
    }
  } else {
    log.value = 'Unable to make call.'
  }
}

function cancelCall() {
  _call.value.disconnect()
  showCallPopup.value = false
  if (showSmallCallWindow.value == undefined) {
    showSmallCallWindow = false
  } else {
    showSmallCallWindow.value = false
  }
  calling.value = false
  onCall.value = false
  callStatus.value = ''
  muted.value = false
  note.value = {
    title: '',
    content: '',
  }
}

function toggleCallWindow() {
  showCallPopup.value = !showCallPopup.value
  if (showSmallCallWindow.value == undefined) {
    showSmallCallWindow = !showSmallCallWindow
  } else {
    showSmallCallWindow.value = !showSmallCallWindow.value
  }
}

onMounted(() => startupClient())

watch(
  () => log.value,
  (value) => {
    console.log(value)
  },
  { immediate: true }
)

const app = getCurrentInstance()
app.appContext.config.globalProperties.makeCall = makeOutgoingCall
</script>

<style scoped>
.pulse::before {
  content: '';
  position: absolute;
  border: 1px solid green;
  width: calc(100% + 20px);
  height: calc(100% + 20px);
  border-radius: 50%;
  animation: pulse 1s linear infinite;
}

.pulse::after {
  content: '';
  position: absolute;
  border: 1px solid green;
  width: calc(100% + 20px);
  height: calc(100% + 20px);
  border-radius: 50%;
  animation: pulse 1s linear infinite;
  animation-delay: 0.3s;
}

@keyframes pulse {
  0% {
    transform: scale(0.5);
    opacity: 0;
  }

  50% {
    transform: scale(1);
    opacity: 1;
  }

  100% {
    transform: scale(1.3);
    opacity: 0;
  }
}
</style>
