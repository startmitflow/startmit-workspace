# StartMit Video Generation with Remotion

**Location:** `startmit-videos/`  
**Purpose:** Create marketing videos, explainers, and social content for StartMit

---

## What is Remotion?

Remotion is a React-based framework for creating videos programmatically. Write video scenes as React components, then render to MP4.

**Use cases for StartMit:**
- Explainer videos about UG/GmbH formation
- Social media content (LinkedIn, Instagram)
- Product demos and walkthroughs
- Animated testimonials
- Educational content about German business law

---

## Installation

```bash
cd startmit-videos
npm install
```

---

## Project Structure

```
startmit-videos/
├── src/
│   ├── Root.tsx           # Composition definitions
│   └── MyComposition.tsx  # Video scenes
├── package.json
├── tsconfig.json
└── README.md
```

---

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Open Remotion Studio (preview) |
| `npm run build` | Render video to MP4 |
| `npm run upgrade` | Update Remotion to latest |

---

## Quick Start

### 1. Preview in Studio
```bash
npm run dev
```
Opens browser at `http://localhost:3000` for live preview.

### 2. Render Video
```bash
npx remotion render src/Root.tsx StartMitIntro out/video.mp4
```

---

## Composition: StartMitIntro

**Duration:** 5 seconds (150 frames @ 30fps)  
**Resolution:** 1920x1080 (Full HD)  
**Props:**
- `title`: Main headline (default: "StartMit")
- `subtitle`: Supporting text (default: "Empower Your Side Hustle with AI")

**Animations:**
- Title scales in with spring physics
- Subtitle fades and slides up
- Dark blue background (#0f172a)

---

## Creating New Videos

### Step 1: Create Component
```tsx
// src/ExplainerVideo.tsx
import {useCurrentFrame, interpolate} from 'remotion';

export const ExplainerVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [0, 1]);
  
  return (
    <div style={{opacity, background: 'white'}}>
      <h1>How to Form a UG in Germany</h1>
      {/* Your content */}
    </div>
  );
};
```

### Step 2: Register in Root
```tsx
// src/Root.tsx
import {ExplainerVideo} from './ExplainerVideo';

<Composition
  id="UGExplainer"
  component={ExplainerVideo}
  durationInFrames={300}
  fps={30}
  width={1920}
  height={1080}
/>
```

### Step 3: Render
```bash
npx remotion render src/Root.tsx UGExplainer out/ug-explainer.mp4
```

---

## Video Ideas for StartMit

| Video | Duration | Purpose |
|-------|----------|---------|
| **UG vs GmbH** | 60s | Educational, LinkedIn |
| **Formation Process** | 90s | Walkthrough, YouTube |
| **Client Testimonial** | 30s | Social proof, Instagram |
| **AI Automation Demo** | 45s | Product feature, website |
| **Tax Benefits Explained** | 120s | SEO content, blog |

---

## Resources

- **Remotion Docs:** https://www.remotion.dev/docs
- **Best Practices:** See `skills/remotion/rules/` for patterns
- **Examples:** https://github.com/remotion-dev/remotion/tree/main/packages/example

---

## Skills Installed

- `remotion` — Best practices and patterns
- `remotion-video-toolkit` — Additional utilities

---

*Ready to create videos. Run `npm run dev` to start.*
