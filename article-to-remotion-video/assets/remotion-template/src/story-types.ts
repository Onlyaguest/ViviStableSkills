export type Stat = {value: string; label: string};

export type SceneType = 'hero' | 'workflow' | 'chips' | 'distribution' | 'closing';

export type Scene = {
  id: string;
  type: SceneType;
  durationSeconds: number;
  kicker: string;
  title: string;
  accentTitle?: string;
  body?: string;
  quote?: string;
  image?: string;
  steps?: string[];
  stats?: Stat[];
  chips?: string[];
  total?: number;
  totalLabel?: string;
  footer?: string;
  badges?: string[];
  narration?: string;
  audio?: string;
  audioPlaybackRate?: number;
};

export type Story = {
  meta: {
    title: string;
    sourceTitle: string;
    sourceUrl?: string;
    authorVoice?: string;
    fps?: number;
    width?: number;
    height?: number;
  };
  theme?: Partial<{
    background: string;
    panel: string;
    text: string;
    muted: string;
    primary: string;
    success: string;
  }>;
  scenes: Scene[];
};
