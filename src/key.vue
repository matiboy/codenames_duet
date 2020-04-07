<template>
<table id="key" border="0" class="mb-4">
  <tr v-for="(row, i) in rows" :key="i">
    <td 
    v-for="(word, j) in row" :key="j"
    :class="{good: green.includes(word), assassin: black.includes(word)}"></td>
  </tr>
</table>
</template>
<script lang="ts">
import Vue from 'vue'
import {chunk} from 'lodash'

export default Vue.extend({
  name: 'key',
  props: ['words', 'green', 'black'],
  data() {
    return {
    }
  },
  computed: {
    rows() {
      return chunk(this.words, 5)
    }
  }
})
</script>