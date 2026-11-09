import React from 'react';
import {Composition, Series, AbsoluteFill, Img, staticFile} from 'remotion';
import {scenes, FPS, totalFrames} from './scenes';

const font = 'Arial, Helvetica, sans-serif';

const Scene = ({title, bullets, images}) => {
  const hasImages = images.length > 0;
  return (
    <AbsoluteFill style={{backgroundColor: '#1b1b1b', color: '#f2f2f2', fontFamily: font, padding: 56}}>
      <div style={{fontSize: 48, fontWeight: 700, marginBottom: 32}}>{title}</div>
      <div style={{display: 'flex', flex: 1, gap: 40, minHeight: 0}}>
        <div style={{flex: 1, fontSize: hasImages ? 28 : 34, lineHeight: 1.45}}>
          {bullets.map((b) => (
            <div key={b} style={{marginBottom: 18}}>
              {'• '}
              {b}
            </div>
          ))}
        </div>
        {hasImages ? (
          <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 16, minHeight: 0}}>
            {images.map((name) => (
              <Img
                key={name}
                src={staticFile(name)}
                style={{width: '100%', flex: 1, minHeight: 0, objectFit: 'contain', backgroundColor: '#000'}}
              />
            ))}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

const Walkthrough = () => (
  <Series>
    {scenes.map((s) => (
      <Series.Sequence key={s.title} durationInFrames={s.seconds * FPS}>
        <Scene title={s.title} bullets={s.bullets} images={s.images} />
      </Series.Sequence>
    ))}
  </Series>
);

export const Root = () => (
  <Composition
    id="Walkthrough"
    component={Walkthrough}
    durationInFrames={totalFrames}
    fps={FPS}
    width={1280}
    height={720}
  />
);
