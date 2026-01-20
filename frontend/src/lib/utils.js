import { transpose, quantile, scaleLinear, scaleLog, scaleTime, scaleUtc, extent, bin, sort} from "d3";

function responseJson(response) {
  if (!response.ok) throw new Error(response.status + " " + response.statusText);
  if (response.status === 204 || response.status === 205) return;
  return response.json();
}

export function json(input, init) {
  return fetch(input, init).then(responseJson);
}

function objectFromArray(values, keys) {
  const o = new Object()
  for (let i = 0; i < keys.length; i++) {
    o[keys[i]] = values[i]
  }
  return o
}

export function decum(data, period) {
  const result = []
  for (let i = 0; i < data.length; i++) {
    result.push(i < period ? 0.0 : data[i] - data[i - period])
    if (result[i] < 0) {
      result[i] = 0.0
    }
  }
  return result
}

export function decumAll(data, periods) {
  if (data.precip || data.Precip) {
    const precipName = data.precip ? "precip" : "Precip"
    const totalPrecip = Object.values(data[precipName].data)
    const members = Object.keys(data[precipName].data)
    for (let accum of periods) {
      const decumPrecip = totalPrecip.map(d => decum(d, accum))
      const o = new Object()
      for (let i = 0; i < members.length; i++) {
        o[members[i]] = decumPrecip[i]
      }
      data[precipName + "_" + accum + "h"] = {data: o, dttm: data[precipName].dttm}
    }
  }
  return(data)
}


export function quantiles(data, quant) {
  if (!data) return
  if (!quant) {
    quant = Array(11)
      .fill(0)
      .map((el, idx) => idx / 10)
  }
  
  let result = transpose(Object.values(data.data))
    .map(d => quant.map(q => quantile(d, q)))

  for (let i = 0; i < result.length; i++) {
    result[i] = {dttm: data.dttm[i], ...objectFromArray(result[i], quant)}
  }

  return(result)
}

export function spaghetti(data) {
  if (!data) return
  let result = transpose(Object.values(data.data))
  for (let i = 0; i < result.length; i++) {
    result[i] = {dttm: data.dttm[i], ...objectFromArray(result[i], Object.keys(data.data))}
  }
  return result
}



export function objectToArray(obj) {
  // Get the keys of the object
  const keys = Object.keys(obj);

  // Get the length of the arrays (assuming all arrays are of the same length)
  const length = obj[keys[0]].length;

  // Initialize the result array
  const result = [];

  // Iterate over the length of the arrays
  for (let i = 0; i < length; i++) {
    // Initialize a new object for each index
    const newObj = {};

    // Populate the new object with values from each array at the current index
    keys.forEach((key) => {
      newObj[key] = obj[key][i];
    });

    // Add the new object to the result array
    result.push(newObj);
  }

  return result;
}

export function getScaleFunc(scaleType) {
  switch(scaleType) {
    case "log":
      return scaleLog
      break
    case "time":
      return scaleTime
      break
    case "utc":
      return scaleUtc
      break
    default:
      return scaleLinear
      break
  }
}

export function longData(data) {
  if (!data) return
  return Object.keys(data.data).map(k => data.dttm.map((d, i) => ({dttm: d, member: k, fcst: data.data[k][i]}))).flat()
}

export function ensProbs(data, thresh, comparator = "ge") {
  if (!data) return
  const probs = transpose(Object.values(data))
  if (comparator === "ge") {
    return probs.map(d => d.map(d => d >= thresh).reduce((a, b) => a + b, 0) / d.length)
  }
  if (comparator === "gt") {
    return probs.map(d => d.map(d => d > thresh).reduce((a, b) => a + b, 0) / d.length)
  }
  if (comparator === "le") {
    return probs.map(d => d.map(d => d <= thresh).reduce((a, b) => a + b, 0) / d.length)
  }
  if (comparator === "lt") {
    return probs.map(d => d.map(d => d < thresh).reduce((a, b) => a + b, 0) / d.length)
  }
  if (comparator === "eq") {
    return probs.map(d => d.map(d => d === thresh).reduce((a, b) => a + b, 0) / d.length)
  }
  if (comparator === "between") {
    return probs.map(d => d.map(d => d >= thresh[0] && d <= thresh[1]).reduce((a, b) => a + b, 0) / d.length)
  }
}

function sortMemberBins(data, binWidth) {
  return sort(data, d => d.fcst)
    .map((d, i) => {
      const x = i === 0 ? data.x1 - binWidth / 2 : data.x0 + binWidth / 2
      const y = binWidth / 2 + i * binWidth
      return {...d, x: x, y: y, radius: binWidth / 2, count: i}
    })
    .filter(d => d.count < 11)
}

export function binMembers(data, numBins) {
  if (!data) return
  if (!data.data) return
  const domain = extent(Object.values(data.data).flat())
  const thresholds = scaleLinear().domain(domain).nice().ticks(numBins)
  const binWidth = [...new Set(thresholds.slice(1).map((d, i) => d - thresholds[i]))][0]
  const bins = bin().domain(domain).thresholds(thresholds)
  const binnedData = objectToArray(data.data)
    .map(d => 
      bins.value(d => d.fcst)(Object.keys(d).map((key, i) => ({member: key, fcst: d[key]})))
        .map(d => sortMemberBins(d, binWidth))
        .flat()
  
    )
  return binnedData
}