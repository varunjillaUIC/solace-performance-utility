interface IconProps {
  size?: number;
  color?: string;
}

const c = (color?: string) => color || "#5a6675";

export function IconPublish({ size = 15, color }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 15 15" fill="none">
      <path d="M2 4h11M2 7.5h7M2 11h5" stroke={c(color)} strokeWidth="1.4" strokeLinecap="round"/>
      <path d="M11 9l2.5 2.5L11 14" stroke={c(color)} strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

export function IconSubscribe({ size = 15, color }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 15 15" fill="none">
      <path d="M3 7.5C3 5 5 3 7.5 3S12 5 12 7.5" stroke={c(color)} strokeWidth="1.4" strokeLinecap="round"/>
      <path d="M1 7.5C1 3.9 3.9 1 7.5 1S14 3.9 14 7.5" stroke={c(color)} strokeWidth="1.4" strokeLinecap="round"/>
      <circle cx="7.5" cy="7.5" r="1.5" fill={c(color)}/>
      <path d="M7.5 9v3" stroke={c(color)} strokeWidth="1.4" strokeLinecap="round"/>
    </svg>
  );
}

export function IconQueue({ size = 15, color }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 15 15" fill="none">
      <rect x="2" y="5" width="11" height="7" rx="2" stroke={c(color)} strokeWidth="1.4"/>
      <path d="M5 5V4a2.5 2.5 0 015 0v1" stroke={c(color)} strokeWidth="1.4"/>
      <path d="M5 8.5h5M7.5 8.5v2" stroke={c(color)} strokeWidth="1.4" strokeLinecap="round"/>
    </svg>
  );
}

export function IconPerf({ size = 15, color }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 15 15" fill="none">
      <path d="M2 11L5 8l3 3 5-6" stroke={c(color)} strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
      <circle cx="13" cy="2" r="1.5" fill={c(color)} opacity="0.6"/>
    </svg>
  );
}

export function IconProfiles({ size = 15, color }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 15 15" fill="none">
      <circle cx="7.5" cy="5" r="2.5" stroke={c(color)} strokeWidth="1.4"/>
      <path d="M2.5 13c0-2.76 2.24-5 5-5s5 2.24 5 5" stroke={c(color)} strokeWidth="1.4" strokeLinecap="round"/>
    </svg>
  );
}

export function IconDisconnect({ size = 14, color }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 14 14" fill="none">
      <path d="M5 2H2a1 1 0 00-1 1v7a1 1 0 001 1h3M10 10.5l3-3-3-3M6 7h7"
        stroke={c(color)} strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

export function IconSend({ size = 13, color }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 13 13" fill="none">
      <path d="M2 6.5l9-4.5-4.5 9-1.5-4.5L2 6.5z" fill={c(color)}/>
    </svg>
  );
}

export function IconClear({ size = 13, color }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 13 13" fill="none">
      <path d="M2 2l9 9M11 2L2 11" stroke={c(color)} strokeWidth="1.4" strokeLinecap="round"/>
    </svg>
  );
}

export function IconCopy({ size = 13, color }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 13 13" fill="none">
      <rect x="4" y="4" width="8" height="8" rx="1.5" stroke={c(color)} strokeWidth="1.2"/>
      <path d="M1 9V2a1 1 0 011-1h7" stroke={c(color)} strokeWidth="1.2" strokeLinecap="round"/>
    </svg>
  );
}

export function IconStop({ size = 13, color }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 13 13" fill="none">
      <rect x="2.5" y="2.5" width="8" height="8" rx="1.5" fill={c(color)}/>
    </svg>
  );
}

export function IconExport({ size = 13, color }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 13 13" fill="none">
      <path d="M6.5 1v7M4 6l2.5 2.5L9 6" stroke={c(color)} strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M2 10v1a1 1 0 001 1h7a1 1 0 001-1v-1" stroke={c(color)} strokeWidth="1.3" strokeLinecap="round"/>
    </svg>
  );
}

export function IconReplay({ size = 13, color }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 13 13" fill="none">
      <path d="M2 6.5A4.5 4.5 0 1111 4.5" stroke={c(color)} strokeWidth="1.3" strokeLinecap="round"/>
      <path d="M9 2l2 2.5L8.5 6" stroke={c(color)} strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}