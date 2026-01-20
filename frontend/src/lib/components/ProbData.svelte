<script>

  import { ensProbs } from "$lib/utils";
  import { setContext } from "svelte";

  let { data, children } = $props()

  let thresh = $state()
  let comparator = $state("gt")

  let prob = $derived(
    typeof thresh !== "undefined"
      ? ensProbs(data.data, thresh, comparator).map((d, i) => ({dttm: data.dttm[i], prob: d}))
      : undefined
  )

  setContext("probs", {
    getThresh() { return thresh },
    getProbs() { return prob },
    getComparator() { return comparator },

    updateThresh(value) { thresh = value },
    updateComparator(value) { comparator = value }
  })

  let i = $state(-1)

  setContext("probHover", {
    getIndex() { return i }, 
    setIndex(idx) { i = idx }
  })
  
  </script>

  {@render children?.()}
