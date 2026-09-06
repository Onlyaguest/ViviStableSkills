import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  Series,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import type {Scene, Story} from './story-types';

type Theme = Required<NonNullable<Story['theme']>>;

const defaults: Theme = {
  background: '#07100F',
  panel: '#101A18',
  text: '#F4F0E7',
  muted: '#9DAAA4',
  primary: '#F16B42',
  success: '#57E0BD',
};

const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};

const Background: React.FC<{theme: Theme; frame: number}> = ({theme, frame}) => {
  const drift = frame * 0.1;
  return (
    <AbsoluteFill
      style={{
        backgroundColor: theme.background,
        backgroundImage: `radial-gradient(circle at 78% 18%, ${theme.primary}1F, transparent 30%), linear-gradient(rgba(210,232,225,.12) 1px, transparent 1px), linear-gradient(90deg, rgba(210,232,225,.12) 1px, transparent 1px)`,
        backgroundSize: `auto, 72px 72px, 72px 72px`,
        backgroundPosition: `0 0, ${drift}px ${drift}px, ${drift}px ${drift}px`,
      }}
    >
      <AbsoluteFill style={{background: `linear-gradient(180deg, transparent, ${theme.background} 92%)`}} />
    </AbsoluteFill>
  );
};

const MediaCard: React.FC<{src: string; theme: Theme}> = ({src, theme}) => (
  <div
    style={{
      width: 510,
      border: '1px solid rgba(210,232,225,.18)',
      borderRadius: 26,
      padding: 12,
      background: `${theme.panel}EE`,
      boxShadow: '0 34px 90px rgba(0,0,0,.48)',
    }}
  >
    <Img
      src={staticFile(src)}
      style={{width: '100%', height: 600, objectFit: 'contain', borderRadius: 18, display: 'block'}}
    />
    <div style={{padding: '14px 10px 6px', color: theme.muted, fontSize: 16}}>SOURCE IMAGE</div>
  </div>
);

const Kicker: React.FC<{children: React.ReactNode; theme: Theme}> = ({children, theme}) => (
  <div style={{display: 'flex', alignItems: 'center', gap: 18, color: theme.success, fontSize: 22, fontWeight: 750, letterSpacing: 3}}>
    <span style={{width: 64, height: 2, background: theme.primary}} />
    {children}
  </div>
);

const Stats: React.FC<{scene: Scene; theme: Theme; frame: number}> = ({scene, theme, frame}) => (
  <div style={{display: 'grid', gridTemplateColumns: `repeat(${Math.min(4, scene.stats?.length ?? 1)}, 1fr)`, gap: 14, marginTop: 30}}>
    {(scene.stats ?? []).map((stat, index) => {
      const amount = interpolate(frame, [50 + index * 9, 72 + index * 9], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
      return (
        <div
          key={`${stat.value}-${stat.label}`}
          style={{
            padding: '23px 24px',
            minHeight: 120,
            borderRadius: 18,
            borderTop: `3px solid ${index === 0 ? theme.primary : theme.success}`,
            background: theme.panel,
            opacity: amount,
            transform: `translateY(${(1 - amount) * 18}px)`,
          }}
        >
          <div style={{fontSize: 48, lineHeight: 1, fontWeight: 850, color: index === 0 ? theme.primary : theme.success}}>{stat.value}</div>
          <div style={{fontSize: 19, marginTop: 12, color: theme.muted}}>{stat.label}</div>
        </div>
      );
    })}
  </div>
);

const Workflow: React.FC<{scene: Scene; theme: Theme; frame: number}> = ({scene, theme, frame}) => (
  <>
    <div style={{display: 'flex', alignItems: 'center', gap: 10, marginTop: 42, flexWrap: 'wrap'}}>
      {(scene.steps ?? []).map((step, index) => {
        const amount = interpolate(frame, [28 + index * 10, 48 + index * 10], [0, 1], clamp);
        return (
          <React.Fragment key={step}>
            <div style={{padding: '14px 20px', borderRadius: 14, border: `1px solid ${theme.primary}`, background: `${theme.primary}17`, fontSize: 20, opacity: amount}}>{step}</div>
            {index < (scene.steps?.length ?? 0) - 1 ? <span style={{color: theme.success, fontSize: 25}}>→</span> : null}
          </React.Fragment>
        );
      })}
    </div>
    <Stats scene={scene} theme={theme} frame={frame} />
  </>
);

const Chips: React.FC<{scene: Scene; theme: Theme; frame: number}> = ({scene, theme, frame}) => (
  <div style={{display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0,1fr))', gap: 16, marginTop: 34}}>
    {(scene.chips ?? []).map((chip, index) => {
      const amount = interpolate(frame, [24 + index * 8, 45 + index * 8], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
      return (
        <div
          key={chip}
          style={{
            height: 84,
            borderRadius: 17,
            border: `1px solid ${index % 3 === 0 ? theme.primary : 'rgba(210,232,225,.18)'}`,
            background: index % 3 === 0 ? `${theme.primary}14` : theme.panel,
            display: 'flex',
            alignItems: 'center',
            padding: '0 24px',
            fontSize: 25,
            fontWeight: 650,
            opacity: amount,
            transform: `translateX(${(1 - amount) * 32}px)`,
          }}
        >
          <span style={{width: 42, color: theme.muted, fontSize: 16}}>{String(index + 1).padStart(2, '0')}</span>
          {chip}
        </div>
      );
    })}
  </div>
);

const Distribution: React.FC<{scene: Scene; theme: Theme; frame: number; duration: number}> = ({scene, theme, frame, duration}) => {
  const total = Math.floor(interpolate(frame, [35, Math.min(125, duration * 0.55)], [0, scene.total ?? 0], {...clamp, easing: Easing.out(Easing.cubic)}));
  return (
    <>
      <Workflow scene={{...scene, stats: []}} theme={theme} frame={frame} />
      <div style={{display: 'flex', alignItems: 'flex-end', gap: 28, marginTop: 46}}>
        <div style={{fontSize: 190, lineHeight: .76, fontWeight: 900, letterSpacing: -14, color: theme.primary, fontVariantNumeric: 'tabular-nums'}}>{total}</div>
        <div style={{fontSize: 42, fontWeight: 800, paddingBottom: 8}}>{scene.totalLabel ?? 'items'}</div>
      </div>
      <Stats scene={scene} theme={theme} frame={frame} />
      {scene.footer ? <div style={{marginTop: 20, color: theme.muted, fontSize: 20}}>{scene.footer}</div> : null}
    </>
  );
};

const SceneView: React.FC<{
  scene: Scene;
  index: number;
  startFrame: number;
  duration: number;
  totalFrames: number;
  storyTitle: string;
  theme: Theme;
}> = ({scene, index, startFrame, duration, totalFrames, storyTitle, theme}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const entrance = spring({frame, fps, config: {damping: 18, stiffness: 110}});
  const opacity = interpolate(frame, [0, 16, duration - 18, duration], [0, 1, 1, 0], clamp);
  const progress = Math.min(1, (startFrame + frame) / totalFrames);
  const hasImage = Boolean(scene.image);

  return (
    <AbsoluteFill style={{fontFamily: 'Inter, "PingFang SC", "Microsoft YaHei", sans-serif', color: theme.text, opacity}}>
      <Background theme={theme} frame={startFrame + frame} />
      <div style={{position: 'absolute', left: 64, right: 64, top: 42, display: 'flex', justifyContent: 'space-between', color: theme.muted, fontSize: 17, letterSpacing: 2}}>
        <span>{storyTitle.toUpperCase()}</span>
        <span>{String(index + 1).padStart(2, '0')} / {scene.id.toUpperCase()}</span>
      </div>
      <div style={{position: 'absolute', left: 64, right: 64, bottom: 40, height: 2, background: 'rgba(210,232,225,.14)'}}>
        <div style={{height: '100%', width: `${progress * 100}%`, background: `linear-gradient(90deg, ${theme.primary}, ${theme.success})`}} />
      </div>

      <div
        style={{
          position: 'absolute',
          left: 100,
          right: 100,
          top: 120,
          bottom: 90,
          display: 'grid',
          gridTemplateColumns: hasImage ? '1fr 540px' : '1fr',
          gap: 70,
          alignItems: 'center',
          transform: `translateY(${(1 - entrance) * 34}px)`,
        }}
      >
        <div>
          <Kicker theme={theme}>{scene.kicker}</Kicker>
          <h1 style={{fontSize: scene.type === 'closing' ? 82 : 76, lineHeight: 1.08, letterSpacing: -4, margin: '30px 0 18px', maxWidth: 1100}}>{scene.title}</h1>
          {scene.accentTitle ? <div style={{fontSize: 72, lineHeight: 1.04, color: theme.primary, fontWeight: 900, letterSpacing: -4}}>{scene.accentTitle}</div> : null}
          {scene.body ? <p style={{fontSize: 26, lineHeight: 1.55, color: theme.muted, maxWidth: 960, margin: '25px 0 0'}}>{scene.body}</p> : null}
          {scene.quote ? <div style={{marginTop: 36, padding: '20px 25px', borderRadius: 18, border: `1px solid ${theme.primary}88`, background: `${theme.primary}12`, display: 'inline-block', fontSize: 27}}>“{scene.quote}”</div> : null}
          {scene.type === 'workflow' ? <Workflow scene={scene} theme={theme} frame={frame} /> : null}
          {scene.type === 'chips' ? <Chips scene={scene} theme={theme} frame={frame} /> : null}
          {scene.type === 'distribution' ? <Distribution scene={scene} theme={theme} frame={frame} duration={duration} /> : null}
          {scene.type === 'closing' && scene.badges ? (
            <div style={{display: 'flex', gap: 12, marginTop: 32}}>
              {scene.badges.map((badge) => <span key={badge} style={{padding: '10px 16px', borderRadius: 99, border: '1px solid rgba(210,232,225,.18)', color: theme.muted}}>{badge}</span>)}
            </div>
          ) : null}
        </div>
        {scene.image ? <MediaCard src={scene.image} theme={theme} /> : null}
      </div>

      {scene.audio ? (
        <Audio
          src={staticFile(scene.audio)}
          playbackRate={scene.audioPlaybackRate ?? 1}
          volume={0.96}
        />
      ) : null}
    </AbsoluteFill>
  );
};

export const ArticleVideo: React.FC<{story: Story}> = ({story}) => {
  const {fps, durationInFrames} = useVideoConfig();
  const theme: Theme = {...defaults, ...(story.theme ?? {})};
  let cursor = 0;

  return (
    <AbsoluteFill style={{backgroundColor: theme.background}}>
      <Series>
        {story.scenes.map((scene, index) => {
          const duration = Math.round(scene.durationSeconds * fps);
          const startFrame = cursor;
          cursor += duration;
          return (
            <Series.Sequence key={scene.id} durationInFrames={duration}>
              <SceneView
                scene={scene}
                index={index}
                startFrame={startFrame}
                duration={duration}
                totalFrames={durationInFrames}
                storyTitle={story.meta.title}
                theme={theme}
              />
            </Series.Sequence>
          );
        })}
      </Series>
    </AbsoluteFill>
  );
};
