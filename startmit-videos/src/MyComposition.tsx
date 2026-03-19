import {useCurrentFrame, useVideoConfig, interpolate, spring} from 'remotion';

export const MyComposition: React.FC<{
  title: string;
  subtitle: string;
}> = ({title, subtitle}) => {
  const frame = useCurrentFrame();
  const {durationInFrames, fps} = useVideoConfig();

  // Fade in animation
  const opacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Scale animation using spring
  const scale = spring({
    fps,
    frame,
    config: {
      damping: 100,
      stiffness: 200,
      mass: 0.5,
    },
  });

  // Slide up animation for subtitle
  const translateY = interpolate(frame, [30, 60], [50, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        flex: 1,
        backgroundColor: '#0f172a',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: 'sans-serif',
      }}
    >
      <div
        style={{
          opacity,
          transform: `scale(${scale})`,
        }}
      >
        <h1
          style={{
            fontSize: 120,
            fontWeight: 'bold',
            color: '#3b82f6',
            margin: 0,
          }}
        >
          {title}
        </h1>
      </div>
      <div
        style={{
          opacity,
          transform: `translateY(${translateY}px)`,
          marginTop: 40,
        }}
      >
        <p
          style={{
            fontSize: 48,
            color: '#94a3b8',
            margin: 0,
          }}
        >
          {subtitle}
        </p>
      </div>
    </div>
  );
};
