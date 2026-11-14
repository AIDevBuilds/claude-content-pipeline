import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Easing,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

export const FPS = 30;

// ── Spec types ────────────────────────────────────────────────────────────────
// A Short is ONE diagram that evolves through keyframed states, so every Short is
// purpose-built (YouTube demonetizes look-alike template output) and the visuals
// can follow the voiceover beat by beat.

type Tone = 'a' | 'b' | 'muted' | 'dark';
type Word = {text: string; start: number; end: number};
type Phrase = {start: number; end: number; words: Word[]};

export type NodeDef = {icon: string; label: string; sub?: string; tone?: Tone; mono?: boolean};
export type NodeState = {
  x: number; y: number; w: number;            // centre x/y on the 1080x1920 canvas, card width
  opacity?: number; tone?: Tone; label?: string; sub?: string; glow?: boolean;
  row?: boolean; h?: number;                 // row = wide card, icon left (for vertical stacks)
};
export type EdgeStyle = {tone?: Tone; glow?: boolean; width?: number};
export type Edge = [string, string] | [string, string, EdgeStyle];
export type State = {at: number; nodes: Record<string, NodeState>; edges?: Edge[]};
export type Packet = {path: string[]; start: number; end: number; blocked?: boolean};
// between: centre the chip in the gap between two nodes (it follows them as they move).
// toneAt: the chip turns accentB (the problem colour) at this time.
export type Chip = {node: string; text: string; at: number; until?: number; dx?: number; dy?: number;
  between?: [string, string]; toneAt?: number};
// A dashed vertical boundary line (e.g. between two modules).
export type Divider = {at: number; until?: number; x: number; y1: number; y2: number};
export type Badge = {node: string; icon: string; at: number; until?: number; tone?: Tone};
export type Meter = {at: number; until?: number; y: number; value: number; threshold?: number;
  label: string; caption: string};
export type Note = {at: number; until?: number; y: number; text: string; mono?: boolean; flipAt?: number};
export type Header = {at: number; title: string; accent?: string; accentAt?: number};

export type ShortProps = {
  brand: {
    canvas: string; surface: string; stroke: string; textPrimary: string;
    textMuted: string; accentA: string; accentB: string; brandName: string; url: string;
  };
  eyebrow: string;
  audio: string | null;
  durationSec: number;
  phrases: Phrase[];
  emphasis: string[];
  headers: Header[];
  nodes: Record<string, NodeDef>;
  states: State[];
  packets: Packet[];
  chips: Chip[];
  badges: Badge[];
  meters: Meter[];
  notes: Note[];
  dividers?: Divider[];
  icons: Record<string, string>;
};

// YouTube covers the right ~140px (buttons) and bottom ~480px (title, channel).
// The top ~260px is also covered: checked 6 Nov 2026 on a Samsung S25 (back and
// search icons over the band) and an iPhone 18 Pro (status bar over the band, back
// and search icons down to about y 255). Readable content stays in x 72..920,
// y 262..1440; card edges past x 920 come close to the like button.
const SAFE = {left: 72, right: 160};
const W = 1080 - SAFE.left - SAFE.right;
const FONT = 'Inter, "Helvetica Neue", Helvetica, Arial, sans-serif';
const MONO = '"SF Mono", Menlo, Consolas, monospace';
const MOVE = 0.5; // seconds for a state-to-state move

const fontFace = `@font-face { font-family: 'Inter';
  src: url('${staticFile('fonts/Inter-latin.woff2')}') format('woff2'); font-weight: 100 900; }`;

const Icon: React.FC<{svg?: string; size: number; color: string; stroke?: number}> = ({svg, size, color, stroke = 2}) =>
  svg ? (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={stroke}
      strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{__html: svg}} />
  ) : null;

const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
const within = (t: number, at: number, until?: number) => t >= at && (until === undefined || t < until);
const fadeWin = (t: number, at: number, until?: number) => {
  const inn = at <= 0 ? 1 : interpolate(t, [at, at + 0.25], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const out = until === undefined ? 1 : interpolate(t, [until - 0.2, until], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return Math.min(inn, out);
};

export const Short: React.FC<ShortProps> = (p) => {
  const {brand, eyebrow, audio, durationSec, phrases, emphasis, headers, nodes, states,
    packets, chips, badges, meters, notes, icons} = p;
  const dividers = p.dividers ?? [];
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const toneColor = (x?: Tone) =>
    x === 'b' ? brand.accentB : x === 'muted' ? brand.textMuted : x === 'dark' ? brand.textPrimary : brand.accentA;
  // Anything timed at 0 is fully drawn on frame 0: the hook frame never animates in
  // (it is also the frame YouTube offers as the thumbnail).
  const pop = (start: number) => start <= 0 ? 1 : spring({frame: frame - start * fps, fps, config: {damping: 14, stiffness: 170, mass: 0.6}});
  const isKey = (w: string) => emphasis.includes(w.replace(/[^\w']/g, '').toLowerCase());

  // ── Resolve every node's position for this frame ──────────────────────────
  const si = Math.max(0, states.reduce((acc, s, i) => (t >= s.at ? i : acc), 0));
  const cur = states[si];
  const prev = si > 0 ? states[si - 1] : null;
  const k = prev ? spring({frame: frame - cur.at * fps, fps, config: {damping: 200}, durationInFrames: Math.round(MOVE * fps)}) : 1;

  type Resolved = Required<Pick<NodeState, 'x' | 'y' | 'w' | 'opacity'>> & NodeState & {appear: number};
  const resolved: Record<string, Resolved> = {};
  for (const id of Object.keys(nodes)) {
    const a = prev?.nodes[id];
    const b = cur.nodes[id];
    if (!a && !b) continue;
    if (b && !a) {
      const ap = pop(cur.at + (si === 0 ? 0 : 0.05));
      resolved[id] = {...b, opacity: (b.opacity ?? 1) * Math.min(1, ap * 1.4), appear: ap};
    } else if (a && !b) {
      resolved[id] = {...a, opacity: (a.opacity ?? 1) * (1 - k), appear: 1};
    } else if (a && b) {
      resolved[id] = {
        ...b, x: lerp(a.x, b.x, k), y: lerp(a.y, b.y, k), w: lerp(a.w, b.w, k),
        h: lerp(a.h ?? a.w * 1.18, b.h ?? b.w * 1.18, k),
        opacity: lerp(a.opacity ?? 1, b.opacity ?? 1, k), appear: 1,
      };
    }
  }
  const hOf = (n: NodeState) => n.h ?? n.w * 1.18;

  // Packet position along its path, following nodes as they move.
  const packetAt = (pk: Packet) => {
    const pts = pk.path.map((id) => resolved[id]).filter(Boolean);
    if (pts.length < 2 || t < pk.start) return null;
    const prog = Math.min(1, (t - pk.start) / (pk.end - pk.start));
    const seg = Math.min(pts.length - 2, Math.floor(prog * (pts.length - 1)));
    const local = prog * (pts.length - 1) - seg;
    const A = pts[seg], B = pts[seg + 1];
    // Stop at the edge of the last card rather than its centre.
    const vertical = Math.abs(B.y - A.y) > Math.abs(B.x - A.x);
    const gap = (vertical ? hOf(B) / 2 : B.w / 2) + (pk.blocked ? 44 : 18);
    const stopShort = seg === pts.length - 2 ? gap / Math.max(1, vertical ? Math.abs(B.y - A.y) : Math.abs(B.x - A.x)) : 0;
    const l = Math.min(local, 1 - stopShort);
    return {x: lerp(A.x, B.x, l), y: lerp(A.y, B.y, l), done: prog >= 1, blocked: pk.blocked};
  };

  const header = [...headers].reverse().find((h) => t >= h.at) ?? headers[0];
  const headerIn = header ? pop(header.at) : 0;
  const phrase = phrases.find((ph, i) => t >= ph.start - 0.12 && t < (phrases[i + 1]?.start ?? Infinity) - 0.12) ?? null;
  const progress = Math.min(1, t / durationSec);

  return (
    <AbsoluteFill style={{backgroundColor: brand.canvas, fontFamily: FONT}}>
      <style>{fontFace}</style>
      {audio ? <Audio src={staticFile(audio)} /> : null}
      <AbsoluteFill style={{backgroundImage: `radial-gradient(${brand.stroke} 2.4px, transparent 2.4px)`,
        backgroundSize: '44px 44px'}} />

      {/* Top band and progress: decorative only, no text (YouTube's controls sit over it) */}
      <div style={{position: 'absolute', top: 0, left: 0, right: 0, height: 120, backgroundColor: brand.textPrimary}} />

      {/* Series label, below YouTube's top controls and above the header. The brand
          name is left out: YouTube shows the channel name under the video anyway. */}
      <div style={{position: 'absolute', top: 262, left: SAFE.left, width: W, fontSize: 26, fontWeight: 700,
        letterSpacing: 4, color: brand.textMuted, lineHeight: 1}}>{eyebrow.toUpperCase()}</div>
      <div style={{position: 'absolute', top: 120, left: 0, height: 10, width: `${progress * 100}%`, backgroundColor: brand.accentA}} />

      {/* Header: changes with the story, max two lines */}
      {header ? (
        <div key={header.at} style={{position: 'absolute', top: 312, left: SAFE.left, width: W,
          opacity: Math.min(1, headerIn * 1.4), transform: `translateY(${(1 - headerIn) * 24}px)`}}>
          <div style={{fontSize: 62, fontWeight: 900, lineHeight: 1.06, color: brand.textPrimary, letterSpacing: -1}}>{header.title}</div>
          {header.accent && t >= (header.accentAt ?? header.at) ? (
            <div style={{fontSize: 62, fontWeight: 900, lineHeight: 1.06, color: brand.accentA, letterSpacing: -1,
              opacity: Math.min(1, pop(header.accentAt ?? header.at) * 1.4),
              transform: `scale(${0.9 + 0.1 * pop(header.accentAt ?? header.at)})`, transformOrigin: 'left center'}}>{header.accent}</div>
          ) : null}
        </div>
      ) : null}

      {/* Edges (packets travel under the cards, so they show only on connectors) */}
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill={brand.textPrimary} />
          </marker>
          <marker id="arrow-b" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill={brand.accentB} />
          </marker>
        </defs>
        {dividers.filter((d) => within(t, d.at, d.until)).map((d, i) => {
          const draw = d.at <= 0 ? 1 : interpolate(t, [d.at, d.at + 0.6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
          return (
            <line key={`div${i}`} x1={d.x} y1={d.y1} x2={d.x} y2={lerp(d.y1, d.y2, draw)} stroke={brand.textMuted}
              strokeWidth={5} strokeDasharray="18 14" strokeLinecap="round" opacity={fadeWin(t, d.at, d.until)} />
          );
        })}
        {(cur.edges ?? []).map(([a, b, st], i) => {
          const A = resolved[a], B = resolved[b];
          const style = (st ?? {}) as EdgeStyle;
          const ec = style.tone ? toneColor(style.tone) : brand.textPrimary;
          const ep = style.glow ? 0.5 + 0.5 * Math.sin(t * 9) : 0;
          if (!A || !B) return null;
          const draw = Math.min(A.appear, B.appear);
          const vertical = Math.abs(B.y - A.y) > Math.abs(B.x - A.x);
          const x1 = vertical ? A.x : A.x + A.w / 2, y1 = vertical ? A.y + hOf(A) / 2 : A.y;
          const x2 = vertical ? B.x : B.x - B.w / 2 - 6, y2 = vertical ? B.y - hOf(B) / 2 - 6 : B.y;
          const sw = style.width ?? (vertical ? 9 : 7);
          return (
            <React.Fragment key={i}>
              {style.glow ? (
                <line x1={x1} y1={y1} x2={lerp(x1, x2, draw)} y2={lerp(y1, y2, draw)} stroke={ec}
                  strokeWidth={sw + 14 + 10 * ep} strokeLinecap="round" opacity={0.25 * Math.min(A.opacity, B.opacity)} />
              ) : null}
              <line x1={x1} y1={y1} x2={lerp(x1, x2, draw)} y2={lerp(y1, y2, draw)}
                stroke={ec} strokeWidth={sw} strokeLinecap="round"
                markerEnd={style.tone === 'b' ? 'url(#arrow-b)' : 'url(#arrow)'}
                opacity={Math.min(A.opacity, B.opacity)} />
            </React.Fragment>
          );
        })}
      </svg>

      {/* Packets */}
      {packets.map((pk, i) => {
        const pos = packetAt(pk);
        if (!pos) return null;
        const hit = pos.done && pk.blocked;
        const shake = hit ? Math.sin(t * 60) * Math.max(0, 1 - (t - pk.end) * 3) * 10 : 0;
        const fade = pos.done && !pk.blocked ? Math.max(0, 1 - (t - pk.end) * 2) : 1;
        const color = hit ? brand.accentB : brand.accentA;
        return (
          <React.Fragment key={i}>
          {hit ? (
            <div style={{position: 'absolute', left: pos.x - 60, top: pos.y + 10, width: 120, height: 8, borderRadius: 4,
              backgroundColor: brand.accentB, transform: `scaleX(${pop(pk.end)})`}} />
          ) : null}
          <div style={{position: 'absolute', left: pos.x - 14 + shake, top: pos.y - 14, width: 28, height: 28,
            borderRadius: 14, backgroundColor: color, boxShadow: `0 0 0 10px ${color}40`, opacity: fade}} />
          </React.Fragment>
        );
      })}

      {/* Nodes */}
      {Object.entries(resolved).map(([id, n]) => {
        const def = nodes[id];
        const tone = n.tone ?? def.tone;
        const color = toneColor(tone);
        const h = hOf(n);
        const glow = n.glow ? 0.5 + 0.5 * Math.sin(t * 9) : 0;
        const sub = n.sub ?? def.sub;
        const frame0 = {position: 'absolute' as const, left: n.x - n.w / 2, top: n.y - h / 2, width: n.w, height: h,
          opacity: n.opacity, transform: `scale(${0.85 + 0.15 * Math.min(1, n.appear)})`,
          backgroundColor: brand.canvas, boxSizing: 'border-box' as const,
          boxShadow: `0 16px 36px rgba(17,26,46,0.12)${glow ? `, 0 0 0 ${8 + 10 * glow}px ${brand.accentB}40` : ''}`};
        if (n.row) {
          const icon = Math.min(64, h * 0.46);
          return (
            <div key={id} style={{...frame0, border: `5px solid ${color}`, borderRadius: 26, display: 'flex',
              alignItems: 'center', gap: 28, padding: '0 34px'}}>
              <div style={{width: icon * 1.5, height: icon * 1.5, flex: 'none', borderRadius: '50%', backgroundColor: brand.surface,
                display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                <Icon svg={icons[def.icon]} size={icon} color={color} />
              </div>
              <div style={{fontSize: 46, fontWeight: 900, color: brand.textPrimary}}>{n.label ?? def.label}</div>
              {sub ? <div style={{marginLeft: 'auto', fontSize: 32, fontWeight: 800, color, textAlign: 'right',
                fontFamily: def.mono ? MONO : FONT}}>{sub}</div> : null}
            </div>
          );
        }
        const iconSize = n.w * 0.34;
        return (
          <div key={id} style={{...frame0, border: `${Math.max(4, n.w / 55)}px solid ${color}`, borderRadius: n.w * 0.12,
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: n.w * 0.05,
            padding: n.w * 0.06}}>
            <div style={{width: iconSize * 1.45, height: iconSize * 1.45, borderRadius: '50%', backgroundColor: brand.surface,
              display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
              <Icon svg={icons[def.icon]} size={iconSize} color={color} />
            </div>
            <div style={{fontSize: n.w * 0.175, fontWeight: 900, color: brand.textPrimary, lineHeight: 1.05, textAlign: 'center'}}>
              {n.label ?? def.label}
            </div>
            {sub ? (
              <div style={{fontSize: Math.max(28, n.w * 0.11), fontWeight: 700, color, lineHeight: 1.15, textAlign: 'center',
                fontFamily: def.mono ? MONO : FONT}}>{sub}</div>
            ) : null}
          </div>
        );
      })}

      {/* Chips (e.g. a score above a node) */}
      {chips.filter((c) => within(t, c.at, c.until)).map((c, i) => {
        const n = resolved[c.node];
        if (!n) return null;
        const a = pop(c.at);
        const B = c.between ? resolved[c.between[1]] : null;
        const A0 = c.between ? resolved[c.between[0]] : null;
        const cx = A0 && B ? (A0.x + A0.w / 2 + B.x - B.w / 2) / 2 : n.x;
        const bad = c.toneAt !== undefined && t >= c.toneAt;
        return (
          <div key={i} style={{position: 'absolute', left: cx + (c.dx ?? 0) - 90, top: n.y - hOf(n) / 2 + (c.dy ?? -86),
            width: 180, textAlign: 'center', opacity: Math.min(fadeWin(t, c.at, c.until), a * 1.4),
            transform: `scale(${0.7 + 0.3 * a})`}}>
            <span style={{fontSize: 40, fontWeight: 900, color: '#FFFFFF', backgroundColor: bad ? brand.accentB : brand.accentA,
              padding: '8px 22px', borderRadius: 40}}>{c.text}</span>
          </div>
        );
      })}

      {/* Badges on a node's corner */}
      {badges.filter((b) => within(t, b.at, b.until)).map((b, i) => {
        const n = resolved[b.node];
        if (!n) return null;
        const a = pop(b.at);
        const size = 76;
        return (
          <div key={i} style={{position: 'absolute', left: n.x + n.w / 2 - size * 0.95, top: n.y - hOf(n) / 2 - size * 0.4,
            width: size, height: size, borderRadius: size / 2, backgroundColor: brand.canvas,
            border: `5px solid ${toneColor(b.tone ?? 'b')}`, display: 'flex', alignItems: 'center', justifyContent: 'center',
            opacity: fadeWin(t, b.at, b.until), transform: `scale(${a})`}}>
            <Icon svg={icons[b.icon]} size={size * 0.6} color={toneColor(b.tone ?? 'b')} stroke={2.6} />
          </div>
        );
      })}

      {/* Meter with an optional threshold tick */}
      {meters.filter((m) => within(t, m.at, m.until)).map((m, i) => {
        const fill = m.at <= 0 ? m.value : interpolate(t, [m.at + 0.15, m.at + 1.2], [0, m.value], {
          extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
        const trackW = W - 20;
        return (
          <div key={i} style={{position: 'absolute', top: m.y, left: SAFE.left + 10, width: trackW, opacity: fadeWin(t, m.at, m.until)}}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 14}}>
              <span style={{fontSize: 40, fontWeight: 800, color: brand.textPrimary}}>{m.label}</span>
              <span />
            </div>
            <div style={{position: 'relative', height: 56, borderRadius: 28, backgroundColor: brand.surface, border: `3px solid ${brand.stroke}`}}>
              <div style={{width: `${fill * 100}%`, height: '100%', backgroundColor: brand.accentA, borderRadius: 28}} />
              <span style={{position: 'absolute', top: -118, left: `${fill * 100}%`, transform: 'translateX(-50%)', fontSize: 96, fontWeight: 900, color: brand.accentA, lineHeight: 1}}>{fill.toFixed(2)}</span>
              {m.threshold !== undefined ? (
                <div style={{position: 'absolute', left: `${m.threshold * 100}%`, top: -18, height: 92, borderLeft: `5px dashed ${brand.textPrimary}`}}>
                  <span style={{position: 'absolute', top: 96, left: -70, width: 140, textAlign: 'center', fontSize: 26,
                    fontWeight: 700, color: brand.textPrimary}}>{m.threshold.toFixed(2)} limit</span>
                </div>
              ) : null}
            </div>
            <div style={{marginTop: 64, fontSize: 40, fontWeight: 700, color: brand.textMuted, textAlign: 'center'}}>{m.caption}</div>
          </div>
        );
      })}

      {/* Notes (e.g. a policy rule in mono) */}
      {notes.filter((n) => within(t, n.at, n.until)).map((n, i) => {
        const a = pop(n.at);
        return (
          <div key={i} style={{position: 'absolute', top: n.y, left: SAFE.left, width: W, display: 'flex', justifyContent: 'center',
            opacity: Math.min(fadeWin(t, n.at, n.until), a * 1.4), transform: `translateY(${(1 - a) * 20}px)`}}>
            <span style={{fontFamily: n.mono ? MONO : FONT, fontSize: 38, fontWeight: 700, color: brand.textPrimary,
              backgroundColor: brand.surface, border: `3px solid ${n.flipAt === undefined || t >= n.flipAt ? brand.accentB : brand.textMuted}`, borderRadius: 16, padding: '14px 26px'}}>{n.text}</span>
          </div>
        );
      })}

      {/* Captions: one line per chunk, upcoming words faint, active word in a pill */}
      {phrase ? (
        <div style={{position: 'absolute', top: 1330, left: SAFE.left, width: W, height: 120,
          display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 18, whiteSpace: 'nowrap'}}>
          {phrase.words.map((w, i) => {
            const active = t >= w.start - 0.03 && t < w.end + 0.08;
            const shown = t >= w.start - 0.03;
            const key = isKey(w.text);
            return (
              <span key={i} style={{fontSize: 72, fontWeight: 900, letterSpacing: -0.5, padding: '2px 14px', borderRadius: 14,
                color: active ? '#FFFFFF' : key ? brand.accentB : brand.textPrimary,
                backgroundColor: active ? (key ? brand.accentB : brand.accentA) : 'transparent',
                opacity: shown ? 1 : 0.35}}>{w.text}</span>
            );
          })}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
