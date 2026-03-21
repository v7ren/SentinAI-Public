// used for merging notification prefs and user settings — keeps nested objects intact
function mergeDeep(target, source) {
  for (const key of Object.keys(source)) {
    if (typeof source[key] === 'object' && source[key] !== null) {
      if (!target[key]) target[key] = {};
      mergeDeep(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

function mergeObjects(target, ...sources) {
  let result = { ...target };
  for (const src of sources) {
    if (src && typeof src === 'object') result = mergeDeep(result, src);
  }
  return result;
}

module.exports = { mergeDeep, mergeObjects };
