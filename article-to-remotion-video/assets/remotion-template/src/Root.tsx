import React from 'react';
import {Composition} from 'remotion';
import storyData from '../story.json';
import {ArticleVideo} from './ArticleVideo';
import type {Story} from './story-types';

const story = storyData as Story;
const fps = story.meta.fps ?? 30;
const durationInFrames = Math.round(
  story.scenes.reduce((sum, scene) => sum + scene.durationSeconds, 0) * fps,
);

export const RemotionRoot: React.FC = () => (
  <Composition
    id="ArticleVideo"
    component={ArticleVideo}
    defaultProps={{story}}
    durationInFrames={durationInFrames}
    fps={fps}
    width={story.meta.width ?? 1920}
    height={story.meta.height ?? 1080}
  />
);
