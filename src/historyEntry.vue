<template>
<div v-html="entryContent">
</div>
</template>
<script lang="ts">
import Vue from 'vue'

const enum Kinds {
  GUESS = 'guess'
  GREEN = 'green'
  STOP = 'stop'
  BLACK = 'black'
  CREATED = 'created'
  LOST = 'lost'
  WON = 'won'
  SUDDEN_DEATH = 'sudden_death'
}

export default Vue.extend({
  props: ['entry'],
  computed: {
    entryContent() {
      if(Kinds.GUESS === this.entry.)
    }
  }
})
</script>