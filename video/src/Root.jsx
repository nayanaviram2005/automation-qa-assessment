import React from 'react';
import {Composition, Sequence, AbsoluteFill, OffthreadVideo, staticFile, interpolate, useCurrentFrame} from 'remotion';
import {overlays, intro, outro, segments, FPS, INTRO_SECONDS, OUTRO_SECONDS, VIDEO_FRAMES, totalFrames} from './overlays';

const font = 'Arial, Helvetica, sans-serif';
const FADE = 12;

const useFade = (duration) => {
  const frame = useCurrentFrame();
  return interpolate(frame, [0, FADE, duration - FADE, duration], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
};

const Card = ({title, lines, duration}) => {
  const opacity = useFade(duration);
  return (
    <AbsoluteFill style={{backgroundColor: '#1b1b1b', color: '#f2f2f2', fontFamily: font, padding: 80}}>
      <div style={{opacity}}>
        <div style={{fontSize: 56, fontWeight: 700, marginBottom: 40}}>{title}</div>
        {lines.map((line) => (
          <div key={line} style={{fontSize: 32, lineHeight: 1.4, marginBottom: 20}}>
            {'• '}
            {line}
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

const Callout = ({text, box, duration}) => {
  const opacity = useFade(duration);
  return (
    <div
      style={{
        position: 'absolute',
        left: box.left,
        top: box.top,
        width: box.width,
        boxSizing: 'border-box',
        padding: '16px 22px',
        backgroundColor: 'rgba(17,17,17,0.94)',
        borderLeft: '6px solid #f0b429',
        borderRadius: 6,
        color: '#ffffff',
        fontFamily: font,
        fontSize: 28,
        lineHeight: 1.35,
        opacity,
      }}
    >
      {text}
    </div>
  );
};

const Walkthrough = () => {
  const introFrames = INTRO_SECONDS * FPS;
  const videoFrames = VIDEO_FRAMES;
  const outroFrames = OUTRO_SECONDS * FPS;
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <Sequence from={0} durationInFrames={introFrames}>
        <Card title={intro.title} lines={intro.lines} duration={introFrames} />
      </Sequence>
      <Sequence from={introFrames} durationInFrames={videoFrames}>
        {segments.map((s) => (
          <Sequence key={s.from} from={s.offset} durationInFrames={s.frames}>
            <AbsoluteFill>
              <OffthreadVideo src={staticFile('walkthrough.mp4')} startFrom={s.startFrom} style={{width: '100%', height: '100%'}} />
            </AbsoluteFill>
          </Sequence>
        ))}
        {overlays.map((o) => {
          const from = Math.round(o.start * FPS);
          const duration = Math.round((o.end - o.start) * FPS);
          return (
            <Sequence key={o.text} from={from} durationInFrames={duration}>
              <Callout text={o.text} box={o.box} duration={duration} />
            </Sequence>
          );
        })}
      </Sequence>
      <Sequence from={introFrames + videoFrames} durationInFrames={outroFrames}>
        <Card title={outro.title} lines={outro.lines} duration={outroFrames} />
      </Sequence>
    </AbsoluteFill>
  );
};

export const Root = () => (
  <Composition id="Walkthrough" component={Walkthrough} durationInFrames={totalFrames} fps={FPS} width={1600} height={900} />
);
