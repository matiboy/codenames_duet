import {
  ConsoleLogger, LogLevel
 } from 'amazon-chime-sdk-js'
import { TestSound } from './chime/test-sound'

const logger = new ConsoleLogger('The Gary', LogLevel.DEBUG)

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('key').addEventListener('click', async () => {
    logger.debug(() => 'Clicked on table')
    // const config = new MeetingSessionConfiguration()
  })
})