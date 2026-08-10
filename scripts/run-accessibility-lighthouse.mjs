import { mkdir, rm, writeFile } from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'

import { launch } from '../app/frontend/node_modules/chrome-launcher/dist/chrome-launcher.js'
import lighthouse from '../app/frontend/node_modules/lighthouse/core/index.js'


const projectRoot = path.resolve(import.meta.dirname, '..')
const reportsDirectory = path.join(projectRoot, 'reports')
const profileDirectory = path.join(reportsDirectory, `lighthouse-profile-${process.pid}`)
const targetUrl = process.argv[2] || 'http://127.0.0.1:5173/'

await mkdir(reportsDirectory, { recursive: true })
await mkdir(profileDirectory, { recursive: true })

const browser = await launch({
  chromePath: process.env.CHROME_PATH,
  chromeFlags: ['--headless=new', '--disable-gpu', '--no-first-run'],
  userDataDir: profileDirectory,
})

try {
  const result = await lighthouse(targetUrl, {
    port: browser.port,
    onlyCategories: ['accessibility'],
    output: ['json', 'html'],
    formFactor: 'desktop',
    screenEmulation: {
      mobile: false,
      width: 1350,
      height: 940,
      deviceScaleFactor: 1,
      disabled: false,
    },
  })

  if (!result || !Array.isArray(result.report)) {
    throw new Error('Lighthouse did not return both requested reports.')
  }

  const [jsonReport, htmlReport] = result.report
  const parsed = JSON.parse(jsonReport)
  const score = parsed.categories.accessibility.score
  await writeFile(path.join(reportsDirectory, 'phase8-lighthouse.report.json'), jsonReport)
  await writeFile(path.join(reportsDirectory, 'phase8-lighthouse.report.html'), htmlReport)
  console.log(`Accessibility score: ${Math.round(score * 100)}`)

  if (score !== 1) {
    process.exitCode = 1
  }
} finally {
  await browser.kill()
  await new Promise(resolve => setTimeout(resolve, 500))
  await rm(profileDirectory, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 })
}
