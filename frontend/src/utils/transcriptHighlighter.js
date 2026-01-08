export const findCurrentSegment = (segments, currentTime) => {
  if (!segments || segments.length === 0) return -1;
  
  return segments.findIndex(seg => 
    currentTime >= seg.start_time && currentTime < seg.end_time
  );
};

export const findCurrentWord = (segment, currentTime) => {
  if (!segment || !segment.words || segment.words.length === 0) return -1;
  
  return segment.words.findIndex(word =>
    currentTime >= word.start && currentTime < word.end
  );
};

export const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

export const formatDuration = (seconds) => {
  const hours = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  
  if (hours > 0) {
    return `${hours}h ${mins}m`;
  } else if (mins > 0) {
    return `${mins}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
};
