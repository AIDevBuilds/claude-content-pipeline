import React from 'react';
import {Composition} from 'remotion';
import {Short, ShortProps, FPS} from './Short';

// Placeholder props so `npm run studio` opens without a spec. Real renders always
// pass --props from render_short.py, which fills brand values from config.json.
const sample: ShortProps = {
  brand: {
    canvas: '#FFFFFF', surface: '#F4F4F7', stroke: '#DCDCE4', textPrimary: '#18181B',
    textMuted: '#63636E', accentA: '#4F46E5', accentB: '#DC2626', brandName: 'Brand', url: 'example.com',
  },
  eyebrow: 'SERIES',
  audio: null,
  durationSec: 3,
  phrases: [{start: 0, end: 2, words: [{text: 'Sample', start: 0, end: 1}, {text: 'caption.', start: 1, end: 2}]}],
  emphasis: [],
  headers: [{at: 0, title: 'Header line.'}],
  nodes: {a: {icon: 'x', label: 'Node'}},
  states: [{at: 0, nodes: {a: {x: 496, y: 760, w: 300}}}],
  packets: [], chips: [], badges: [], meters: [], notes: [], icons: {},
};

export const Root: React.FC = () => (
  <Composition
    id="Short"
    component={Short}
    width={1080}
    height={1920}
    fps={FPS}
    durationInFrames={Math.ceil(sample.durationSec * FPS)}
    defaultProps={sample}
    calculateMetadata={({props}) => ({
      durationInFrames: Math.ceil((props.durationSec + 0.6) * FPS),
    })}
  />
);
