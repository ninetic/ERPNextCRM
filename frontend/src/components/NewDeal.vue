<template>
  <div class="flex flex-col gap-4">
    <div v-for="section in allFields" :key="section.section">
      <div class="grid grid-cols-3 gap-4">
        <div v-for="field in section.fields" :key="field.name">
          <div class="text-gray-600 text-sm mb-2">{{ field.label }}</div>
          <FormControl
            v-if="field.type === 'select'"
            type="select"
            :options="field.options"
            v-model="newDeal[field.name]"
          >
            <template v-if="field.name == 'deal_status'" #prefix>
              <IndicatorIcon :class="dealStatuses[newDeal[field.name]].color" />
            </template>
          </FormControl>
          <FormControl
            v-else-if="field.type === 'email'"
            type="email"
            v-model="newDeal[field.name]"
          />
          <Autocomplete
            v-else-if="field.type === 'link'"
            :options="activeAgents"
            :value="getUser(newDeal[field.name]).full_name"
            @change="(option) => (newDeal[field.name] = option.email)"
            :placeholder="field.placeholder"
          >
            <template #prefix>
              <UserAvatar class="mr-2" :user="newDeal[field.name]" size="sm" />
            </template>
            <template #item-prefix="{ option }">
              <UserAvatar class="mr-2" :user="option.email" size="sm" />
            </template>
          </Autocomplete>
          <Dropdown
            v-else-if="field.type === 'dropdown'"
            :options="statusDropdownOptions(newDeal, 'deal')"
            class="w-full flex-1"
          >
            <template #default="{ open }">
              <Button
                :label="newDeal[field.name]"
                class="justify-between w-full"
              >
                <template #prefix>
                  <IndicatorIcon :class="dealStatuses[newDeal[field.name]].color" />
                </template>
                <template #default>{{ newDeal[field.name] }}</template>
                <template #suffix>
                  <FeatherIcon
                    :name="open ? 'chevron-up' : 'chevron-down'"
                    class="h-4 text-gray-600"
                  />
                </template>
              </Button>
            </template>
          </Dropdown>
          <FormControl v-else type="text" v-model="newDeal[field.name]" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import { usersStore } from '@/stores/users'
import { dealStatuses, statusDropdownOptions, activeAgents } from '@/utils'
import {
  FormControl,
  Button,
  Autocomplete,
  Dropdown,
  FeatherIcon,
} from 'frappe-ui'
import { computed } from 'vue'

const { getUser, users } = usersStore()
const props = defineProps({
  newDeal: {
    type: Object,
    required: true,
  },
})

const allFields = [
  {
    section: 'Deal Details',
    fields: [
      {
        label: 'Salutation',
        name: 'salutation',
        type: 'select',
        options: [
          {
            label: 'Mr',
            value: 'Mr',
          },
          {
            label: 'Ms',
            value: 'Ms',
          },
          {
            label: 'Mrs',
            value: 'Mrs',
          },
        ],
      },
      {
        label: 'First Name',
        name: 'first_name',
        type: 'data',
      },
      {
        label: 'Last Name',
        name: 'last_name',
        type: 'data',
      },
      {
        label: 'Email',
        name: 'email',
        type: 'data',
      },
      {
        label: 'Mobile no',
        name: 'mobile_no',
        type: 'data',
      },
    ],
  },
  {
    section: 'Other Details',
    fields: [
      {
        label: 'Organization',
        name: 'organization_name',
        type: 'data',
      },
      {
        label: 'Status',
        name: 'deal_status',
        type: 'select',
        options: statusDropdownOptions(props.newDeal, 'deal'),
      },
      {
        label: 'Deal owner',
        name: 'lead_owner',
        type: 'link',
        placeholder: 'Deal owner',
      },
    ],
  },
]
</script>
