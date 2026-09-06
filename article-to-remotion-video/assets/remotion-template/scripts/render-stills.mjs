import {readFileSync, mkdirSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {join} from 'node:path';

const story = JSON.parse(readFileSync(new URL('../story.json', import.meta.url), 'utf8'));
const fps = story.meta.fps ?? 30;
mkdirSync(new URL('../out/stills', import.meta.url), {recursive: true});

let cursor = 0;
for (const scene of story.scenes) {
  const duration = Math.round(scene.durationSeconds * fps);
  const frame = cursor + Math.floor(duration * 0.55);
  const output = join('out', 'stills', `${scene.id}.png`);
  const command = process.platform === 'win32' ? 'npx.cmd' : 'npx';
  const browserArgs = process.env.REMOTION_BROWSER_EXECUTABLE
    ? [`--browser-executable=${process.env.REMOTION_BROWSER_EXECUTABLE}`]
    : [];
  const result = spawnSync(
    command,
    ['remotion', 'still', 'src/index.ts', 'ArticleVideo', output, `--frame=${frame}`, ...browserArgs],
    {stdio: 'inherit'},
  );
  if (result.status !== 0) process.exit(result.status ?? 1);
  cursor += duration;
}
