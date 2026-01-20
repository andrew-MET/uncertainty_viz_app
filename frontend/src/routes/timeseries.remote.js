import { query } from "$app/server"
import { env } from "$env/dynamic/private"
import { decum } from "$lib/utils";

const objectToQueryString = async queryParameters => {
  const result = queryParameters
    ? Object.entries(queryParameters).reduce(
        (queryString, [key, val], index) => {
          const symbol = queryString.length === 0 ? '?' : '&';
          queryString += key === "accum" ? '' :`${symbol}${key}=${val.toString()}`;
          return queryString;
        },
        ''
      )
    : '';
  return(result)
};

export const getTimeseries = query("unchecked", async (data) => {
  const url = await `${env.FASTAPI_BASE}/api/timeseries${await objectToQueryString(data)}`
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    const result = await response.json();
    const mbrNames = Object.keys(result.data)

    if (data.param === "press") {
      mbrNames.forEach((e) => result.data[e] = result.data[e].map(d => d / 100))
    }

    if (data.param === "temp") {
      mbrNames.forEach((e) => result.data[e] = result.data[e].map(d => d - 273.15))
    }

    if (data.accum) {
      mbrNames.forEach((e) => result.data[e] = decum(result.data[e], data.accum))
    }

    return result
  } catch (error) {
    console.error(error.message);
    return null
  }
})