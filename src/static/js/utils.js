export function isNil(value) {
    // null and undefined
    return value == null;
}

export function isNull(value) {
    // null only
    return value === null;
}

export function isObject(value) {
    if (isNil(value)) {
        return false;
    }

    return typeof value === 'object';
}

export function isArray(value) {
    return Array.isArray(value);
}

export function isFunction(value) {
    return typeof value === 'function';
}

export function isString(value) {
    return typeof value === 'string' || value instanceof String;
}

export function isEmpty(value) {
    if (isNil(value)) {
        return true;
    }

    if (isArray(value) || isString(value)) {
        return value.length === 0;
    }

    if (isObject(value)) {
        return Object.keys(value).length === 0;
    }

    return false;
}

export function criteriaOps2Int(op) {
    let ops = 0;
    switch(op) {
        case "!=":
        case "!==":
        case "<>":
            ops = 1;
            break;
        case "<":
            ops = 2;
            break;
        case "<=":
            ops = 3;
            break;
        case ">":
            ops = 4;
            break;
        case ">=":
            ops = 5;
            break;
        // TODO: finish this  ie: contains, between, begins ...
        default:    // ==
            ops = 0;
    }

    return ops;
}

/**
export function get(obj, path, defaultValue=null) {
    // get data from multilevel object where path is in dot notation or array format
    // ie: path = user.Settings.Locale
    // ie: path = CountryStates.Country[0]

    const keys = path.split(/\.|\[(\d+)\]/).filter(Boolean);
    return keys.reduce((prev, key) => {
        if (!isEmpty(key)) {
            if (isObject(prev) && !isNil(prev) && !isArray(prev)) {
                if(key in prev) return prev[key];
                return defaultValue;
            } else if (isArray(prev)) {
                const index = parseInt(key, 10);
                if (!isNaN(index)) {
                    if(index < prev.length) return prev[index];
                    return defaultValue;
                }
            } else if(prev) {
                return prev;
            }
        }
        return defaultValue;
    }, obj);
}
**/
export function get(obj, path, defaultValue=null) {
    /**
    get data from multilevel object where path is in dot notation or array format
    ie: name, name[0], name[*], name[], dot.notated[0], dot.notated[*],
        dot[0].notated, dot[*].notated
    **/
    // Convert brackets to dot form: warehouse[1] -> warehouse.1
    // warehouse[*] -> warehouse.*
    const tokens = path
        .replace(/\[\]/g, '[*]')
        .replace(/\[(\*|\d+)\]/g, '.$1')
        .split('.')
        .filter(Boolean);

    function walk(value, i) {
        if (value == null) return undefined;
        if (i === tokens.length) return value;

        const key = tokens[i];

        if(key === '*') {
            if (!isArray(value)) return undefined;
            return value.map(v => walk(v, i + 1));
        }

        return walk(value[key], i + 1);
    }

    const result = walk(obj, 0);
    return result === undefined ? defaultValue : result;
}

export function set(obj, path, value) {
    /**
        set nested structure
        ie: name, name[0], name[*], name[], dot.notated[0], dot.notated[*],
            dot[0].notated, dot[*].notated
        creates missing objects/arrays automatically
    **/
    const tokens = path
        .replace(/\[\]/g, '[*]')
        .replace(/\[(\*|\d+)\]/g, '.$1')
        .split('.')
        .filter(Boolean);

    function walk(cur, i) {
        const key = tokens[i];

        // Last token → assign
        if(i === tokens.length - 1) {
            if(key === '*') {
                if(!Array.isArray(cur)) return;
                cur.forEach((_, idx) => cur[idx] = value);
            } else {
                cur[key] = value;
            }
            return;
        }

        // Wildcard → recurse into all
        if(key === '*') {
            if(!Array.isArray(cur)) return;
            cur.forEach(v => walk(v, i + 1));
            return;
        }

        // Create missing structure
        if(isNil(cur[key])) {
            const next = tokens[i + 1];
            cur[key] = next === '*' || /^\d+$/.test(next) ? [] : {};
        }

        walk(cur[key], i + 1);
    }

    walk(obj, 0);
    return obj;
}

/**
export function set(obj, path, value) {
    // set data from multilevel object where path is in dot notation or array format
    // ie: obj = row; path = user.Settings.Locale
    // ie: path = CountryStates.Country[0]

    const keys = path.split(/\.|\[(\d+)\]/).filter(Boolean);
    keys.reduce((prev, key, index) => {
        if (index === keys.length - 1) {
            prev[key] = value;
        } else if (!isNaN(parseInt(keys[index + 1]))) {
            if (!isArray(prev[key])) {
                prev[key] = [];
            }
            if (!prev[key][parseInt(keys[index + 1])]) {
                prev[key][parseInt(keys[index + 1])] = {};
            }
            return prev[key][parseInt(keys[index + 1])];
        } else {
            if (!prev[key]) {
                prev[key] = {};
            }
            return prev[key];
        }
    }, obj);
}
**/
export function dateTimeFormat(locale, type="Date", hour12=true) {
    // tokenMap: Intl part.type = date-fns unicode tokens
    const tokenMap = {
        day: "dd",
        month: "MM",
        year: "yyyy",
        hour: "hh",
        minute: "mm",
        second: "ss",
        dayPeriod: "a"
    };
    let formatter = null;
    if(type === "DateTime") {
        formatter = new Intl.DateTimeFormat(locale, {
            year: 'numeric',  // 4-digit year
            month: '2-digit', // Month with leading zero
            day: '2-digit',   // Day with leading zero
            hour: '2-digit',  // Hour with leading zero
            minute: '2-digit',// Minute with leading zero
            second: '2-digit',// Second with leading zero
            hour12: hour12,
        });
    } else if(type === "Time") {
        formatter = new Intl.DateTimeFormat(locale, {
            hour: '2-digit',  // Hour with leading zero
            minute: '2-digit',// Minute with leading zero
            second: '2-digit',// Second with leading zero
            hour12: hour12,
        });
    } else {
        formatter = new Intl.DateTimeFormat(locale);
    }
    const parts = formatter.formatToParts(new Date());
    return parts
        .map((part) => tokenMap[part.type] || part.value)
        .join("");
}

export function dateTimeFormatTZ(datetime, locale, timezone) {
    const formatter = new Intl.DateTimeFormat(locale, {
            timeZone: timezone,
            year: 'numeric',  // 4-digit year
            month: '2-digit', // Month with leading zero
            day: '2-digit',   // Day with leading zero
            hour: '2-digit',  // Hour with leading zero
            minute: '2-digit',// Minute with leading zero
            second: '2-digit',// Second with leading zero
            hourCycle: "h23", // Ensures 24-hour format
    });
    const parts = formatter.formatToParts(datetime);

    // Extract parts and construct ISO-like string
    const formattedDate = `${parts.find(p => p.type === "year").value}-` +
                          `${parts.find(p => p.type === "month").value}-` +
                          `${parts.find(p => p.type === "day").value}T` +
                          `${parts.find(p => p.type === "hour").value}:` +
                          `${parts.find(p => p.type === "minute").value}:` +
                          `${parts.find(p => p.type === "second").value}`;
    // Add timezone offset (XXX)
    const offsetFormatter = new Intl.DateTimeFormat(locale, {
            timeZoneName: "shortOffset",
            timeZone: timezone,
    });
    const offset = offsetFormatter.formatToParts(datetime).find(p => p.type === "timeZoneName").value;

  return `${formattedDate}${offset}`;
}

export function serializeTemporal(value, type) {

    const pad = v => String(v).padStart(2,'0');

    if (type.toLowerCase() === "date") {
        return `${value.getFullYear()}-${pad(value.getMonth()+1)}-${pad(value.getDate())}`;
    }

    if (type.toLowerCase() === "datetime") {
        return value.toISOString();
    }

    if (type.toLowerCase() === "time") {
        return `${pad(value.getHours())}:${pad(value.getMinutes())}:${pad(value.getSeconds())}`;
    }

    return value;
}

/*
 * Tiny tokenizer
 * https://gist.github.com/borgar/451393/7698c95178898c9466214867b46acb2ab2f56d68
 * - Accepts a subject string and an object of regular expressions for parsing
 * - Returns an array of token objects
 *
 * tokenize('this is text.', { word:/\w+/, whitespace:/\s+/, punctuation:/[^\w\s]/ }, 'invalid');
 * result => [{ token="this", type="word" },{ token=" ", type="whitespace" }, Object { token="is", type="word" }, ... ]
 *
 */
function tokenize ( s, parsers, deftok ) {
  var m, r, t, tokens = [];
  while ( s ) {
    t = null;
    m = s.length;
    for ( var key in parsers ) {
      r = parsers[ key ].exec( s );
      // try to choose the best match if there are several
      // where "best" is the closest to the current starting point
      if ( r && ( r.index < m ) ) {
        t = {
          token: r[ 0 ],
          type: key,
          matches: r.slice( 1 )
        }
        m = r.index;
      }
    }
    if ( m ) {
      // there is text between last token and currently
      // matched token - push that out as default or "unknown"
      tokens.push({
        token : s.substr( 0, m ),
        type  : deftok || 'unknown'
      });
    }
    if ( t ) {
      // push current token onto sequence
      tokens.push( t );
    }
    s = s.substr( m + (t ? t.token.length : 0) );
  }
  return tokens;
}

export function tokenizer(s) {
    // simple tokenizer: word operator object

    // to test regex online: https://regex101.com/r/zQ3pQ7/1
    const parsers = {
        // word:/\w+/,
        word:/[\w.]+/,  // allow for dotNotation words
        whitespace:/\s+/,
        operators:/(<[=>]?|==?|>=?|!==?|&&|\|\|)/,
        punctuation:/[^\w\s]/
    };

    return tokenize(s, parsers, "invalid");
}
